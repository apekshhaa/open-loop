import { motion } from 'motion/react';
import { useState, useEffect } from 'react';
import { AureumPanel } from './AureumPanel';
import { TerminalLog } from './TerminalLog';
import { Fingerprint, Radar, Target } from 'lucide-react';
import { LogEntry } from '../types';

interface EngineProps {
  agentId: string;
  onComplete: (score: number) => void;
}

export function Engine({ agentId, onComplete }: EngineProps) {
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [currentScore, setCurrentScore] = useState(0);

  const addLog = (message: string, type: LogEntry['type'] = 'info') => {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    setLogs(prev => [...prev, { id: Math.random().toString(), timestamp, message, type }]);
  };

  useEffect(() => {
    const sequence = [
      { delay: 500, msg: `Initiating neural analysis for entity ${agentId}...`, progress: 10 },
      { delay: 1500, msg: "Establishing handshake with validator nodes...", progress: 20 },
      { delay: 2500, msg: "Retrieving cross-chain behavioral footprints...", progress: 35 },
      { delay: 4000, msg: "Identity verification synced. Confidence: 99.8%", type: 'success' as const, progress: 50 },
      { delay: 5500, msg: "Scanning liquidity depth across 12 protocol clusters...", progress: 65 },
      { delay: 7000, msg: "Analyzing risk vectors from historical volatility matrix...", progress: 80, type: 'warning' as const },
      { delay: 8500, msg: "Solvability vectors stabilized. Finalizing score...", progress: 95 },
      { delay: 10000, msg: "Engine calculation complete. Generating verdict.", type: 'success' as const, progress: 100 },
    ];

    sequence.forEach((step, idx) => {
      setTimeout(() => {
        addLog(step.msg, step.type);
        setProgress(step.progress);
        if (idx === sequence.length - 1) {
          setTimeout(() => onComplete(842), 1500); // Prime score
        }
      }, step.delay);
    });

    const scoreInterval = setInterval(() => {
      setCurrentScore(prev => {
        if (prev < 842) return prev + Math.floor(Math.random() * 15);
        return 842;
      });
    }, 100);

    return () => clearInterval(scoreInterval);
  }, []);

  return (
    <div className="pt-12 pb-24 px-4 max-w-6xl mx-auto w-full flex flex-col gap-8">
      <div className="flex justify-between items-end border-b border-gold/20 pb-4">
        <div>
          <h2 className="font-display text-4xl font-bold text-gold glow-gold">Neural Processing Engine</h2>
          <div className="flex items-center gap-2 font-mono text-[10px] text-gold/60 mt-2">
            <motion.div 
              animate={{ backgroundColor: ['#FFD700', 'transparent', '#FFD700'] }}
              className="w-2 h-2 rounded-full" 
            />
            &gt; STATUS: SYNCHRONIZED | PROCESSING_COHORT_A9
          </div>
        </div>
        <div className="font-mono text-[10px] text-gold/30 text-right uppercase tracking-widest hidden sm:block">
          T+0.00ms Latency <br /> Node: OMEGA-7
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Gauges */}
        <div className="lg:col-span-4 flex flex-col gap-8">
          <AureumPanel title="Identity Verification">
            <div className="flex flex-col items-center py-8">
              <div className="relative w-40 h-40 flex items-center justify-center">
                <Fingerprint className="text-gold/20 w-32 h-32 absolute" strokeWidth={1} />
                <motion.div 
                  animate={{ y: [-60, 60, -60] }}
                  transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                  className="absolute w-full h-[2px] bg-gold shadow-[0_0_15px_#ffd700] z-20"
                />
                {/* Decorative Rings */}
                <div className="absolute inset-0 rounded-full border border-gold/20" />
                <div className="absolute inset-[-10px] rounded-full border border-gold/10" />
              </div>
              <div className="mt-8 font-mono text-[10px] text-gold/60 flex justify-between w-full border-t border-gold/10 pt-4 px-4">
                <span>&gt; MATCH: 99.8%</span>
                <span className="text-gold uppercase">Verified</span>
              </div>
            </div>
          </AureumPanel>

          <AureumPanel title="Risk Vector Radar">
            <div className="flex flex-col items-center py-8">
              <div className="relative w-40 h-40 flex items-center justify-center">
                <Radar className="text-gold/20 w-32 h-32 absolute" />
                <div className="absolute inset-0 rounded-full border border-gold/20" />
                <div className="absolute inset-4 rounded-full border border-gold/10" />
                <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gold/10 -translate-x-1/2" />
                <div className="absolute top-1/2 left-0 right-0 h-px bg-gold/10 -translate-y-1/2" />
                
                {/* Scanning sweep */}
                <motion.div 
                  animate={{ rotate: 360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
                  className="absolute inset-0 rounded-full bg-gradient-to-tr from-transparent via-transparent to-gold/20 origin-center"
                />

                {/* Data Points */}
                <div className="absolute top-1/4 left-1/3 w-1.5 h-1.5 bg-gold rounded-full blur-[1px] shadow-[0_0_8px_gold]" />
                <div className="absolute bottom-1/3 right-1/4 w-1 h-1 bg-gold rounded-full opacity-40" />
              </div>
            </div>
          </AureumPanel>
        </div>

        {/* Right Column: Computing Node */}
        <div className="lg:col-span-8 flex flex-col gap-8">
          <AureumPanel className="p-8">
            <div className="flex flex-col md:flex-row items-center gap-12">
              <div className="flex-1">
                <span className="font-display font-bold text-[10px] text-gold/60 uppercase tracking-[0.3em] mb-3 block">Computation Node Alpha</span>
                <h3 className="font-display font-medium text-2xl text-white mb-4">Neural Credit Assessment</h3>
                <p className="font-sans text-xs text-gold/60 leading-relaxed max-w-sm">
                  Analyzing 14,000+ alternative data points via deep temporal networks to establish absolute solvability vectors.
                </p>
                <div className="grid grid-cols-2 gap-8 mt-12">
                  <div className="border-l border-gold/20 pl-4">
                    <span className="block font-mono text-[9px] text-gold/40 uppercase mb-1">Liquidity Depth</span>
                    <span className="font-mono text-xs text-gold">Tier 1 Elite</span>
                  </div>
                  <div className="border-l border-gold/20 pl-4">
                    <span className="block font-mono text-[9px] text-gold/40 uppercase mb-1">Default Prob</span>
                    <span className="font-mono text-xs text-gold">0.0012%</span>
                  </div>
                </div>
              </div>

              {/* Score Gauge */}
              <div className="relative w-56 h-56 flex flex-col items-center justify-center shrink-0">
                <svg className="w-full h-full -rotate-90">
                  <circle
                    cx="112"
                    cy="112"
                    r="90"
                    className="stroke-gold/5 fill-none"
                    strokeWidth="8"
                  />
                  <motion.circle
                    cx="112"
                    cy="112"
                    r="90"
                    stroke="url(#goldGradient)"
                    strokeWidth="8"
                    strokeDasharray={2 * Math.PI * 90}
                    initial={{ strokeDashoffset: 2 * Math.PI * 90 }}
                    animate={{ strokeDashoffset: (2 * Math.PI * 90) * (1 - progress / 100) }}
                    className="fill-none"
                    strokeLinecap="butt"
                  />
                  <defs>
                    <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#FFD700" stopOpacity="0.2" />
                      <stop offset="100%" stopColor="#FFD700" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute flex flex-col items-center">
                  <span className="font-display text-5xl font-black text-gold glow-gold tracking-tight">{currentScore}</span>
                  <span className="font-display text-[10px] font-bold text-gold/60 uppercase tracking-widest mt-1">Prime Sector</span>
                </div>
              </div>
            </div>
          </AureumPanel>

          <TerminalLog logs={logs} className="flex-1" />
        </div>
      </div>
    </div>
  );
}
