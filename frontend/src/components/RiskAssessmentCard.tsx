"use client";

import { useState } from "react";
import { evaluateAllTransactions, AssessmentBatchResponse } from "@/lib/api";
import {
  ShieldCheck,
  Play,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ShieldAlert,
  HelpCircle,
  XCircle,
  FileText,
  Info,
} from "lucide-react";

interface RiskAssessmentCardProps {
  onAssessmentComplete?: () => void;
}

export function RiskAssessmentCard({ onAssessmentComplete }: RiskAssessmentCardProps) {
  const [loading, setLoading] = useState<boolean>(false);
  const [batchResult, setBatchResult] = useState<AssessmentBatchResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleRunAssessments = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await evaluateAllTransactions();
      setBatchResult(res);
      if (onAssessmentComplete) {
        onAssessmentComplete();
      }
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error ? err.message : "Failed to execute batch risk assessment."
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
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-semibold text-zinc-100">
                Decision-Support Risk Assessment Engine
              </h3>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-zinc-800 text-zinc-400">
                Phase 4 Active
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Deterministic bounded risk scores and explainable advisory recommendations (ALLOW / REVIEW / BLOCK).
            </p>
          </div>
        </div>

        <button
          onClick={handleRunAssessments}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-zinc-950 font-semibold text-xs transition-all shadow-lg shadow-emerald-950/50 cursor-pointer"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Evaluating Risk Models & Rules...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Execute Risk Assessments</span>
            </>
          )}
        </button>
      </div>

      {/* Observability Summary Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <div className="p-3.5 rounded-lg bg-zinc-950/80 border border-zinc-800/80 space-y-1">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Total Evaluated</span>
            <FileText className="w-3.5 h-3.5" />
          </div>
          <div className="font-mono text-xl font-bold text-zinc-100">
            {batchResult ? batchResult.total_evaluated : "—"}
          </div>
          <span className="text-[10px] text-zinc-500 font-mono">
            {batchResult ? `${batchResult.ruleset_version} | ${batchResult.decision_policy_version}` : "rs_v1.0.0"}
          </span>
        </div>

        <div className="p-3.5 rounded-lg bg-zinc-950/80 border border-zinc-800/80 space-y-1">
          <div className="flex items-center justify-between text-emerald-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider">ALLOW</span>
            <CheckCircle2 className="w-3.5 h-3.5" />
          </div>
          <div className="font-mono text-xl font-bold text-emerald-400">
            {batchResult ? batchResult.allow_count : "—"}
          </div>
          <span className="text-[10px] text-zinc-500">Score &lt; 30 (Low Risk)</span>
        </div>

        <div className="p-3.5 rounded-lg bg-zinc-950/80 border border-zinc-800/80 space-y-1">
          <div className="flex items-center justify-between text-amber-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider">REVIEW</span>
            <HelpCircle className="w-3.5 h-3.5" />
          </div>
          <div className="font-mono text-xl font-bold text-amber-400">
            {batchResult ? batchResult.review_count : "—"}
          </div>
          <span className="text-[10px] text-zinc-500">Score 30–59 (Medium Risk)</span>
        </div>

        <div className="p-3.5 rounded-lg bg-zinc-950/80 border border-zinc-800/80 space-y-1">
          <div className="flex items-center justify-between text-rose-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider">BLOCK (Advisory)</span>
            <XCircle className="w-3.5 h-3.5" />
          </div>
          <div className="font-mono text-xl font-bold text-rose-400">
            {batchResult ? batchResult.block_count : "—"}
          </div>
          <span className="text-[10px] text-zinc-500">Score &ge; 60 (High Risk)</span>
        </div>
      </div>

      {/* Success Notification */}
      {batchResult && (
        <div className="flex items-start gap-2.5 p-3.5 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <span>
            Batch assessment evaluation completed: {batchResult.total_evaluated} transactions evaluated ({batchResult.allow_count} ALLOW, {batchResult.review_count} REVIEW, {batchResult.block_count} BLOCK).
          </span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-start gap-2.5 p-3.5 rounded-lg bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Strict Non-Action Advisory Guardrail Banner */}
      <div className="flex items-start gap-3 p-3.5 rounded-lg bg-zinc-950 border border-amber-500/30 text-xs leading-relaxed">
        <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1 text-zinc-400">
          <span className="text-zinc-200 font-semibold block">
            Advisory Decision Support Guardrail (Non-Executing System)
          </span>
          <p>
            Recommendations (<code className="text-emerald-400 font-mono">ALLOW</code>, <code className="text-amber-400 font-mono">REVIEW</code>, <code className="text-rose-400 font-mono">BLOCK</code>) represent risk intelligence advice for human analysts. The system <strong className="text-zinc-200">never executes automated transaction blocks</strong>, payment cancellations, or external payment gateway calls. Underlying transaction status is strictly preserved.
          </p>
        </div>
      </div>
    </div>
  );
}
