"use client";

import { useState } from "react";
import { triggerAnalysis, AnalysisRunRead } from "@/lib/api";
import {
  Network,
  Play,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Clock,
  Layers,
  Info,
} from "lucide-react";

interface AnalysisControlCardProps {
  onAnalysisComplete?: (run: AnalysisRunRead) => void;
}

export function AnalysisControlCard({
  onAnalysisComplete,
}: AnalysisControlCardProps) {
  const [loading, setLoading] = useState<boolean>(false);
  const [lastRun, setLastRun] = useState<AnalysisRunRead | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleRunAnalysis = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const run = await triggerAnalysis();
      setLastRun(run);
      if (onAnalysisComplete) {
        onAnalysisComplete(run);
      }
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error ? err.message : "Failed to execute analysis."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-zinc-100">
              Graph & Pattern Analysis Sentinel
            </h3>
            <p className="text-xs text-zinc-400">
              Deterministic rule-based detectors correlating shared entities, velocities, and failure sequences.
            </p>
          </div>
        </div>

        <button
          onClick={handleRunAnalysis}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-zinc-950 font-semibold text-xs transition-all shadow-lg shadow-sky-950/50 cursor-pointer"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Analyzing Entities & Patterns...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Execute Pattern Analysis</span>
            </>
          )}
        </button>
      </div>

      {/* Observability Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-lg bg-zinc-950/80 border border-zinc-800/80 space-y-1">
          <span className="text-[11px] text-zinc-500 uppercase tracking-wider font-semibold block">
            Latest Execution Run
          </span>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-zinc-400" />
            <span className="font-mono text-xs text-zinc-200 truncate">
              {lastRun ? lastRun.run_id : "No run yet this session"}
            </span>
          </div>
        </div>

        <div className="p-4 rounded-lg bg-zinc-950/80 border border-zinc-800/80 space-y-1">
          <span className="text-[11px] text-zinc-500 uppercase tracking-wider font-semibold block">
            Transactions Evaluated
          </span>
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-emerald-400" />
            <span className="font-mono text-base font-bold text-zinc-100">
              {lastRun ? lastRun.total_transactions_analyzed : "—"}
            </span>
          </div>
        </div>

        <div className="p-4 rounded-lg bg-zinc-950/80 border border-zinc-800/80 space-y-1">
          <span className="text-[11px] text-zinc-500 uppercase tracking-wider font-semibold block">
            Observed Findings
          </span>
          <div className="flex items-center gap-2">
            <Network className="w-4 h-4 text-sky-400" />
            <span className="font-mono text-base font-bold text-zinc-100">
              {lastRun ? lastRun.findings_count : "—"}
            </span>
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {lastRun && (
        <div className="flex items-start gap-2.5 p-3.5 rounded-lg bg-sky-950/40 border border-sky-500/30 text-sky-300 text-xs">
          <CheckCircle2 className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
          <span>
            Analysis completed successfully: evaluated {lastRun.total_transactions_analyzed} transactions, identified {lastRun.findings_count} explainable relationship findings.
          </span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-start gap-2.5 p-3.5 rounded-lg bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Decision Support Guardrail Note */}
      <div className="flex items-start gap-2.5 p-3 rounded-lg bg-zinc-950 border border-zinc-800/80 text-zinc-400 text-xs leading-relaxed">
        <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <span>
          <strong className="text-zinc-300 font-medium">Explainable Findings Guardrail:</strong> Findings represent deterministic, evidence-backed relationship patterns (shared instruments, shared devices, shared IP subnets, velocity bursts) to support human analyst decision-making. No automated transaction rejections or black-box fraud scores are executed.
        </span>
      </div>
    </div>
  );
}
