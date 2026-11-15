"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { personas } from "@/lib/api";
import type { Persona } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import { useToast } from "@/components/ui/Toast";
import { useAuth } from "@/lib/auth-context";

export default function PersonasDashboardPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [items, setItems] = useState<Persona[] | null>(null);
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [relationship, setRelationship] = useState("");
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () => {
    personas.list()
      .then(setItems)
      .catch((e) => {
        const msg = e instanceof Error ? e.message : "Failed to load personas";
        setError(msg);
        toast(msg, "error");
      });
  };

  useEffect(() => { load(); }, []);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await personas.create({
        name,
        relationship: relationship || undefined,
        description: description || undefined,
      });
      setName("");
      setRelationship("");
      setDescription("");
      setIsModalOpen(false);
      toast("Digital persona created successfully", "success");
      await load();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Could not create persona";
      setError(msg);
      toast(msg, "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-[#E2E8E6] pb-6">
        <div>
          <h1 className="font-serif text-3xl md:text-4xl text-[#141B1F]">
            Welcome back, {user?.full_name || user?.email?.split("@")[0] || "Friend"}
          </h1>
          <p className="mt-1 text-sm text-[#5A6A72]">
            Preserve memories, curate life experiences, and converse with digital identities.
          </p>
        </div>
        <div>
          <Button variant="primary" onClick={() => setIsModalOpen(true)}>
            <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Persona
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="card-saas">
          <p className="text-xs font-semibold uppercase tracking-wider text-[#5A6A72]">Total Personas</p>
          <p className="mt-2 font-serif text-3xl text-[#141B1F]">
            {items === null ? "..." : items.length}
          </p>
          <p className="mt-1 text-xs text-[#5A6A72]">Active digital representations</p>
        </div>
      </div>

      {/* Personas Section */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-serif text-2xl text-[#141B1F]">Your Digital Personas</h2>
        </div>

        {error && <div className="error-saas mb-6">{error}</div>}

        {items === null ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="card-saas space-y-4">
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-16 w-full" />
              </div>
            ))}
          </div>
        ) : items.length === 0 ? (
          <EmptyState
            icon={
              <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            }
            title="No personas created yet"
            description="Create your first digital persona to begin collecting memories, uploading media, and starting AI conversations."
            action={
              <Button variant="primary" onClick={() => setIsModalOpen(true)}>
                Create first persona
              </Button>
            }
          />
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((p) => (
              <Link
                key={p.id}
                href={`/personas/${p.id}`}
                className="card-saas group flex flex-col justify-between hover:border-[#2B454E]/40"
              >
                <div>
                  <div className="flex items-start justify-between">
                    <h3 className="font-serif text-xl text-[#141B1F] group-hover:text-[#2B454E] transition-colors">
                      {p.name}
                    </h3>
                    {p.relationship && (
                      <span className="rounded-full bg-[#F6F5F2] px-2.5 py-0.5 text-xs font-medium text-[#5A6A72]">
                        {p.relationship}
                      </span>
                    )}
                  </div>
                  {p.description && (
                    <p className="mt-3 line-clamp-3 text-sm text-[#5A6A72]">
                      {p.description}
                    </p>
                  )}
                </div>

                <div className="mt-6 flex items-center justify-between border-t border-[#E2E8E6] pt-4 text-xs font-medium text-[#2B454E]">
                  <span>Explore workspace</span>
                  <svg className="h-4 w-4 transform transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Create Persona Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create Digital Persona"
        description="Establish a new identity to preserve memories and converse with."
      >
        <form onSubmit={create} className="space-y-4">
          <Input
            label="Name"
            id="pname"
            required
            placeholder="e.g. Eleanor Vance"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Input
            label="Relationship"
            id="prel"
            placeholder="e.g. Grandmother"
            value={relationship}
            onChange={(e) => setRelationship(e.target.value)}
          />
          <div>
            <label className="label-saas" htmlFor="pdesc">About them</label>
            <textarea
              id="pdesc"
              rows={4}
              className="input-saas resize-none"
              placeholder="Share background, personality traits, and key life stories..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-3 pt-4 border-t border-[#E2E8E6]">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={busy}>
              Create persona
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
