"use client";

import { useState } from "react";
import {
  CaseRead,
  updateCaseStatus,
  updateCaseAssignment,
  updateCasePriority,
  addCaseNote,
  recordCaseDisposition,
} from "@/lib/api";
import {
  X,
  FileText,
  History,
  Send,
  CheckCircle2,
  AlertOctagon,
  Scale,
  Lock,
  ArrowRight,
} from "lucide-react";

interface CaseDetailViewProps {
  caseItem: CaseRead;
  onClose: () => void;
  onCaseUpdated: (updatedCase: CaseRead) => void;
}

export function CaseDetailView({ caseItem, onClose, onCaseUpdated }: CaseDetailViewProps) {
  // Local form states
  const [newStatus, setNewStatus] = useState<string>(caseItem.status);
  const [statusReason, setStatusReason] = useState<string>("");
  const [newPriority, setNewPriority] = useState<string>(caseItem.priority);
  const [assignee, setAssignee] = useState<string>(caseItem.assigned_to || "");
  const [noteContent, setNoteContent] = useState<string>("");
  const [noteAuthor, setNoteAuthor] = useState<string>("analyst_lead");

  // Disposition form
  const [disposition, setDisposition] = useState<string>(caseItem.disposition || "CONFIRMED_SUSPICIOUS");
  const [dispositionRationale, setDispositionRationale] = useState<string>(
    caseItem.disposition_rationale || ""
  );
  const [dispositionActor, setDispositionActor] = useState<string>("senior_analyst");

  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Status update handler
  const handleStatusChange = async () => {
    if (newStatus === caseItem.status) return;
    setLoadingAction("status");
    setActionError(null);
    setActionSuccess(null);
    try {
      const updated = await updateCaseStatus(caseItem.case_id, {
        status: newStatus,
        actor: "analyst",
        reason: statusReason || undefined,
      });
      onCaseUpdated(updated);
      setActionSuccess(`Status successfully transitioned to ${newStatus}`);
      setStatusReason("");
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Failed to update status");
    } finally {
      setLoadingAction(null);
    }
  };

  // Priority update handler
  const handlePriorityChange = async () => {
    if (newPriority === caseItem.priority) return;
    setLoadingAction("priority");
    setActionError(null);
    setActionSuccess(null);
    try {
      const updated = await updateCasePriority(caseItem.case_id, {
        priority: newPriority,
        actor: "analyst",
      });
      onCaseUpdated(updated);
      setActionSuccess(`Priority updated to ${newPriority}`);
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Failed to update priority");
    } finally {
      setLoadingAction(null);
    }
  };

  // Assignment update handler
  const handleAssignmentChange = async () => {
    setLoadingAction("assignment");
    setActionError(null);
    setActionSuccess(null);
    try {
      const updated = await updateCaseAssignment(caseItem.case_id, {
        assigned_to: assignee.trim() || null,
        actor: "analyst",
      });
      onCaseUpdated(updated);
      setActionSuccess(`Case assignment updated`);
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Failed to update assignment");
    } finally {
      setLoadingAction(null);
    }
  };

  // Add note handler
  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteContent.trim()) return;
    setLoadingAction("note");
    setActionError(null);
    setActionSuccess(null);
    try {
      await addCaseNote(caseItem.case_id, {
        content: noteContent.trim(),
        author: noteAuthor.trim() || "analyst",
      });
      // Refresh case to include new note and audit event
      const updated = await updateCasePriority(caseItem.case_id, {
        priority: caseItem.priority,
        actor: "analyst",
      });
      onCaseUpdated(updated);
      setNoteContent("");
      setActionSuccess("Note added to investigation history");
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Failed to add note");
    } finally {
      setLoadingAction(null);
    }
  };

  // Record disposition handler
  const handleRecordDisposition = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dispositionRationale.trim()) {
      setActionError("Disposition rationale is required.");
      return;
    }
    setLoadingAction("disposition");
    setActionError(null);
    setActionSuccess(null);
    try {
      const updated = await recordCaseDisposition(caseItem.case_id, {
        disposition,
        rationale: dispositionRationale.trim(),
        actor: dispositionActor.trim() || "analyst",
      });
      onCaseUpdated(updated);
      setActionSuccess(`Disposition '${disposition}' recorded and case closed`);
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Failed to record disposition");
    } finally {
      setLoadingAction(null);
    }
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/80 backdrop-blur-sm animate-in fade-in duration-150 overflow-y-auto">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden my-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-zinc-800 bg-zinc-950/50">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs text-zinc-400 font-bold">{caseItem.case_id}</span>
              <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${getStatusBadgeClass(caseItem.status)}`}>
                {caseItem.status}
              </span>
              <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${getPriorityBadgeClass(caseItem.priority)}`}>
                {caseItem.priority} PRIORITY
              </span>
              {caseItem.disposition && (
                <span className="px-2 py-0.5 rounded text-[11px] font-semibold border bg-emerald-500/10 text-emerald-300 border-emerald-500/30">
                  DISPOSITION: {caseItem.disposition}
                </span>
              )}
            </div>
            <h3 className="text-lg font-bold text-zinc-100">{caseItem.title}</h3>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Status Alerts */}
        {actionError && (
          <div className="px-6 py-2.5 bg-rose-500/10 border-b border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertOctagon className="w-4 h-4 shrink-0" />
            <span>{actionError}</span>
          </div>
        )}
        {actionSuccess && (
          <div className="px-6 py-2.5 bg-emerald-500/10 border-b border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{actionSuccess}</span>
          </div>
        )}

        {/* Modal Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1 text-xs">
          {/* Critical Non-Action Guarantee Notice */}
          <div className="p-3.5 rounded-xl border border-emerald-500/20 bg-emerald-500/5 text-emerald-300 flex items-start gap-3">
            <Lock className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-semibold text-emerald-200">Advisory Review Sentinel — Non-Action Guarantee</span>
              <p className="text-[11px] text-emerald-400/90 leading-relaxed">
                Analyst case actions and recorded dispositions are compliance investigation outcomes only.
                The system strictly maintains immutable transaction states and executes zero financial or payment blocks.
              </p>
            </div>
          </div>

          {/* Grid Overview: Case Controls & Linked Data */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Case Management Controls */}
            <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/60 space-y-4">
              <span className="font-semibold text-zinc-200 uppercase tracking-wider text-[11px]">
                Case Workflow Controls
              </span>

              {/* Status Transition */}
              <div className="space-y-1.5">
                <label className="text-zinc-400">Transition Status</label>
                <div className="flex gap-2">
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-2.5 py-1.5 text-zinc-200 text-xs"
                  >
                    <option value="NEW">NEW</option>
                    <option value="ASSIGNED">ASSIGNED</option>
                    <option value="IN_REVIEW">IN_REVIEW</option>
                    <option value="PENDING_INFO">PENDING_INFO</option>
                    <option value="CLOSED">CLOSED</option>
                    <option value="ARCHIVED">ARCHIVED</option>
                  </select>
                  <button
                    type="button"
                    onClick={handleStatusChange}
                    disabled={loadingAction === "status" || newStatus === caseItem.status}
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-zinc-950 font-semibold rounded-lg text-xs"
                  >
                    {loadingAction === "status" ? "..." : "Update"}
                  </button>
                </div>
              </div>

              {/* Priority Update */}
              <div className="space-y-1.5">
                <label className="text-zinc-400">Priority Level</label>
                <div className="flex gap-2">
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-2.5 py-1.5 text-zinc-200 text-xs"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                  <button
                    type="button"
                    onClick={handlePriorityChange}
                    disabled={loadingAction === "priority" || newPriority === caseItem.priority}
                    className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 text-zinc-200 font-medium rounded-lg text-xs"
                  >
                    {loadingAction === "priority" ? "..." : "Set"}
                  </button>
                </div>
              </div>

              {/* Assignee Update */}
              <div className="space-y-1.5">
                <label className="text-zinc-400">Assigned Analyst</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={assignee}
                    onChange={(e) => setAssignee(e.target.value)}
                    placeholder="e.g. analyst_sarah"
                    className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-2.5 py-1.5 text-zinc-200 text-xs font-mono"
                  />
                  <button
                    type="button"
                    onClick={handleAssignmentChange}
                    disabled={loadingAction === "assignment"}
                    className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 text-zinc-200 font-medium rounded-lg text-xs"
                  >
                    {loadingAction === "assignment" ? "..." : "Assign"}
                  </button>
                </div>
              </div>
            </div>

            {/* Linked Data Snapshot */}
            <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/60 space-y-3">
              <span className="font-semibold text-zinc-200 uppercase tracking-wider text-[11px]">
                Linked Transaction & Assessment
              </span>

              <div className="space-y-2 text-[11px]">
                <div className="flex justify-between py-1 border-b border-zinc-800/80">
                  <span className="text-zinc-400">Transaction ID:</span>
                  <span className="font-mono text-zinc-200">{caseItem.transaction?.transaction_id || `Tx #${caseItem.transaction_id}`}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-zinc-800/80">
                  <span className="text-zinc-400">Customer ID:</span>
                  <span className="font-mono text-zinc-200">{caseItem.transaction?.customer_id || "N/A"}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-zinc-800/80">
                  <span className="text-zinc-400">Amount / Currency:</span>
                  <span className="font-mono text-zinc-200">
                    {caseItem.transaction?.amount ? `${caseItem.transaction.amount} ${caseItem.transaction.currency}` : "N/A"}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-zinc-800/80">
                  <span className="text-zinc-400">Transaction Status:</span>
                  <span className="font-mono text-emerald-400 font-semibold">{caseItem.transaction?.status || "SUCCESS (Unmodified)"}</span>
                </div>
                {caseItem.assessment && (
                  <>
                    <div className="flex justify-between py-1 border-b border-zinc-800/80">
                      <span className="text-zinc-400">Advisory Recommendation:</span>
                      <span className="font-mono font-bold text-amber-400">{caseItem.assessment.recommendation} ({caseItem.assessment.score}/100)</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-zinc-800/80">
                      <span className="text-zinc-400">Ruleset / Policy:</span>
                      <span className="font-mono text-zinc-400">{caseItem.assessment.ruleset_version} / {caseItem.assessment.decision_policy_version}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Analyst Review Disposition Section */}
          <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-zinc-200 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                <Scale className="w-3.5 h-3.5 text-emerald-400" />
                <span>Analyst Review Disposition</span>
              </span>
              {caseItem.disposition && (
                <span className="text-[10px] text-zinc-400 font-mono">
                  Recorded by {caseItem.disposition_by || "analyst"} on {new Date(caseItem.disposition_at || "").toLocaleString()}
                </span>
              )}
            </div>

            <form onSubmit={handleRecordDisposition} className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-zinc-400 text-[11px]">Disposition Classification</label>
                  <select
                    value={disposition}
                    onChange={(e) => setDisposition(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-2.5 py-1.5 text-zinc-200 text-xs"
                  >
                    <option value="NO_ACTION">NO_ACTION — No operational action required</option>
                    <option value="FALSE_POSITIVE">FALSE_POSITIVE — Legitimate customer behavior</option>
                    <option value="CONFIRMED_SUSPICIOUS">CONFIRMED_SUSPICIOUS — Coordinated abuse confirmed</option>
                    <option value="ESCALATED">ESCALATED — Escalated to senior legal/risk team</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-zinc-400 text-[11px]">Reviewing Analyst</label>
                  <input
                    type="text"
                    value={dispositionActor}
                    onChange={(e) => setDispositionActor(e.target.value)}
                    placeholder="Analyst name"
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-2.5 py-1.5 text-zinc-200 text-xs font-mono"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-zinc-400 text-[11px]">Investigation Rationale & Justification</label>
                <textarea
                  value={dispositionRationale}
                  onChange={(e) => setDispositionRationale(e.target.value)}
                  placeholder="Detail evidence, phone/bank verification findings, or abuse cluster analysis..."
                  rows={2}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-zinc-200 text-xs resize-none"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loadingAction === "disposition" || !dispositionRationale.trim()}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-zinc-950 font-bold rounded-lg text-xs shadow-lg shadow-emerald-950/40"
                >
                  {loadingAction === "disposition" ? "Recording..." : "Record Disposition & Close Case"}
                </button>
              </div>
            </form>
          </div>

          {/* Append-Only Analyst Notes */}
          <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/60 space-y-4">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-sky-400" />
              <span className="font-semibold text-zinc-200 uppercase tracking-wider text-[11px]">
                Analyst Investigation Notes ({caseItem.notes?.length || 0})
              </span>
            </div>

            {/* Notes list */}
            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
              {caseItem.notes && caseItem.notes.length > 0 ? (
                caseItem.notes.map((note) => (
                  <div key={note.note_id} className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 space-y-1">
                    <div className="flex items-center justify-between text-[10px] text-zinc-400">
                      <span className="font-semibold text-zinc-300 font-mono">{note.author}</span>
                      <span>{new Date(note.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-zinc-300 whitespace-pre-wrap">{note.content}</p>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-zinc-500 italic">No notes added yet.</div>
              )}
            </div>

            {/* Add note form */}
            <form onSubmit={handleAddNote} className="space-y-2 pt-2 border-t border-zinc-800">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={noteAuthor}
                  onChange={(e) => setNoteAuthor(e.target.value)}
                  placeholder="Author"
                  className="w-32 bg-zinc-900 border border-zinc-800 rounded-lg px-2.5 py-1.5 text-zinc-200 text-xs font-mono"
                />
                <input
                  type="text"
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  placeholder="Append observation or finding note..."
                  className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-2.5 py-1.5 text-zinc-200 text-xs"
                />
                <button
                  type="submit"
                  disabled={loadingAction === "note" || !noteContent.trim()}
                  className="px-3 py-1.5 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white font-semibold rounded-lg text-xs flex items-center gap-1"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Add</span>
                </button>
              </div>
            </form>
          </div>

          {/* Immutable Case Audit Trail Timeline */}
          <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/60 space-y-3">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-emerald-400" />
              <span className="font-semibold text-zinc-200 uppercase tracking-wider text-[11px]">
                Immutable Case Audit Trail ({caseItem.audit_events?.length || 0} Events)
              </span>
            </div>

            <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
              {caseItem.audit_events && caseItem.audit_events.length > 0 ? (
                caseItem.audit_events.map((evt) => (
                  <div key={evt.event_id} className="p-2.5 rounded-lg bg-zinc-900/90 border border-zinc-800/80 flex items-start gap-3">
                    <div className="p-1.5 rounded bg-zinc-800 text-zinc-300 font-mono text-[10px] uppercase font-bold shrink-0">
                      {evt.event_type}
                    </div>
                    <div className="flex-1 space-y-1 text-[11px]">
                      <div className="flex items-center justify-between text-zinc-400 text-[10px]">
                        <span className="font-semibold text-zinc-300 font-mono">Actor: {evt.actor}</span>
                        <span>{new Date(evt.created_at).toLocaleString()}</span>
                      </div>
                      {evt.from_state || evt.to_state ? (
                        <div className="flex items-center gap-1.5 text-zinc-300 font-mono text-[11px]">
                          <span className="text-zinc-500">{evt.from_state || "initial"}</span>
                          <ArrowRight className="w-3 h-3 text-zinc-500" />
                          <span className="text-emerald-400 font-bold">{evt.to_state}</span>
                        </div>
                      ) : null}
                      {evt.event_details && Object.keys(evt.event_details).length > 0 && (
                        <pre className="text-[10px] font-mono text-zinc-400 bg-zinc-950 p-1.5 rounded overflow-x-auto">
                          {JSON.stringify(evt.event_details, null, 2)}
                        </pre>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-zinc-500 italic">No audit events recorded.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
