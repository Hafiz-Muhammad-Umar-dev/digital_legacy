"use client";

import { useEffect, useState } from "react";
import { videos } from "@/lib/api";
import type { Job, MediaAsset } from "@/lib/types";

export default function VideosPanel({ personaId }: { personaId: string }) {
  const [items, setItems] = useState<MediaAsset[] | null>(null);
  const [jobs, setJobs] = useState<Record<string, Job>>({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () => videos.list(personaId).then(setItems).catch((e) => setError(e.message));
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [personaId]);

  async function upload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true); setError("");
    try { await videos.upload(personaId, file); await load(); }
    catch (err) { setError(err instanceof Error ? err.message : "Upload failed"); }
    finally { setBusy(false); e.target.value = ""; }
  }

  async function process(id: string | number) {
    setError("");
    try {
      const job = await videos.process(id);
      setJobs((j) => ({ ...j, [String(id)]: job }));
    } catch (err) { setError(err instanceof Error ? err.message : "Could not start processing"); }
  }

  async function refreshJob(id: string | number) {
    try {
      const job = await videos.job(id);
      setJobs((j) => ({ ...j, [String(id)]: job }));
    } catch (err) { setError(err instanceof Error ? err.message : "Could not load job"); }
  }

  return (
    <div className="max-w-2xl">
      <label className="label" htmlFor="vid">Upload a video</label>
      <input id="vid" type="file" accept="video/*" onChange={upload} disabled={busy} className="text-sm" />
      {busy && <p className="mt-2 text-sm text-ink/60">Uploading…</p>}
      {error && <p className="error mt-4">{error}</p>}

      <ul className="mt-8 divide-y divide-mist border-y border-mist">
        {items === null && <li className="py-4 text-ink/60">Loading…</li>}
        {items?.length === 0 && <li className="py-4 text-ink/60">No videos uploaded yet.</li>}
        {items?.map((v) => {
          const job = jobs[String(v.id)];
          return (
            <li key={v.id} className="py-4">
              <p>{v.filename ?? `Video ${v.id}`}</p>
              {v.status && <p className="text-xs text-ink/60">Status: {v.status}</p>}
              <div className="mt-2 flex items-center gap-2">
                <button className="btn-quiet" onClick={() => process(v.id)}>Start processing</button>
                <button className="btn-quiet" onClick={() => refreshJob(v.id)}>Check job</button>
                {job && (
                  <span className="text-sm">
                    {job.status}{typeof job.progress === "number" ? ` (${job.progress}%)` : ""}{job.error ? ` – ${job.error}` : ""}
                  </span>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
