"use client";

import { useEffect, useState, useCallback } from "react";
import {
  getTransactions,
  getTransactionById,
  TransactionRead,
} from "@/lib/api";
import {
  RefreshCw,
  Search,
  CheckCircle,
  XCircle,
  Clock,
  Eye,
  Shield,
  Layers,
  X,
} from "lucide-react";

interface TransactionListProps {
  refreshTrigger?: number;
}

export function TransactionList({ refreshTrigger = 0 }: TransactionListProps) {
  const [transactions, setTransactions] = useState<TransactionRead[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [customerFilter, setCustomerFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [selectedTxn, setSelectedTxn] = useState<TransactionRead | null>(null);
  const [inspectLoading, setInspectLoading] = useState<boolean>(false);

  const fetchTransactionsList = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTransactions({
        customer_id: customerFilter.trim() || undefined,
        status: statusFilter.trim() || undefined,
        limit: 50,
      });
      setTransactions(data.items);
      setTotal(data.total);
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "Failed to load transactions."
      );
    } finally {
      setLoading(false);
    }
  }, [customerFilter, statusFilter]);

  useEffect(() => {
    let ignore = false;
    getTransactions({
      customer_id: customerFilter.trim() || undefined,
      status: statusFilter.trim() || undefined,
      limit: 50,
    })
      .then((data) => {
        if (!ignore) {
          setTransactions(data.items);
          setTotal(data.total);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!ignore) {
          setError(
            err instanceof Error ? err.message : "Failed to load transactions."
          );
          setLoading(false);
        }
      });
    return () => {
      ignore = true;
    };
  }, [customerFilter, statusFilter, refreshTrigger]);

  const handleInspect = async (transactionId: string) => {
    setInspectLoading(true);
    try {
      const details = await getTransactionById(transactionId);
      setSelectedTxn(details);
    } catch (err) {
      console.error(err);
    } finally {
      setInspectLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case "SUCCESS":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle className="w-3 h-3" />
            <span>SUCCESS</span>
          </span>
        );
      case "FAILED":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <XCircle className="w-3 h-3" />
            <span>FAILED</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Clock className="w-3 h-3" />
            <span>{status}</span>
          </span>
        );
    }
  };

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 shadow-xl space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-sky-400" />
            <h3 className="text-base font-semibold text-zinc-100">
              Transaction Explorer & Ingest Feed
            </h3>
            <span className="px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 text-xs font-mono">
              {total} Total
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-0.5">
            Real-time persistence records and normalized graph entity linkages.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Customer Filter */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-zinc-500" />
            <input
              type="text"
              placeholder="Filter Customer ID..."
              value={customerFilter}
              onChange={(e) => setCustomerFilter(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs focus:outline-none focus:border-sky-500"
          >
            <option value="">All Statuses</option>
            <option value="SUCCESS">SUCCESS</option>
            <option value="FAILED">FAILED</option>
            <option value="PENDING">PENDING</option>
          </select>

          {/* Refresh Button */}
          <button
            onClick={() => fetchTransactionsList()}
            disabled={loading}
            className="p-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs transition-colors cursor-pointer"
            title="Refresh Ingest Feed"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-sky-400" : ""}`} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Transactions Table */}
      <div className="overflow-x-auto rounded-lg border border-zinc-800/80 bg-zinc-950/60">
        <table className="w-full text-left text-xs">
          <thead className="bg-zinc-900/80 border-b border-zinc-800 text-zinc-400 uppercase tracking-wider font-semibold text-[10px]">
            <tr>
              <th className="px-4 py-3">Transaction ID</th>
              <th className="px-4 py-3">Customer</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Payment Instrument</th>
              <th className="px-4 py-3">Device / IP</th>
              <th className="px-4 py-3">Timestamp</th>
              <th className="px-4 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60 text-zinc-300">
            {loading && transactions.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-zinc-500">
                  <div className="flex items-center justify-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin text-sky-400" />
                    <span>Loading real database transactions...</span>
                  </div>
                </td>
              </tr>
            ) : transactions.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-zinc-500">
                  No transactions found in database. Ingest transactions using the form above.
                </td>
              </tr>
            ) : (
              transactions.map((tx) => (
                <tr
                  key={tx.id}
                  className="hover:bg-zinc-900/40 transition-colors"
                >
                  <td className="px-4 py-3 font-mono font-medium text-zinc-200">
                    {tx.transaction_id}
                  </td>
                  <td className="px-4 py-3 font-mono text-zinc-400">
                    {tx.customer_id}
                  </td>
                  <td className="px-4 py-3 font-mono font-semibold text-zinc-100">
                    {tx.amount} <span className="text-[10px] text-zinc-500">{tx.currency}</span>
                  </td>
                  <td className="px-4 py-3">
                    {getStatusBadge(tx.status)}
                  </td>
                  <td className="px-4 py-3 text-zinc-400">
                    {tx.card_bin && tx.card_last4 ? (
                      <span className="font-mono text-[11px]">
                        BIN {tx.card_bin} •••• {tx.card_last4}
                      </span>
                    ) : tx.instrument_token ? (
                      <span className="font-mono text-[11px] truncate max-w-[120px] inline-block">
                        {tx.instrument_token}
                      </span>
                    ) : tx.upi_vpa ? (
                      <span className="text-[11px]">{tx.upi_vpa}</span>
                    ) : (
                      <span className="text-zinc-600 uppercase text-[10px]">{tx.payment_method}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-zinc-400 font-mono text-[11px]">
                    {tx.ip_address || tx.device_id || "—"}
                  </td>
                  <td className="px-4 py-3 text-zinc-500 text-[11px]">
                    {new Date(tx.transacted_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    })}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleInspect(tx.transaction_id)}
                      disabled={inspectLoading}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white text-[11px] font-medium transition-colors cursor-pointer"
                    >
                      <Eye className="w-3 h-3 text-sky-400" />
                      <span>Inspect</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Safe Field Inspector Modal */}
      {selectedTxn && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="relative w-full max-w-2xl rounded-2xl border border-zinc-800 bg-zinc-900 p-6 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-emerald-400" />
                <div>
                  <h4 className="text-base font-semibold text-zinc-100">
                    Safe Transaction Inspector
                  </h4>
                  <p className="text-xs text-zinc-400 font-mono">
                    ID: {selectedTxn.transaction_id}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setSelectedTxn(null)}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Approved Transaction Attributes (Sanitized Grid) */}
            <div className="space-y-3">
              <h5 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Core Transaction Attributes
              </h5>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block">Amount</span>
                  <span className="font-mono font-bold text-zinc-200 text-sm">
                    {selectedTxn.amount} {selectedTxn.currency}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block">Status</span>
                  <div className="mt-1">{getStatusBadge(selectedTxn.status)}</div>
                </div>

                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block">Payment Method</span>
                  <span className="font-mono text-zinc-200 uppercase text-xs">
                    {selectedTxn.payment_method}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block">Customer ID</span>
                  <span className="font-mono text-zinc-200">
                    {selectedTxn.customer_id}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block">Card Mask / BIN</span>
                  <span className="font-mono text-zinc-300">
                    {selectedTxn.card_bin ? `${selectedTxn.card_bin} •••• ${selectedTxn.card_last4 || ""}` : "N/A"}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block">Safe Token</span>
                  <span className="font-mono text-zinc-300 truncate block">
                    {selectedTxn.instrument_token || selectedTxn.upi_vpa || "N/A"}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block">Device ID</span>
                  <span className="font-mono text-zinc-300 truncate block">
                    {selectedTxn.device_id || "N/A"}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block">IP Address</span>
                  <span className="font-mono text-zinc-300">
                    {selectedTxn.ip_address || "N/A"}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block">Geo Location</span>
                  <span className="text-zinc-300">
                    {[selectedTxn.location_city, selectedTxn.location_country].filter(Boolean).join(", ") || "N/A"}
                  </span>
                </div>
              </div>
            </div>

            {/* Normalized Graph Entity Links */}
            <div className="space-y-3 pt-3 border-t border-zinc-800">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-emerald-400" />
                <h5 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                  Normalized Graph Entity Associations ({selectedTxn.entities.length})
                </h5>
              </div>

              <div className="space-y-2">
                {selectedTxn.entities.map((rel, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs"
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                        {rel.entity.entity_type}
                      </span>
                      <span className="font-mono text-zinc-200">
                        {rel.entity.entity_value}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-[11px] text-zinc-400">
                      <span className="text-[10px] text-zinc-500">Rel:</span>
                      <span className="font-mono text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/20">
                        {rel.relationship_type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end pt-3 border-t border-zinc-800">
              <button
                onClick={() => setSelectedTxn(null)}
                className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition-colors cursor-pointer"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
