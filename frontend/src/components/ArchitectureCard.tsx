import React from "react";
import {
  GitFork,
  CheckCircle,
  Database,
  Network,
  Lock,
  Boxes,
} from "lucide-react";

export const ArchitectureCard: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Foundation Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 space-y-3">
          <div className="flex items-center gap-2.5 text-zinc-100 font-semibold text-sm">
            <div className="p-1.5 rounded-md bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Boxes className="w-4 h-4" />
            </div>
            <span>FastAPI Gateway</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Asynchronous REST backend with Pydantic validation, structured v1
            routing, CORS controls, and diagnostic health probes.
          </p>
          <div className="flex flex-wrap gap-1.5 pt-1">
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
              FastAPI
            </span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
              Pydantic v2
            </span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
              Pytest
            </span>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 space-y-3">
          <div className="flex items-center gap-2.5 text-zinc-100 font-semibold text-sm">
            <div className="p-1.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Database className="w-4 h-4" />
            </div>
            <span>PostgreSQL & Persistence</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            SQLAlchemy 2.0 async engine session management, connection pooling,
            and Docker Compose container definition for local persistence.
          </p>
          <div className="flex flex-wrap gap-1.5 pt-1">
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
              SQLAlchemy 2.0
            </span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
              asyncpg
            </span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
              PostgreSQL 16
            </span>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 space-y-3">
          <div className="flex items-center gap-2.5 text-zinc-100 font-semibold text-sm">
            <div className="p-1.5 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Network className="w-4 h-4" />
            </div>
            <span>Next.js Console</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            High-performance Next.js App Router frontend with TypeScript,
            real-time API integration, and analyst-oriented interface.
          </p>
          <div className="flex flex-wrap gap-1.5 pt-1">
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
              Next.js 15+
            </span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
              TypeScript
            </span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
              Tailwind CSS
            </span>
          </div>
        </div>
      </div>

      {/* Decision Support Framework & Guardrails */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 space-y-3">
          <div className="flex items-center gap-2 text-zinc-100 font-semibold text-sm">
            <GitFork className="w-4 h-4 text-emerald-400" />
            <span>Decision Taxonomy</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between p-2 rounded bg-zinc-950/50 border border-zinc-800/60">
              <span className="font-mono text-emerald-400 font-semibold">ALLOW</span>
              <span className="text-zinc-400">Normal velocity & legitimate entity traces</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-zinc-950/50 border border-zinc-800/60">
              <span className="font-mono text-amber-400 font-semibold">REVIEW</span>
              <span className="text-zinc-400">Borderline signals requiring analyst review</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-zinc-950/50 border border-zinc-800/60">
              <span className="font-mono text-rose-400 font-semibold">BLOCK</span>
              <span className="text-zinc-400">High-confidence coordinated abuse ring indicators</span>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 space-y-3">
          <div className="flex items-center gap-2 text-zinc-100 font-semibold text-sm">
            <Lock className="w-4 h-4 text-sky-400" />
            <span>Architectural Guardrails</span>
          </div>
          <ul className="space-y-2 text-xs text-zinc-400">
            <li className="flex items-start gap-2">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span>
                <strong className="text-zinc-300">Decision-Support Only:</strong> AI does not execute autonomous financial debits or irreversible fund actions.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span>
                <strong className="text-zinc-300">Auditable Explanations:</strong> Every evaluation links directly to the underlying triggering signals.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span>
                <strong className="text-zinc-300">Modular Extensibility:</strong> Clean boundaries between ingestion, ring detection, scoring, and storage.
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
