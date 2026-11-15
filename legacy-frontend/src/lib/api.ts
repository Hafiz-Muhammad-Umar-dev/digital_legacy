import type {
  ChatRequest, ChatResponse, Conversation, Job, MediaAsset, Memory, Persona,
  PersonaCreate, RegisterPayload, TokenResponse, TTSRequest, TTSResponse, User,
} from "./types";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
const PREFIX = "/api/v1";

const ACCESS_KEY = "dl_access";
const REFRESH_KEY = "dl_refresh";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

/* ---------- token storage ---------- */
export const tokens = {
  get access() { return typeof window === "undefined" ? null : localStorage.getItem(ACCESS_KEY); },
  get refresh() { return typeof window === "undefined" ? null : localStorage.getItem(REFRESH_KEY); },
  set(t: { access_token: string; refresh_token?: string }) {
    localStorage.setItem(ACCESS_KEY, t.access_token);
    if (t.refresh_token) localStorage.setItem(REFRESH_KEY, t.refresh_token);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

/* ---------- helpers ---------- */
async function parseError(res: Response): Promise<ApiError> {
  let msg = `Request failed (${res.status})`;
  try {
    const data = await res.json();
    if (typeof data.detail === "string") msg = data.detail;
    else if (Array.isArray(data.detail)) msg = data.detail.map((d: { msg: string }) => d.msg).join(", ");
  } catch { /* ignore */ }
  return new ApiError(res.status, msg);
}

let refreshing: Promise<boolean> | null = null;

async function tryRefresh(): Promise<boolean> {
  if (refreshing) return refreshing;
  refreshing = (async () => {
    const refresh_token = tokens.refresh;
    if (!refresh_token) return false;
    try {
      const res = await fetch(`${API_URL}${PREFIX}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token }),
      });
      if (!res.ok) return false;
      tokens.set(await res.json());
      return true;
    } catch { return false; }
    finally { setTimeout(() => { refreshing = null; }, 0); }
  })();
  return refreshing;
}

async function request(path: string, init: RequestInit = {}, auth = true): Promise<Response> {
  const build = () => {
    const headers = new Headers(init.headers);
    if (auth && tokens.access) headers.set("Authorization", `Bearer ${tokens.access}`);
    return fetch(`${API_URL}${PREFIX}${path}`, { ...init, headers });
  };
  let res = await build();
  if (res.status === 401 && auth && (await tryRefresh())) res = await build();
  if (!res.ok) {
    if (res.status === 401 && auth) {
      tokens.clear();
      if (typeof window !== "undefined") window.location.href = "/login";
    }
    throw await parseError(res);
  }
  return res;
}

async function json<T>(path: string, init: RequestInit = {}, auth = true): Promise<T> {
  const res = await request(path, init, auth);
  if (res.status === 204) return undefined as T;
  return res.json();
}

const body = (data: unknown): RequestInit => ({
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});

/* ---------- Auth ---------- */
export const auth = {
  register: (p: RegisterPayload) => json<User>("/auth/register", { method: "POST", ...body(p) }, false),
  // OAuth2 password flow: form-encoded, field is "username" (put the email in it)
  login: (email: string, password: string) =>
    json<TokenResponse>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: email, password }),
    }, false),
  logout: () => json<void>("/auth/logout", { method: "POST", ...body({ refresh_token: tokens.refresh }) }),
  me: () => json<User>("/auth/me"),
};

/* ---------- Personas ---------- */
export const personas = {
  list: () => json<Persona[]>("/personas"),
  create: (p: PersonaCreate) => json<Persona>("/personas", { method: "POST", ...body(p) }),
  get: (id: string | number) => json<Persona>(`/personas/${id}`),
};

/* ---------- Memories ---------- */
export const memories = {
  list: (personaId: string | number) => json<Memory[]>(`/personas/${personaId}/memories`),
  create: (personaId: string | number, content: string) =>
    json<Memory>(`/personas/${personaId}/memories`, { method: "POST", ...body({ content }) }),
  edit: (id: string | number, content: string) =>
    json<Memory>(`/memories/${id}`, { method: "PATCH", ...body({ content }) }),
  approve: (id: string | number) => json<Memory>(`/memories/${id}/approve`, { method: "POST" }),
  reject: (id: string | number) => json<Memory>(`/memories/${id}/reject`, { method: "POST" }),
};

/* ---------- Videos ---------- */
export const videos = {
  list: (personaId: string | number) => json<MediaAsset[]>(`/personas/${personaId}/videos`),
  upload: (personaId: string | number, file: File) => {
    const fd = new FormData();
    fd.append("file", file); // field name: "file" — schema check kar lein
    return json<MediaAsset>(`/personas/${personaId}/video`, { method: "POST", body: fd });
  },
  process: (videoId: string | number) => json<Job>(`/videos/${videoId}/process`, { method: "POST" }),
  job: (videoId: string | number) => json<Job>(`/videos/${videoId}/job`),
};

/* ---------- Conversations & Chat ---------- */
export const conversations = {
  list: (personaId: string | number) => json<Conversation[]>(`/personas/${personaId}/conversations`),
};

export const chat = {
  send: (p: ChatRequest) => json<ChatResponse>("/chat", { method: "POST", ...body(p) }),
  // VoiceChatRequest ka exact shape Swagger me dekh kar adjust karein
  voice: (p: Record<string, unknown>) => json<ChatResponse>("/chat/voice", { method: "POST", ...body(p) }),
};

export function replyText(r: ChatResponse): string {
  const keys = ["reply", "response", "message", "answer", "text", "content", "assistant_message", "output"];
  for (const k of keys) {
    const v = (r as Record<string, unknown>)[k];
    if (typeof v === "string" && v.trim()) return v;
  }
  // fallback: pehli lambi string jo id jaisi na ho
  for (const [k, v] of Object.entries(r)) {
    if (typeof v === "string" && v.length > 1 && !k.endsWith("id")) return v;
  }
  return "";
}

/* ---------- TTS ---------- */
export const tts = {
  // Audio bytes ya JSON (audio_url/filename), dono handle karta hai. Blob URL return karta hai.
  async speak(p: TTSRequest): Promise<string> {
    const res = await request("/tts/speak", { method: "POST", ...body(p) });
    const type = res.headers.get("content-type") ?? "";
    if (type.includes("application/json")) {
      const data = (await res.json()) as TTSResponse;
      const ref = data.audio_url ?? data.url ?? data.filename;
      if (!ref) throw new Error("TTS response did not include an audio reference");
      return tts.audioBlobUrl(ref);
    }
    return URL.createObjectURL(await res.blob());
  },
  // Audio fetch with auth header, returns a blob URL ready for <audio src>
  async audioBlobUrl(filenameOrUrl: string): Promise<string> {
    const name = filenameOrUrl.split("/").pop()!;
    const res = await request(`/tts/audio/${encodeURIComponent(name)}`);
    return URL.createObjectURL(await res.blob());
  },
};

/* ---------- System ---------- */
export const system = {
  health: () => json<{ status: string }>("/health", {}, false),
};
