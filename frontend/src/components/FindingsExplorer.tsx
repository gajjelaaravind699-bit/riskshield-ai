"use client";

import { useEffect, useState, useCallback } from "react";
import { getFindings, getFindingById, FindingRead } from "@/lib/api";
import {
  ShieldAlert,
  RefreshCw,
  Eye,
  X,
  CreditCard,
  Smartphone,
  Globe,
  Zap,
  AlertTriangle,
  Info,
  Layers,
  Calendar,
  User,
} from "lucide-react";

interface FindingsExplorerProps {
  refreshTrigger?: number;
}

export function FindingsExplorer({ refreshTrigger = 0 }: FindingsExplorerProps) {
  const [findings, setFindings] = useState<FindingRead[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [typeFilter, setTypeFilter] = useState<string>("");
  const [severityFilter, setSeverityFilter] = useState<string>("");
  const [selectedFinding, setSelectedFinding] = useState<FindingRead | null>(null);
  const [inspectLoading, setInspectLoading] = useState<boolean>(false);

  const fetchFindingsList = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getFindings({
        finding_type: typeFilter || undefined,
        severity: severityFilter || undefined,
        limit: 50,
      });
      setFindings(data.items);
      setTotal(data.total);
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch findings."
      );
    } finally {
      setLoading(false);
    }
  }, [typeFilter, severityFilter]);

  useEffect(() => {
    fetchFindingsList();
  }, [fetchFindingsList, refreshTrigger]);

  const handleInspect = async (findingId: string) => {
    setInspectLoading(true);
    try {
      const details = await getFindingById(findingId);
      setSelectedFinding(details);
    } catch (err) {
      console.error(err);
    } finally {
      setInspectLoading(false);
    }
  };

  const getFindingTypeBadge = (type: string) => {
    switch (type) {
      case "SHARED_PAYMENT_INSTRUMENT":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CreditCard className="w-3 h-3" />
            <span>Shared Instrument</span>
          </span>
        );
      case "SHARED_DEVICE":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <Smartphone className="w-3 h-3" />
            <span>Shared Device</span>
          </span>
        );
      case "SHARED_IP_CLUSTER":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Globe className="w-3 h-3" />
            <span>Shared IP Cluster</span>
          </span>
        );
      case "VELOCITY_BURST":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Zap className="w-3 h-3" />
            <span>Velocity Burst</span>
          </span>
        );
      case "RAPID_FAILURE_BURST":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <AlertTriangle className="w-3 h-3" />
            <span>Failure Burst</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-zinc-800 text-zinc-300">
            <Info className="w-3 h-3" />
            <span>{type}</span>
          </span>
        );
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "HIGH":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
            HIGH
          </span>
        );
      case "MEDIUM":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
            MEDIUM
          </span>
        );
      case "LOW":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
            LOW
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-zinc-800 text-zinc-400">
            INFO
          </span>
        );
    }
  };

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 shadow-xl space-y-6">
      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-semibold text-zinc-100">
              Explainable Findings & Evidence Explorer
            </h3>
            <span className="px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 text-xs font-mono">
              {total} Findings
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-0.5">
            Observed relationship links, multi-account sharing, and temporal frequency anomalies.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Finding Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs focus:outline-none focus:border-amber-500"
          >
            <option value="">All Detector Types</option>
            <option value="SHARED_PAYMENT_INSTRUMENT">Shared Payment Instrument</option>
            <option value="SHARED_DEVICE">Shared Device Fingerprint</option>
            <option value="SHARED_IP_CLUSTER">Shared IP Cluster</option>
            <option value="VELOCITY_BURST">Velocity Burst</option>
            <option value="RAPID_FAILURE_BURST">Rapid Failure Burst</option>
          </select>

          {/* Severity Filter */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs focus:outline-none focus:border-amber-500"
          >
            <option value="">All Severities</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>

          {/* Refresh */}
          <button
            onClick={() => fetchFindingsList()}
            disabled={loading}
            className="p-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs transition-colors cursor-pointer"
            title="Refresh Findings"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-amber-400" : ""}`} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Findings Table */}
      <div className="overflow-x-auto rounded-lg border border-zinc-800/80 bg-zinc-950/60">
        <table className="w-full text-left text-xs">
          <thead className="bg-zinc-900/80 border-b border-zinc-800 text-zinc-400 uppercase tracking-wider font-semibold text-[10px]">
            <tr>
              <th className="px-4 py-3">Pattern Type</th>
              <th className="px-4 py-3">Finding Title</th>
              <th className="px-4 py-3">Severity</th>
              <th className="px-4 py-3">Involved Entities</th>
              <th className="px-4 py-3">Involved Transactions</th>
              <th className="px-4 py-3">Detected At</th>
              <th className="px-4 py-3 text-right">Evidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60 text-zinc-300">
            {loading && findings.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-zinc-500">
                  <div className="flex items-center justify-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin text-amber-400" />
                    <span>Loading relationship findings...</span>
                  </div>
                </td>
              </tr>
            ) : findings.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-zinc-500">
                  No relationship findings detected. Execute pattern analysis after ingesting transactions.
                </td>
              </tr>
            ) : (
              findings.map((f) => (
                <tr key={f.id} className="hover:bg-zinc-900/40 transition-colors">
                  <td className="px-4 py-3">
                    {getFindingTypeBadge(f.finding_type)}
                  </td>
                  <td className="px-4 py-3 font-medium text-zinc-100 max-w-[260px] truncate" title={f.title}>
                    {f.title}
                  </td>
                  <td className="px-4 py-3">
                    {getSeverityBadge(f.severity)}
                  </td>
                  <td className="px-4 py-3 text-zinc-400 font-mono text-[11px]">
                    {f.related_entities.length} entities
                  </td>
                  <td className="px-4 py-3 text-zinc-400 font-mono text-[11px]">
                    {f.related_transactions.length} txns
                  </td>
                  <td className="px-4 py-3 text-zinc-500 text-[11px]">
                    {new Date(f.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    })}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleInspect(f.finding_id)}
                      disabled={inspectLoading}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white text-[11px] font-medium transition-colors cursor-pointer"
                    >
                      <Eye className="w-3 h-3 text-amber-400" />
                      <span>Inspect</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Safe Evidence Detail Inspector Modal */}
      {selectedFinding && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="relative w-full max-w-2xl rounded-2xl border border-zinc-800 bg-zinc-900 p-6 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
              <div className="flex items-center gap-3">
                <ShieldAlert className="w-6 h-6 text-amber-400" />
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-base font-semibold text-zinc-100">
                      {selectedFinding.title}
                    </h4>
                    {getSeverityBadge(selectedFinding.severity)}
                  </div>
                  <p className="text-xs text-zinc-400 font-mono mt-0.5">
                    Finding ID: {selectedFinding.finding_id}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setSelectedFinding(null)}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Human-Readable Explanation */}
            <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800/80 space-y-1">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 block">
                Detector Explanation
              </span>
              <p className="text-xs text-zinc-200 leading-relaxed">
                {selectedFinding.explanation}
              </p>
            </div>

            {/* Structured Evidence Grid (Sanitized Safe Fields) */}
            <div className="space-y-2">
              <h5 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Supporting Evidence Summary
              </h5>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
                {Object.entries(selectedFinding.evidence_payload).map(([k, v]) => (
                  <div key={k} className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800/80">
                    <span className="text-[10px] text-zinc-500 block capitalize">
                      {k.replace(/_/g, " ")}
                    </span>
                    <span className="font-mono text-zinc-200 text-xs truncate block font-medium">
                      {Array.isArray(v) ? v.join(", ") : String(v)}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Participating Graph Entities */}
            <div className="space-y-2 pt-2 border-t border-zinc-800">
              <h5 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Involved Graph Entities ({selectedFinding.related_entities.length})
              </h5>
              <div className="space-y-1.5 max-h-40 overflow-y-auto">
                {selectedFinding.related_entities.map((re, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 rounded bg-zinc-950 border border-zinc-800 text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                        {re.entity.entity_type}
                      </span>
                      <span className="font-mono text-zinc-200">
                        {re.entity.entity_value}
                      </span>
                    </div>
                    <span className="font-mono text-[10px] text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/20">
                      {re.role}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Participating Transactions */}
            <div className="space-y-2 pt-2 border-t border-zinc-800">
              <h5 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Involved Transactions ({selectedFinding.related_transactions.length})
              </h5>
              <div className="space-y-1.5 max-h-40 overflow-y-auto">
                {selectedFinding.related_transactions.map((rt, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 rounded bg-zinc-950 border border-zinc-800 text-xs font-mono"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-zinc-200 font-semibold">{rt.transaction.transaction_id}</span>
                      <span className="text-zinc-500">({rt.transaction.customer_id})</span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px]">
                      <span className="text-zinc-200 font-bold">{rt.transaction.amount} {rt.transaction.currency}</span>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] ${rt.transaction.status === "SUCCESS" ? "text-emerald-400 bg-emerald-950/40" : "text-rose-400 bg-rose-950/40"}`}>
                        {rt.transaction.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Footer */}
            <div className="flex justify-end pt-3 border-t border-zinc-800">
              <button
                onClick={() => setSelectedFinding(null)}
                className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition-colors cursor-pointer"
              >
                Close Finding
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
