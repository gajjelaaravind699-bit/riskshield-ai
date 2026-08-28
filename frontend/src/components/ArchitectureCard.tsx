import React from "react";
import {
  CheckCircle,
  Database,
  Network,
  Lock,
  Boxes,
  ShieldCheck,
  Briefcase,
  Scale,
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
              Pytest (35 tests)
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
            SQLAlchemy 2.0 async engine session management, Alembic migrations,
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
              Alembic (5 revisions)
            </span>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 space-y-3">
          <div className="flex items-center gap-2.5 text-zinc-100 font-semibold text-sm">
            <div className="p-1.5 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Network className="w-4 h-4" />
            </div>
            <span>Next.js Sentinel Console</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            High-performance Next.js App Router frontend with TypeScript,
            real-time API integration, and analyst-oriented investigation interface.
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
            <Briefcase className="w-4 h-4 text-indigo-400" />
            <span>Phase 5: Human Analyst Case Management Active</span>
          </div>
          <div className="p-3.5 rounded-lg bg-zinc-950/70 border border-zinc-800/80 space-y-2 text-xs text-zinc-400 leading-relaxed">
            <p>
              Provides state machine status workflows (<code className="text-zinc-300 font-mono">NEW</code> &rarr; <code className="text-zinc-300 font-mono">IN_REVIEW</code> &rarr; <code className="text-zinc-300 font-mono">CLOSED</code>), append-only analyst notes, and human review dispositions (<code className="text-zinc-300 font-mono">CONFIRMED_SUSPICIOUS</code>, <code className="text-zinc-300 font-mono">FALSE_POSITIVE</code>, <code className="text-zinc-300 font-mono">NO_ACTION</code>, <code className="text-zinc-300 font-mono">ESCALATED</code>).
            </p>
            <p className="text-emerald-400/90 flex items-center gap-1 font-medium">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Full immutable audit trail recorded for every case lifecycle action.</span>
            </p>
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
                <strong className="text-zinc-300">Decision-Support Only:</strong> AI recommendations and analyst dispositions are compliance outcomes only — zero automated financial debits or transaction blocks executed.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span>
                <strong className="text-zinc-300">Immutable Audit Trail:</strong> Every analysis run, risk score, analyst note, and disposition is permanently recorded.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span>
                <strong className="text-zinc-300">Deterministic & Explainable:</strong> Bounded 0-100 scores mapped to specific detector finding contributions.
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
