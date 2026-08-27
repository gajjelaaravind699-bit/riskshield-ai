import React from "react";
import { ShieldAlert, Terminal, Layers } from "lucide-react";

export const Header: React.FC = () => {
  return (
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold tracking-tight text-zinc-100 text-lg">
                RiskShield AI
              </span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/50">
                Sentinel v0.1.0
              </span>
            </div>
            <p className="text-xs text-zinc-400">
              Abuse-Ring Sentinel & Decision-Support Engine
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono text-zinc-400">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-md bg-zinc-900 border border-zinc-800">
            <Terminal className="w-3.5 h-3.5 text-zinc-400" />
            <span>FastAPI • Next.js • PostgreSQL</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-300">
            <Layers className="w-3.5 h-3.5 text-emerald-400" />
            <span>Decision Support</span>
          </div>
        </div>
      </div>
    </header>
  );
};
