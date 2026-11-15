"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { personas } from "@/lib/api";
import type { Persona } from "@/lib/types";
import ChatPanel from "@/components/ChatPanel";
import MemoriesPanel from "@/components/MemoriesPanel";
import VideosPanel from "@/components/VideosPanel";
import ConversationsPanel from "@/components/ConversationsPanel";

const TABS = ["Chat", "Memories", "Videos", "History"] as const;
type Tab = (typeof TABS)[number];

export default function PersonaPage() {
  const { id } = useParams<{ id: string }>();
  const [persona, setPersona] = useState<Persona | null>(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<Tab>("Chat");

  useEffect(() => {
    personas.get(id).then(setPersona).catch((e) => setError(e.message));
  }, [id]);

  if (error) return <p className="error">{error}</p>;
  if (!persona) return <p className="text-ink/60">Loading…</p>;

  return (
    <div>
      <Link href="/personas" className="text-sm text-dusk underline">All personas</Link>
      <h1 className="mt-2 text-4xl">{persona.name}</h1>
      {persona.relationship && <p className="text-ink/60">{persona.relationship}</p>}

      <div role="tablist" className="mt-8 flex gap-6 border-b border-mist">
        {TABS.map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => setTab(t)}
            className={`-mb-px border-b-2 pb-2 text-sm ${tab === t ? "border-dusk text-ink" : "border-transparent text-ink/60 hover:text-ink"}`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="mt-8">
        {tab === "Chat" && <ChatPanel personaId={id} personaName={persona.name} />}
        {tab === "Memories" && <MemoriesPanel personaId={id} />}
        {tab === "Videos" && <VideosPanel personaId={id} />}
        {tab === "History" && <ConversationsPanel personaId={id} />}
      </div>
    </div>
  );
}
