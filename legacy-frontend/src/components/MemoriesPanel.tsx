"use client";

import { useEffect, useState } from "react";
import { memories } from "@/lib/api";
import type { Memory } from "@/lib/types";

export default function MemoriesPanel({ personaId }: { personaId: string }) {
  const [items, setItems] = useState<Memory[] | null>(null);
  const [error, setError] = useState("");
  const [content, setContent] = useState("");
  const [editingId, setEditingId] = useState<string | number | null>(null);
  const [editText, setEditText] = useState("");

  const load = () => memories.list(personaId).then(setItems).catch((e) => setError(e.message));
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [personaId]);

  async function act(fn: () => Promise<unknown>) {
    setError("");
    try { await fn(); await load(); } catch (e) { setError(e instanceof Error ? e.message : "Action failed"); }
  }

  return (
    <div className="max-w-2xl">
      <form
        className="space-y-2"
        onSubmit={(e) => { e.preventDefault(); if (!content.trim()) return; act(async () => { await memories.create(personaId, content.trim()); setContent(""); }); }}
      >
        <label className="label" htmlFor="mem">Add a memory</label>
        <textarea id="mem" rows={3} className="input" value={content} onChange={(e) => setContent(e.target.value)} />
        <button className="btn">Save memory</button>
      </form>

      {error && <p className="error mt-4">{error}</p>}

      <ul className="mt-8 divide-y divide-mist border-y border-mist">
        {items === null && <li className="py-4 text-ink/60">Loading…</li>}
        {items?.length === 0 && <li className="py-4 text-ink/60">No memories yet.</li>}
        {items?.map((m) => (
          <li key={m.id} className="py-4">
            {editingId === m.id ? (
              <div className="space-y-2">
                <textarea rows={3} className="input" value={editText} onChange={(e) => setEditText(e.target.value)} />
                <div className="flex gap-2">
                  <button className="btn" onClick={() => act(async () => { await memories.edit(m.id, editText); setEditingId(null); })}>Save</button>
                  <button className="btn-quiet" onClick={() => setEditingId(null)}>Cancel</button>
                </div>
              </div>
            ) : (
              <>
                <p>{m.content}</p>
                <div className="mt-2 flex items-center gap-2">
                  <span className="rounded bg-mist px-2 py-0.5 text-xs">{m.status ?? "pending"}</span>
                  <button className="btn-quiet" onClick={() => { setEditingId(m.id); setEditText(m.content); }}>Edit</button>
                  <button className="btn-quiet" onClick={() => act(() => memories.approve(m.id))}>Approve</button>
                  <button className="btn-danger" onClick={() => act(() => memories.reject(m.id))}>Reject</button>
                </div>
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
