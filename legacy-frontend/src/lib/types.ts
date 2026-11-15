// Types mirror the OpenAPI schemas. Swagger me schemas collapsed thi,
// isliye fields assumed hain — apne backend ke hisab se adjust kar lein.

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type?: string;
}

export interface User {
  id: number | string;
  email: string;
  full_name?: string | null;
  [key: string]: unknown;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
}

export interface Persona {
  id: number | string;
  name: string;
  relationship?: string | null;
  description?: string | null;
  created_at?: string;
  [key: string]: unknown;
}

export interface PersonaCreate {
  name: string;
  relationship?: string;
  description?: string;
}

export type MemoryStatus = "pending" | "approved" | "rejected" | string;

export interface Memory {
  id: number | string;
  persona_id?: number | string;
  content: string;
  status?: MemoryStatus;
  created_at?: string;
  [key: string]: unknown;
}

export interface MediaAsset {
  id: number | string;
  filename?: string;
  url?: string;
  status?: string;
  created_at?: string;
  [key: string]: unknown;
}

export interface Job {
  id: number | string;
  status: string;
  progress?: number;
  error?: string | null;
  [key: string]: unknown;
}

export interface Conversation {
  id: number | string;
  persona_id?: number | string;
  created_at?: string;
  [key: string]: unknown;
}

export interface ChatRequest {
  persona_id: number | string;
  message: string;
  conversation_id?: number | string | null;
}

export interface ChatResponse {
  reply?: string;
  response?: string;
  message?: string;
  conversation_id?: number | string;
  [key: string]: unknown;
}

export interface TTSRequest {
  text: string;
  persona_id?: number | string;
}

export interface TTSResponse {
  audio_url?: string;
  url?: string;
  filename?: string;
  [key: string]: unknown;
}
