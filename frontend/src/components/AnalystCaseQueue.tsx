"use client";

import { useEffect, useState, useCallback } from "react";
import { getCases, createCase, CaseRead } from "@/lib/api";
import { CaseDetailView } from "@/components/CaseDetailView";
import {
  Briefcase,
  RefreshCw,
  Plus,
  Filter,
  UserCheck,
  Clock,
  CheckCircle2,
  AlertTriangle,
  FileCode2,
  Lock,
  ChevronRight,
  Shield,
  Layers,
} from "lucide-react";

interface AnalystCaseQueueProps {
  refreshTrigger?: number;
}

export function AnalystCaseQueue({ refreshTrigger = 0 }: AnalystCaseQueueProps) {
  const [cases, setCases] = useState<CaseRead[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusTab, setStatusTab] = useState<string>("");
  const [priorityFilter, setPriorityFilter] = useState<string>("");
  const [selectedCase, setSelectedCase] = useState<CaseRead | null>(null);

  // Manual Case Creation modal state
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [createTxnId, setCreateTxnId] = useState<string>("");
  const [createTitle, setCreateTitle] = useState<string>("");
  const [createPriority, setCreatePriority] = useState<string>("MEDIUM");
  const [createAssignee, setCreateAssignee] = useState<string>("");
  const [createDescription, setCreateDescription] = useState<string>("");
  const [createLoading, setCreateLoading] = useState<boolean>(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const fetchCasesList = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCases({
        status: statusTab || undefined,
        priority: priorityFilter || undefined,
        limit: 50,
      });
      setCases(data.items);
      setTotal(data.total);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load case queue");
    } finally {
      setLoading(false);
    }
  }, [statusTab, priorityFilter]);

  useEffect(() => {
    fetchCasesList();
  }, [fetchCasesList, refreshTrigger]);

  const handleCreateCaseSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createTxnId.trim() || !createTitle.trim()) {
      setCreateError("Transaction ID and Title are required.");
      return;
    }
    setCreateLoading(true);
    setCreateError(null);
    try {
      const newCase = await createCase({
        transaction_id: createTxnId.trim(),
        title: createTitle.trim(),
        priority: createPriority,
        assigned_to: createAssignee.trim() || undefined,
        description: createDescription.trim() || undefined,
        actor: "lead_analyst",
      });
      setShowCreateModal(false);
      setCreateTxnId("");
      setCreateTitle("");
      setCreateDescription("");
      setCreateAssignee("");
      await fetchCasesList();
      setSelectedCase(newCase);
    } catch (err: unknown) {
      setCreateError(err instanceof Error ? err.message : "Failed to create case");
    } finally {
      setCreateLoading(false);
    }
  };

  const handleCaseUpdated = (updatedCase: CaseRead) => {
    setSelectedCase(updatedCase);
    setCases((prev) => prev.map((c) => (c.case_id === updatedCase.case_id ? updatedCase : c)));
  };

  const getPriorityBadgeClass = (priority: string) => {
    switch (priority) {
      case "CRITICAL":
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      case "HIGH":
        return "bg-rose-500/10 text-rose-400 border-rose-500/30";
      case "MEDIUM":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      default:
        return "bg-zinc-800 text-zinc-300 border-zinc-700";
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case "NEW":
        return "bg-sky-500/10 text-sky-400 border-sky-500/30";
      case "ASSIGNED":
        return "bg-indigo-500/10 text-indigo-400 border-indigo-500/30";
      case "IN_REVIEW":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      case "PENDING_INFO":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/30";
      case "CLOSED":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      default:
        return "bg-zinc-800 text-zinc-300 border-zinc-700";
    }
  };

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6 space-y-6 shadow-xl backdrop-blur-sm">
      {/* Card Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-bold text-zinc-100">
              Analyst Investigation & Case Review Queue
            </h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Phase 5
            </span>
          </div>
          <p className="text-xs text-zinc-400">
            Conduct human compliance investigations, assign analysts, log append-only notes, and record final review dispositions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-colors shadow-lg shadow-indigo-950/50"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Create Case</span>
          </button>

          <button
            onClick={fetchCasesList}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-indigo-400" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Status Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 p-1 bg-zinc-950/80 rounded-xl border border-zinc-800/80">
          {[
            { label: "All Cases", value: "" },
            { label: "New", value: "NEW" },
            { label: "In Review", value: "IN_REVIEW" },
            { label: "Pending Info", value: "PENDING_INFO" },
            { label: "Closed", value: "CLOSED" },
          ].map((tab) => (
            <button
              key={tab.label}
              onClick={() => setStatusTab(tab.value)}
              className={`px-3 py-1 rounded-lg font-medium transition-all ${
                statusTab === tab.value
                  ? "bg-indigo-600 text-white shadow"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Priority Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-zinc-400" />
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-zinc-900 border border-zinc-800 rounded-lg px-2.5 py-1 text-zinc-300 text-xs focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
          {error}
        </div>
      )}

      {/* Cases Queue Table */}
      <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950/50">
        <table className="w-full text-left text-xs text-zinc-400">
          <thead className="border-b border-zinc-800 bg-zinc-900/80 text-[11px] font-semibold text-zinc-300 uppercase tracking-wider">
            <tr>
              <th className="px-4 py-3">Case ID</th>
              <th className="px-4 py-3">Priority</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Case Title & Transaction</th>
              <th className="px-4 py-3">Assignee</th>
              <th className="px-4 py-3">Disposition</th>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60 font-sans">
            {loading && cases.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-zinc-500">
                  <div className="inline-flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
                    <span>Loading case queue...</span>
                  </div>
                </td>
              </tr>
            ) : cases.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-zinc-500">
                  No cases found matching current filters.
                </td>
              </tr>
            ) : (
              cases.map((c) => (
                <tr key={c.case_id} className="hover:bg-zinc-900/50 transition-colors">
                  <td className="px-4 py-3 font-mono font-bold text-zinc-200">{c.case_id}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getPriorityBadgeClass(c.priority)}`}>
                      {c.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getStatusBadgeClass(c.status)}`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="space-y-0.5">
                      <div className="text-zinc-200 font-medium max-w-xs truncate">{c.title}</div>
                      <div className="font-mono text-[10px] text-zinc-400">
                        {c.transaction?.transaction_id || `Tx #${c.transaction_id}`}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {c.assigned_to ? (
                      <span className="font-mono text-[11px] text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                        {c.assigned_to}
                      </span>
                    ) : (
                      <span className="text-zinc-500 italic">Unassigned</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {c.disposition ? (
                      <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                        {c.disposition}
                      </span>
                    ) : (
                      <span className="text-zinc-500 text-[11px]">Pending</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-[11px] text-zinc-400">
                    {new Date(c.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => setSelectedCase(c)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition-colors"
                    >
                      <span>Review</span>
                      <ChevronRight className="w-3 h-3 text-zinc-400" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Case Creation Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/80 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="relative w-full max-w-lg bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl p-6 space-y-4">
            <h3 className="text-base font-bold text-zinc-100">Create Investigation Case</h3>

            {createError && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-lg">
                {createError}
              </div>
            )}

            <form onSubmit={handleCreateCaseSubmit} className="space-y-3 text-xs">
              <div className="space-y-1">
                <label className="text-zinc-300 font-medium">Transaction ID *</label>
                <input
                  type="text"
                  value={createTxnId}
                  onChange={(e) => setCreateTxnId(e.target.value)}
                  placeholder="e.g. txn_p4_live_ring_1"
                  required
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2 text-zinc-200 font-mono"
                />
              </div>

              <div className="space-y-1">
                <label className="text-zinc-300 font-medium">Case Title *</label>
                <input
                  type="text"
                  value={createTitle}
                  onChange={(e) => setCreateTitle(e.target.value)}
                  placeholder="e.g. Coordinated Device Ring Abuse Investigation"
                  required
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2 text-zinc-200"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-zinc-300 font-medium">Priority</label>
                  <select
                    value={createPriority}
                    onChange={(e) => setCreatePriority(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2 text-zinc-200"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-zinc-300 font-medium">Assign To Analyst</label>
                  <input
                    type="text"
                    value={createAssignee}
                    onChange={(e) => setCreateAssignee(e.target.value)}
                    placeholder="e.g. analyst_sarah"
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2 text-zinc-200 font-mono"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-zinc-300 font-medium">Initial Context / Description</label>
                <textarea
                  value={createDescription}
                  onChange={(e) => setCreateDescription(e.target.value)}
                  placeholder="Investigation context or trigger reason..."
                  rows={3}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2 text-zinc-200 resize-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-zinc-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 rounded-lg bg-zinc-800 text-zinc-300 text-xs font-medium hover:bg-zinc-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createLoading}
                  className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50"
                >
                  {createLoading ? "Creating..." : "Create Case"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Case Detail Inspector Modal */}
      {selectedCase && (
        <CaseDetailView
          caseItem={selectedCase}
          onClose={() => setSelectedCase(null)}
          onCaseUpdated={handleCaseUpdated}
        />
      )}
    </div>
  );
}
