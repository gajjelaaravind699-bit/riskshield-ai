"use client";

import React, { useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Server,
  Clock,
  Code2,
} from "lucide-react";
import { getHealthStatus, HealthResponse } from "@/lib/api";

export const HealthStatus: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getHealthStatus(false);
      setHealth(data);
      setLastChecked(new Date());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to connect to backend");
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let ignore = false;
    getHealthStatus(false)
      .then((data) => {
        if (!ignore) {
          setHealth(data);
          setLastChecked(new Date());
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!ignore) {
          setError(err instanceof Error ? err.message : "Failed to connect to backend");
          setHealth(null);
          setLoading(false);
        }
      });
    return () => {
      ignore = true;
    };
  }, []);

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 backdrop-blur-md">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-zinc-800 text-zinc-300">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-zinc-100">
              Backend Health & Readiness Probe
            </h3>
            <p className="text-xs text-zinc-400">
              Live status from FastAPI Sentinel API (/api/v1/health)
            </p>
          </div>
        </div>

        <button
          onClick={fetchHealth}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors disabled:opacity-50"
          title="Refresh health check"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      {loading && !health && !error ? (
        <div className="flex items-center justify-center py-8 text-zinc-400 gap-3">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-400" />
          <span className="text-sm">Connecting to backend gateway...</span>
        </div>
      ) : error ? (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4">
          <div className="flex items-start gap-3">
            <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-200">
                Backend Service Unreachable
              </p>
              <p className="text-xs text-red-300/80 mt-1">{error}</p>
              <p className="text-xs text-zinc-400 mt-2">
                Make sure the FastAPI server is running with{" "}
                <code className="bg-zinc-950 px-1.5 py-0.5 rounded text-zinc-300 font-mono">
                  uvicorn app.main:app --reload --port 8000
                </code>
              </p>
            </div>
          </div>
        </div>
      ) : health ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="rounded-lg bg-zinc-950/60 border border-zinc-800/80 p-3">
              <div className="flex items-center gap-2 text-xs text-zinc-400 mb-1">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Status</span>
              </div>
              <p className="text-sm font-bold text-emerald-400 uppercase tracking-wide">
                {health.status}
              </p>
            </div>

            <div className="rounded-lg bg-zinc-950/60 border border-zinc-800/80 p-3">
              <div className="flex items-center gap-2 text-xs text-zinc-400 mb-1">
                <Server className="w-4 h-4 text-sky-400" />
                <span>Service / Env</span>
              </div>
              <p className="text-sm font-medium text-zinc-200">
                {health.service}{" "}
                <span className="text-xs text-zinc-500 font-mono">({health.environment})</span>
              </p>
            </div>

            <div className="rounded-lg bg-zinc-950/60 border border-zinc-800/80 p-3">
              <div className="flex items-center gap-2 text-xs text-zinc-400 mb-1">
                <Code2 className="w-4 h-4 text-amber-400" />
                <span>Version</span>
              </div>
              <p className="text-sm font-mono text-zinc-200">
                v{health.version}
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-zinc-400 pt-2 border-t border-zinc-800/60">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-zinc-400" />
              <span>Server Timestamp:</span>
              <span className="font-mono text-zinc-300">
                {new Date(health.timestamp).toUTCString()}
              </span>
            </div>
            {lastChecked && (
              <span className="text-[11px] text-zinc-400">
                Last checked: {lastChecked.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};
