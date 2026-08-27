"use client";

import { useState } from "react";
import {
  createTransaction,
  TransactionCreateInput,
  TransactionRead,
} from "@/lib/api";
import {
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  PlusCircle,
  CreditCard,
  Smartphone,
  Globe,
  Loader2,
  Lock,
} from "lucide-react";

interface TransactionIngestFormProps {
  onTransactionIngested?: (transaction: TransactionRead) => void;
}

export function TransactionIngestForm({
  onTransactionIngested,
}: TransactionIngestFormProps) {
  const [formData, setFormData] = useState<TransactionCreateInput>({
    transaction_id: "",
    customer_id: "",
    amount: "",
    currency: "USD",
    status: "SUCCESS",
    payment_method: "card",
    card_bin: "",
    card_last4: "",
    instrument_token: "",
    upi_vpa: "",
    device_id: "",
    ip_address: "",
    user_agent: "",
    location_city: "",
    location_country: "",
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMessage(null);
    setErrorMessage(null);

    try {
      // Clean up optional fields
      const payload: TransactionCreateInput = {
        transaction_id: formData.transaction_id.trim(),
        customer_id: formData.customer_id.trim(),
        amount: formData.amount.trim(),
        currency: formData.currency?.trim() || "USD",
        status: formData.status || "SUCCESS",
        payment_method: formData.payment_method.trim(),
      };

      if (formData.card_bin?.trim()) payload.card_bin = formData.card_bin.trim();
      if (formData.card_last4?.trim()) payload.card_last4 = formData.card_last4.trim();
      if (formData.instrument_token?.trim())
        payload.instrument_token = formData.instrument_token.trim();
      if (formData.upi_vpa?.trim()) payload.upi_vpa = formData.upi_vpa.trim();
      if (formData.device_id?.trim()) payload.device_id = formData.device_id.trim();
      if (formData.ip_address?.trim()) payload.ip_address = formData.ip_address.trim();
      if (formData.user_agent?.trim()) payload.user_agent = formData.user_agent.trim();
      if (formData.location_city?.trim())
        payload.location_city = formData.location_city.trim();
      if (formData.location_country?.trim())
        payload.location_country = formData.location_country.trim();

      const created = await createTransaction(payload);
      setSuccessMessage(
        `Transaction '${created.transaction_id}' ingested successfully with ${created.entities.length} normalized entity links.`
      );

      // Reset form
      setFormData({
        transaction_id: "",
        customer_id: "",
        amount: "",
        currency: "USD",
        status: "SUCCESS",
        payment_method: "card",
        card_bin: "",
        card_last4: "",
        instrument_token: "",
        upi_vpa: "",
        device_id: "",
        ip_address: "",
        user_agent: "",
        location_city: "",
        location_country: "",
      });

      if (onTransactionIngested) {
        onTransactionIngested(created);
      }
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error ? err.message : "An unexpected error occurred."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <PlusCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-zinc-100">
              Ingest Payment Transaction
            </h3>
            <p className="text-xs text-zinc-400">
              Submit raw payment event with zero-trust tokenization and normalized entity extraction.
            </p>
          </div>
        </div>

        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-zinc-800/80 border border-zinc-700/50 text-zinc-400 text-[11px]">
          <Lock className="w-3 h-3 text-emerald-400" />
          <span>Zero-Trust Safe Ingestion</span>
        </div>
      </div>

      {successMessage && (
        <div className="flex items-start gap-2.5 p-3.5 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <span>{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-start gap-2.5 p-3.5 rounded-lg bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <span>{errorMessage}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Core Transaction Fields */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="space-y-1.5">
            <label
              htmlFor="transaction_id"
              className="text-xs font-medium text-zinc-300 flex items-center gap-1"
            >
              <span>Transaction ID</span>
              <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              id="transaction_id"
              name="transaction_id"
              required
              placeholder="e.g. txn_1001"
              value={formData.transaction_id}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
            />
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="customer_id"
              className="text-xs font-medium text-zinc-300 flex items-center gap-1"
            >
              <span>Customer ID</span>
              <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              id="customer_id"
              name="customer_id"
              required
              placeholder="e.g. cust_8921"
              value={formData.customer_id}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
            />
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="amount"
              className="text-xs font-medium text-zinc-300 flex items-center gap-1"
            >
              <span>Amount (Decimal)</span>
              <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              id="amount"
              name="amount"
              required
              placeholder="e.g. 149.99"
              value={formData.amount}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1.5">
              <label
                htmlFor="currency"
                className="text-xs font-medium text-zinc-300"
              >
                Currency
              </label>
              <input
                type="text"
                id="currency"
                name="currency"
                maxLength={3}
                value={formData.currency}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs uppercase focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <label
                htmlFor="status"
                className="text-xs font-medium text-zinc-300"
              >
                Status
              </label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
                className="w-full px-2 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              >
                <option value="SUCCESS">SUCCESS</option>
                <option value="FAILED">FAILED</option>
                <option value="PENDING">PENDING</option>
              </select>
            </div>
          </div>
        </div>

        {/* Safe Payment Instrument Details */}
        <div className="space-y-3 pt-2 border-t border-zinc-800/80">
          <div className="flex items-center gap-2 text-xs font-semibold text-zinc-300">
            <CreditCard className="w-4 h-4 text-sky-400" />
            <span>Safe Payment Instrument Signals (Tokens & References Only)</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-1.5">
              <label
                htmlFor="payment_method"
                className="text-xs font-medium text-zinc-300"
              >
                Payment Method
              </label>
              <select
                id="payment_method"
                name="payment_method"
                value={formData.payment_method}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              >
                <option value="card">Credit / Debit Card</option>
                <option value="upi">UPI</option>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="wallet">Digital Wallet</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label
                htmlFor="card_bin"
                className="text-xs font-medium text-zinc-300"
              >
                Card BIN (First 6-8 digits)
              </label>
              <input
                type="text"
                id="card_bin"
                name="card_bin"
                maxLength={8}
                placeholder="e.g. 411111"
                value={formData.card_bin}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <label
                htmlFor="card_last4"
                className="text-xs font-medium text-zinc-300"
              >
                Card Last 4
              </label>
              <input
                type="text"
                id="card_last4"
                name="card_last4"
                maxLength={4}
                placeholder="e.g. 1111"
                value={formData.card_last4}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <label
                htmlFor="instrument_token"
                className="text-xs font-medium text-zinc-300"
              >
                Instrument Token / Safe Fingerprint
              </label>
              <input
                type="text"
                id="instrument_token"
                name="instrument_token"
                placeholder="e.g. tok_card_fp_9a8b"
                value={formData.instrument_token}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <label
                htmlFor="upi_vpa"
                className="text-xs font-medium text-zinc-300"
              >
                UPI VPA (if UPI)
              </label>
              <input
                type="text"
                id="upi_vpa"
                name="upi_vpa"
                placeholder="e.g. user@okhdfcbank"
                value={formData.upi_vpa}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>
          </div>
        </div>

        {/* Device & Network Origin Signals */}
        <div className="space-y-3 pt-2 border-t border-zinc-800/80">
          <div className="flex items-center gap-2 text-xs font-semibold text-zinc-300">
            <Smartphone className="w-4 h-4 text-amber-400" />
            <span>Device & Network Origin Signals</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-1.5">
              <label
                htmlFor="device_id"
                className="text-xs font-medium text-zinc-300"
              >
                Device ID / Fingerprint
              </label>
              <input
                type="text"
                id="device_id"
                name="device_id"
                placeholder="e.g. dev_fp_8819a"
                value={formData.device_id}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <label
                htmlFor="ip_address"
                className="text-xs font-medium text-zinc-300"
              >
                IP Address
              </label>
              <input
                type="text"
                id="ip_address"
                name="ip_address"
                placeholder="e.g. 198.51.100.42"
                value={formData.ip_address}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <label
                htmlFor="location_city"
                className="text-xs font-medium text-zinc-300"
              >
                City
              </label>
              <input
                type="text"
                id="location_city"
                name="location_city"
                placeholder="e.g. San Francisco"
                value={formData.location_city}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <label
                htmlFor="location_country"
                className="text-xs font-medium text-zinc-300"
              >
                Country Code
              </label>
              <input
                type="text"
                id="location_country"
                name="location_country"
                placeholder="e.g. US"
                value={formData.location_country}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 placeholder-zinc-600 text-xs focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-zinc-950 font-semibold text-xs transition-all shadow-lg shadow-emerald-950/50 cursor-pointer"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Ingesting Transaction...</span>
              </>
            ) : (
              <>
                <span>Submit & Ingest Transaction</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
