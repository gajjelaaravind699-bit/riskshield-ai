"use client";

import { useEffect, useState, useCallback } from "react";
import { getAssessments, getAssessmentById, createCaseFromAssessment, AssessmentRead } from "@/lib/api";
import {
  Shield,
  RefreshCw,
  Eye,
  X,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Scale,
  Lock,
  Briefcase,
} from "lucide-react";

interface AssessmentExplorerProps {
  refreshTrigger?: number;
  onCaseCreated?: () => void;
}

export function AssessmentExplorer({ refreshTrigger = 0, onCaseCreated }: AssessmentExplorerProps) {
  const [assessments, setAssessments] = useState<AssessmentRead[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [recFilter, setRecFilter] = useState<string>("");
  const [riskLevelFilter, setRiskLevelFilter] = useState<string>("");
  const [selectedAssessment, setSelectedAssessment] = useState<AssessmentRead | null>(null);
  const [inspectLoading, setInspectLoading] = useState<boolean>(false);
  const [escalating, setEscalating] = useState<boolean>(false);
  const [escalateSuccess, setEscalateSuccess] = useState<string | null>(null);

  const fetchAssessmentsList = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAssessments({
        recommendation: recFilter || undefined,
        risk_level: riskLevelFilter || undefined,
        limit: 50,
      });
      setAssessments(data.items);
      setTotal(data.total);
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch risk assessments."
      );
    } finally {
      setLoading(false);
    }
  }, [recFilter, riskLevelFilter]);

  useEffect(() => {
    let ignore = false;
    getAssessments({
      recommendation: recFilter || undefined,
      risk_level: riskLevelFilter || undefined,
      limit: 50,
    })
      .then((data) => {
        if (!ignore) {
          setAssessments(data.items);
          setTotal(data.total);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!ignore) {
          setError(
            err instanceof Error ? err.message : "Failed to fetch risk assessments."
          );
          setLoading(false);
        }
      });
    return () => {
      ignore = true;
    };
  }, [recFilter, riskLevelFilter, refreshTrigger]);

  const handleInspect = async (assessmentId: string) => {
    setInspectLoading(true);
    setEscalateSuccess(null);
    try {
      const details = await getAssessmentById(assessmentId);
      setSelectedAssessment(details);
    } catch (err) {
      console.error(err);
    } finally {
      setInspectLoading(false);
    }
  };

  const handleEscalateToCase = async (assessmentId: string) => {
    setEscalating(true);
    setEscalateSuccess(null);
    try {
      const created = await createCaseFromAssessment(assessmentId, {
        actor: "lead_analyst",
      });
      setEscalateSuccess(`Case ${created.case_id} successfully created and queued!`);
      if (onCaseCreated) {
        onCaseCreated();
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create case from assessment");
    } finally {
      setEscalating(false);
    }
  };

  const getRecommendationBadge = (rec: string) => {
    switch (rec.toUpperCase()) {
      case "ALLOW":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            <span>ALLOW</span>
          </span>
        );
      case "REVIEW":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3 h-3" />
            <span>REVIEW</span>
          </span>
        );
      case "BLOCK":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <XCircle className="w-3 h-3" />
            <span>BLOCK (Advisory)</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-zinc-800 text-zinc-300">
            {rec}
          </span>
        );
    }
  };

  const getRiskLevelBadge = (level: string) => {
    switch (level.toUpperCase()) {
      case "CRITICAL":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
            CRITICAL
          </span>
        );
      case "HIGH":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
            HIGH
          </span>
        );
      case "MEDIUM":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
            MEDIUM
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            LOW
          </span>
        );
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 60) return "text-rose-400 bg-rose-500/10 border-rose-500/30";
    if (score >= 30) return "text-amber-400 bg-amber-500/10 border-amber-500/30";
    return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
  };

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 shadow-xl space-y-6">
      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-semibold text-zinc-100">
              Risk Assessments & Decision-Support Explorer
            </h3>
            <span className="px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 text-xs font-mono">
              {total} Evaluated
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-0.5">
            Deterministic risk scores, rule contribution breakdowns, and versioned recommendation traces.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Recommendation Filter */}
          <select
            value={recFilter}
            onChange={(e) => setRecFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Recommendations</option>
            <option value="ALLOW">ALLOW</option>
            <option value="REVIEW">REVIEW</option>
            <option value="BLOCK">BLOCK</option>
          </select>

          {/* Risk Level Filter */}
          <select
            value={riskLevelFilter}
            onChange={(e) => setRiskLevelFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Risk Levels</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>

          {/* Refresh */}
          <button
            onClick={() => fetchAssessmentsList()}
            disabled={loading}
            className="p-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs transition-colors cursor-pointer"
            title="Refresh Assessments"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-emerald-400" : ""}`} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Assessments Table */}
      <div className="overflow-x-auto rounded-lg border border-zinc-800/80 bg-zinc-950/60">
        <table className="w-full text-left text-xs">
          <thead className="bg-zinc-900/80 border-b border-zinc-800 text-zinc-400 uppercase tracking-wider font-semibold text-[10px]">
            <tr>
              <th className="px-4 py-3">Transaction</th>
              <th className="px-4 py-3">Customer ID</th>
              <th className="px-4 py-3">Risk Score</th>
              <th className="px-4 py-3">Risk Level</th>
              <th className="px-4 py-3">Advisory Recommendation</th>
              <th className="px-4 py-3">Ruleset / Policy</th>
              <th className="px-4 py-3">Assessed At</th>
              <th className="px-4 py-3 text-right">Audit Trace</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60 text-zinc-300">
            {loading && assessments.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-zinc-500">
                  <div className="flex items-center justify-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin text-emerald-400" />
                    <span>Loading risk assessments...</span>
                  </div>
                </td>
              </tr>
            ) : assessments.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-zinc-500">
                  No risk assessments generated yet. Click &quot;Execute Risk Assessments&quot; to evaluate persisted transactions.
                </td>
              </tr>
            ) : (
              assessments.map((a) => (
                <tr key={a.id} className="hover:bg-zinc-900/40 transition-colors">
                  <td className="px-4 py-3 font-mono font-semibold text-zinc-100">
                    {a.transaction?.transaction_id || `Txn #${a.transaction_id}`}
                  </td>
                  <td className="px-4 py-3 font-mono text-zinc-400 text-[11px]">
                    {a.transaction?.customer_id || "—"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded font-mono font-bold text-xs border ${getScoreColor(a.score)}`}>
                        {a.score}
                      </span>
                      <div className="w-16 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                        <div
                          className={`h-full ${a.score >= 60 ? "bg-rose-500" : a.score >= 30 ? "bg-amber-500" : "bg-emerald-500"}`}
                          style={{ width: `${Math.min(a.score, 100)}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {getRiskLevelBadge(a.risk_level)}
                  </td>
                  <td className="px-4 py-3">
                    {getRecommendationBadge(a.recommendation)}
                  </td>
                  <td className="px-4 py-3 text-zinc-500 font-mono text-[10px]">
                    {a.ruleset_version} / {a.decision_policy_version}
                  </td>
                  <td className="px-4 py-3 text-zinc-500 text-[11px]">
                    {new Date(a.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    })}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleInspect(a.assessment_id)}
                      disabled={inspectLoading}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white text-[11px] font-medium transition-colors cursor-pointer"
                    >
                      <Eye className="w-3 h-3 text-emerald-400" />
                      <span>Audit Trace</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Audit Detail Modal */}
      {selectedAssessment && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="relative w-full max-w-2xl rounded-2xl border border-zinc-800 bg-zinc-900 p-6 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
              <div className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-emerald-400" />
                <div>
                  <div className="flex items-center gap-2.5">
                    <h4 className="text-base font-semibold text-zinc-100">
                      Assessment: {selectedAssessment.transaction?.transaction_id || `Txn #${selectedAssessment.transaction_id}`}
                    </h4>
                    {getRecommendationBadge(selectedAssessment.recommendation)}
                  </div>
                  <p className="text-xs text-zinc-400 font-mono mt-0.5">
                    ID: {selectedAssessment.assessment_id}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setSelectedAssessment(null)}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Escalate Success Alert */}
            {escalateSuccess && (
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-lg flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{escalateSuccess}</span>
              </div>
            )}

            {/* Non-Action Execution Confirmation Banner */}
            <div className="p-3.5 rounded-lg bg-zinc-950 border border-emerald-500/30 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
                  <Lock className="w-3.5 h-3.5" />
                  <span>Non-Action Advisory Constraint Verified</span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  action_executed: false
                </span>
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                {selectedAssessment.action_disclaimer}
              </p>
            </div>

            {/* Score & Risk Level Metric Summary */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 text-center space-y-1">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 block">
                  Deterministic Score
                </span>
                <span className={`font-mono text-xl font-extrabold ${getScoreColor(selectedAssessment.score).split(" ")[0]}`}>
                  {selectedAssessment.score} / 100
                </span>
              </div>

              <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 text-center space-y-1">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 block">
                  Risk Level
                </span>
                <div>{getRiskLevelBadge(selectedAssessment.risk_level)}</div>
              </div>

              <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 text-center space-y-1">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 block">
                  Ruleset & Policy
                </span>
                <span className="font-mono text-xs text-zinc-300 truncate block">
                  {selectedAssessment.ruleset_version}
                </span>
              </div>
            </div>

            {/* Human-Readable Explanation */}
            <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 block">
                Assessment Explanation
              </span>
              <p className="text-xs text-zinc-200 leading-relaxed">
                {selectedAssessment.explanation}
              </p>
            </div>

            {/* Rule Contributions Breakdown */}
            <div className="space-y-2 pt-2 border-t border-zinc-800">
              <h5 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Rule Contributions Breakdown ({selectedAssessment.rule_contributions.length} Evaluated)
              </h5>
              <div className="space-y-2">
                {selectedAssessment.rule_contributions.map((rc, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border text-xs transition-colors ${rc.triggered ? "bg-zinc-950 border-amber-500/30" : "bg-zinc-950/50 border-zinc-800/80 opacity-75"}`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${rc.triggered ? "bg-amber-400 animate-pulse" : "bg-zinc-600"}`} />
                        <span className="font-semibold text-zinc-200">{rc.rule_name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[10px] text-zinc-500">Weight: {rc.weight}</span>
                        <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${rc.triggered ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" : "bg-zinc-800 text-zinc-500"}`}>
                          +{rc.points_contributed} pts
                        </span>
                      </div>
                    </div>
                    <p className="text-[11px] text-zinc-400 mt-1">
                      {rc.description}
                    </p>
                    {rc.finding_ids.length > 0 && (
                      <div className="flex items-center gap-1.5 mt-2 text-[10px] text-zinc-500 font-mono">
                        <span>Triggered findings:</span>
                        <span className="text-zinc-300">{rc.finding_ids.join(", ")}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Footer with Escalate to Case Action */}
            <div className="flex items-center justify-between pt-3 border-t border-zinc-800">
              <button
                type="button"
                onClick={() => handleEscalateToCase(selectedAssessment.assessment_id)}
                disabled={escalating}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50 transition-colors shadow-lg shadow-indigo-950/50 cursor-pointer"
              >
                <Briefcase className="w-3.5 h-3.5" />
                <span>{escalating ? "Creating Case..." : "Escalate to Case Queue"}</span>
              </button>

              <button
                onClick={() => setSelectedAssessment(null)}
                className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition-colors cursor-pointer"
              >
                Close Audit Trace
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
