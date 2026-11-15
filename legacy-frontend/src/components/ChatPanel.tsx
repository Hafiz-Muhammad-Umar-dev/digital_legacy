"use client";

import { useEffect, useRef, useState } from "react";
import { chat, replyText, tts } from "@/lib/api";

interface Msg { role: "user" | "persona"; text: string; }

export default function ChatPanel({ personaId, personaName }: { personaId: string; personaName: string }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [audioSrc, setAudioSrc] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);
  useEffect(() => { if (audioSrc) audioRef.current?.play().catch(() => {}); }, [audioSrc]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    setInput(""); setError(""); setBusy(true);
    setMessages((m) => [...m, { role: "user", text }]);
    try {
      const res = await chat.send({ persona_id: personaId, message: text, conversation_id: conversationId });
      if (res.conversation_id) setConversationId(res.conversation_id);
      setMessages((m) => [...m, { role: "persona", text: replyText(res) }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Message failed");
    } finally { setBusy(false); }
  }

  async function speak(text: string) {
    if (!text.trim()) { setError("No text to read aloud"); return; }
    setError("");
    try {
      const blobUrl = await tts.speak({ text, persona_id: personaId });
      setAudioSrc(blobUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not generate audio");
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <div className="min-h-[320px] space-y-4">
        {messages.length === 0 && (
          <p className="text-ink/60">Say something to {personaName}. Only approved memories shape the replies.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : ""}>
            <p className={`inline-block max-w-[85%] rounded-lg px-4 py-2 text-left ${m.role === "user" ? "bg-dusk text-white" : "bg-white border border-mist"}`}>
              {m.text}
            </p>
            {m.role === "persona" && (
              <div><button className="mt-1 text-xs text-dusk underline" onClick={() => speak(m.text)}>Play voice</button></div>
            )}
          </div>
        ))}
        <div ref={endRef} />
      </div>

      {audioSrc && <audio ref={audioRef} src={audioSrc} controls className="mt-4 w-full" />}
      {error && <p className="error mt-4" role="alert">{error}</p>}

      <form onSubmit={send} className="mt-6 flex gap-2">
        <input className="input" placeholder={`Message ${personaName}`} value={input} onChange={(e) => setInput(e.target.value)} />
        <button className="btn" disabled={busy}>{busy ? "Sending…" : "Send"}</button>
      </form>
    </div>
  );
}
