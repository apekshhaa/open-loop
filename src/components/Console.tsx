import { motion } from 'motion/react';
import { useState } from 'react';
import { AureumPanel } from './AureumPanel';
import { Bolt } from 'lucide-react';
import { LogEntry } from '../types';

interface ConsoleProps {
  onInitiate: (agentId: string, amount: number) => void;
}

export function Console({ onInitiate }: ConsoleProps) {
  const [agentId, setAgentId] = useState('AGENT-1');
  const [amount, setAmount] = useState('50000');
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="pt-12 pb-24 px-4 max-w-5xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      {/* Left Column: Stats & Context */}
      <div className="lg:col-span-4 flex flex-col gap-8">
        <AureumPanel title="System Uptime">
          <div className="flex flex-col">
            <div className="flex items-baseline gap-2">
              <span className="font-display font-black text-4xl text-gold glow-gold tracking-tight">99.99</span>
              <span className="font-mono text-xs text-gold/60">%</span>
            </div>
            <div className="mt-4 flex items-center gap-2">
              <motion.div 
                animate={{ opacity: [1, 0.4, 1] }}
                className="w-2 h-2 rounded-full bg-gold" 
              />
              <span className="font-mono text-[9px] text-gold/40 uppercase tracking-widest">Core Synchronized</span>
            </div>
          </div>
        </AureumPanel>

        <AureumPanel title="Active Nodes">
          <div className="space-y-4">
            {['Alpha', 'Beta', 'Gamma'].map((node) => (
              <div key={node} className="flex justify-between items-center pb-2 border-b border-gold/5">
                <span className="font-mono text-[10px] text-gold/40 uppercase tracking-widest">NODE_{node.toUpperCase()}</span>
                <span className="font-mono text-[10px] text-gold uppercase tracking-widest">Secure</span>
              </div>
            ))}
          </div>
        </AureumPanel>
      </div>

      {/* Right Column: Console Terminal */}
      <div className="lg:col-span-8">
        <AureumPanel className="min-h-[500px] flex flex-col pt-12">
          <div className="max-w-2xl mx-auto w-full flex flex-col h-full">
            <div className="text-center mb-12">
              <h2 className="font-display font-bold text-2xl text-gold uppercase tracking-widest mb-2">Command Terminal</h2>
              <p className="font-mono text-xs text-gold/40 tracking-widest uppercase">Awaiting agent input parameters</p>
            </div>

            <div className="space-y-12 flex-1">
              {/* Agent ID Input */}
              <div className="space-y-3">
                <label className="font-display font-bold text-[10px] text-gold uppercase tracking-[0.3em] pl-4">Agent ID</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-gold/30 font-mono">&gt;</div>
                  <input 
                    type="text" 
                    value={agentId}
                    onChange={(e) => setAgentId(e.target.value)}
                    className="w-full bg-void/50 border border-gold/20 text-gold font-mono pl-10 pr-4 py-5 focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold/30 transition-all placeholder-gold/20"
                    placeholder="e.g., AGENT-1 or STARTUP-2"
                    disabled={isLoading}
                  />
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 border border-gold/20 border-t-gold rounded-full animate-spin" />
                </div>
              </div>

              {/* Amount Input */}
              <div className="space-y-3">
                <label className="font-display font-bold text-[10px] text-gold uppercase tracking-[0.3em] pl-4">Loan Amount (USD)</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-gold/30 font-mono">$</div>
                  <input 
                    type="number" 
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-full bg-void/50 border border-gold/20 text-gold font-mono pl-10 pr-4 py-5 focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold/30 transition-all text-xl"
                    placeholder="50000"
                    disabled={isLoading}
                  />
                </div>
                <div className="flex justify-between px-4 font-mono text-[9px] text-gold/30 uppercase tracking-widest">
                  <span>Min: $1</span>
                  <span>Max: $10,000,000</span>
                </div>
              </div>
            </div>

            <div className="mt-12 pt-8 border-t border-gold/10">
              <button 
                onClick={() => {
                  const parsedAmount = parseFloat(amount);
                  if (!agentId.trim()) {
                    alert('Please enter an Agent ID');
                    return;
                  }
                  if (isNaN(parsedAmount) || parsedAmount <= 0) {
                    alert('Please enter a valid loan amount');
                    return;
                  }
                  setIsLoading(true);
                  onInitiate(agentId, parsedAmount);
                }}
                disabled={isLoading}
                className="w-full py-6 flex items-center justify-center gap-4 bg-gold text-void font-display font-black text-lg uppercase tracking-widest hover:bg-gold/90 transition-all shadow-[0_0_25px_rgba(255,215,0,0.3)] hover:shadow-[0_0_40px_rgba(255,215,0,0.5)] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Bolt size={20} className={`fill-void ${isLoading ? 'animate-spin' : ''}`} />
                {isLoading ? 'Analyzing...' : 'Initiate Analysis'}
              </button>
            </div>
          </div>
        </AureumPanel>
      </div>
    </div>
  );
}
