"use client";

import { useEffect, useState } from "react";
import { conversations } from "@/lib/api";
import type { Conversation } from "@/lib/types";

export default function ConversationsPanel({ personaId }: { personaId: string }) {
  const [items, setItems] = useState<Conversation[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    conversations.list(personaId).then(setItems).catch((e) => setError(e.message));
  }, [personaId]);

  if (error) return <p className="error">{error}</p>;
  if (items === null) return <p className="text-ink/60">Loading…</p>;
  if (items.length === 0) return <p className="text-ink/60">No conversations yet.</p>;

  return (
    <ul className="max-w-2xl divide-y divide-mist border-y border-mist">
      {items.map((c) => (
        <li key={c.id} className="py-3">
          <p>Conversation {c.id}</p>
          {c.created_at && <p className="text-xs text-ink/60">{new Date(c.created_at).toLocaleString()}</p>}
        </li>
      ))}
    </ul>
  );
}
