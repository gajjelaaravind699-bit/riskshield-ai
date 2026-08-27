"use client";

import { useState } from "react";
import { Header } from "@/components/Header";
import { HealthStatus } from "@/components/HealthStatus";
import { ArchitectureCard } from "@/components/ArchitectureCard";
import { TransactionIngestForm } from "@/components/TransactionIngestForm";
import { TransactionList } from "@/components/TransactionList";
import { AnalysisControlCard } from "@/components/AnalysisControlCard";
import { FindingsExplorer } from "@/components/FindingsExplorer";
import {
  ShieldCheck,
  Radio,
  FileCode2,
  BookOpen,
  ArrowUpRight,
  Terminal,
  Database,
  Network,
} from "lucide-react";

export default function Home() {
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);
  const [findingsTrigger, setFindingsTrigger] = useState<number>(0);

  const handleTransactionIngested = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleAnalysisComplete = () => {
    setFindingsTrigger((prev) => prev + 1);
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-zinc-950">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero & Sentinel Status Banner */}
        <section className="relative overflow-hidden rounded-2xl border border-zinc-800 bg-gradient-to-br from-zinc-900 via-zinc-950 to-zinc-900 p-8 shadow-2xl">
          <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 -mb-8 -ml-8 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 space-y-4 max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-medium">
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              <span>Phase 3: Graph & Pattern Analysis Engine Active</span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold text-zinc-100 tracking-tight">
              RiskShield AI{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-200 to-sky-400">
                Sentinel Console
              </span>
            </h1>

            <p className="text-sm sm:text-base text-zinc-400 leading-relaxed">
              Detect coordinated payment abuse across dispersed accounts, devices, and payment
              instruments. Evaluate multi-account entity sharing, velocity bursts, and failure sequences
              with explainable evidence traces and deterministic rule-based pattern detectors.
            </p>

            <div className="flex flex-wrap gap-3 pt-2">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-zinc-950 font-semibold text-xs transition-all shadow-lg shadow-emerald-950/50"
              >
                <span>Interactive OpenAPI Docs</span>
                <ArrowUpRight className="w-4 h-4" />
              </a>

              <a
                href="#analysis"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 font-medium text-xs transition-all"
              >
                <Network className="w-4 h-4 text-sky-400" />
                <span>Pattern Analysis</span>
              </a>

              <a
                href="#ingest"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 font-medium text-xs transition-all"
              >
                <Database className="w-4 h-4 text-emerald-400" />
                <span>Ingestion Feed</span>
              </a>

              <a
                href="#quickstart"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 font-medium text-xs transition-all"
              >
                <BookOpen className="w-4 h-4 text-zinc-400" />
                <span>Quickstart Guide</span>
              </a>
            </div>
          </div>
        </section>

        {/* Live Backend Health & Readiness Diagnostic */}
        <section>
          <HealthStatus />
        </section>

        {/* Phase 3: Graph & Pattern Analysis Trigger Control */}
        <section id="analysis">
          <AnalysisControlCard onAnalysisComplete={handleAnalysisComplete} />
        </section>

        {/* Phase 3: Explainable Findings & Evidence Explorer */}
        <section>
          <FindingsExplorer refreshTrigger={findingsTrigger} />
        </section>

        {/* Phase 2: Transaction Ingestion Form */}
        <section id="ingest">
          <TransactionIngestForm onTransactionIngested={handleTransactionIngested} />
        </section>

        {/* Phase 2: Live Transaction List & Normalized Entity Explorer */}
        <section>
          <TransactionList refreshTrigger={refreshTrigger} />
        </section>

        {/* System Architecture & Foundation Overview */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-semibold text-zinc-100">
              System Architecture & Core Signals
            </h2>
          </div>
          <ArchitectureCard />
        </section>

        {/* Developer Quickstart Commands */}
        <section id="quickstart" className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-semibold text-zinc-200">
              Developer Local Execution Commands
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="space-y-2 rounded-lg bg-zinc-950/80 p-4 border border-zinc-800/80">
              <div className="flex items-center justify-between text-zinc-400">
                <span className="font-semibold text-zinc-300">Backend Server (FastAPI)</span>
                <span className="font-mono text-[10px]">Port: 8000</span>
              </div>
              <pre className="font-mono text-emerald-400 bg-zinc-900 p-2.5 rounded overflow-x-auto text-[11px]">
                cd backend{"\n"}
                uvicorn app.main:app --reload --port 8000
              </pre>
            </div>

            <div className="space-y-2 rounded-lg bg-zinc-950/80 p-4 border border-zinc-800/80">
              <div className="flex items-center justify-between text-zinc-400">
                <span className="font-semibold text-zinc-300">Automated Pytest Suite</span>
                <span className="font-mono text-[10px]">Backend Tests</span>
              </div>
              <pre className="font-mono text-emerald-400 bg-zinc-900 p-2.5 rounded overflow-x-auto text-[11px]">
                cd backend{"\n"}
                pytest -v
              </pre>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-800/80 bg-zinc-950 py-6 text-xs text-zinc-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <FileCode2 className="w-4 h-4 text-zinc-400" />
            <span>RiskShield AI — Explainable Abuse-Ring Sentinel</span>
          </div>
          <div>Graph Analysis & Findings Layer Active</div>
        </div>
      </footer>
    </div>
  );
}
