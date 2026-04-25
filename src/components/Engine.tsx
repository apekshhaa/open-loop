import { motion } from 'motion/react';
import { useState, useEffect } from 'react';
import { AureumPanel } from './AureumPanel';
import { TerminalLog } from './TerminalLog';
import { Fingerprint, Radar, Target, AlertCircle } from 'lucide-react';
import { LogEntry, AnalysisData, ApiError } from '../types';
import { requestLoan, simulateAnalysisProgress } from '../services/api';

interface EngineProps {
  agentId: string;
  amount: number;
  onComplete: (data: AnalysisData) => void;
}

export function Engine({ agentId, amount, onComplete }: EngineProps) {
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [currentScore, setCurrentScore] = useState(0);
  const [error, setError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const addLog = (message: string, type: LogEntry['type'] = 'info') => {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    setLogs(prev => [...prev, { id: Math.random().toString(), timestamp, message, type }]);
  };

  useEffect(() => {
    let cleanup: (() => void) | null = null;

    const processLoan = async () => {
      try {
        setIsLoading(true);
        addLog(`Initiating analysis for agent: ${agentId}...`);
        addLog(`Loan amount requested: $${amount.toLocaleString()}`);

        // Simulate visual progress while making actual API call
        cleanup = simulateAnalysisProgress((msg, progressValue, type) => {
          addLog(msg, type);
          setProgress(progressValue);
          
          // Animate score based on progress
          if (progressValue > 0) {
            setCurrentScore(Math.min(100, Math.floor((progressValue / 100) * 90) + 10));
          }
        });

        // Make actual backend API call
        const response = await requestLoan(agentId, amount);

        addLog('Backend analysis complete. Processing response...', 'success');

        // Parse response and create AnalysisData
        const analysisData: AnalysisData = {
          agentId: response.agent_id,
          amount: response.amount_requested,
          creditScore: response.score,
          riskLevel: response.risk_level as any,
          confidence: response.confidence,
          approved: response.approved,
          decisionReason: response.decision_reason,
          interestRate: response.interest_rate,
          collateral: `$${response.collateral_required.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
          collateralRequired: response.collateral_required,
          monthlyPayment: response.monthly_payment,
          totalInterest: response.total_interest,
          message: response.message,
          requestId: response.request_id,
          timestamp: response.timestamp,
          fundsAvailable: response.funds_available,
          agentProfile: response.agent_profile ? {
            successRate: response.agent_profile.success_rate,
            transactionCount: response.agent_profile.transaction_count,
            repaymentHistory: response.agent_profile.repayment_history,
            agentTier: response.agent_profile.agent_tier,
          } : undefined,
          pipelineStatus: response.pipeline_status,
        };

        setCurrentScore(Math.round(response.score));
        setProgress(100);

        addLog(`Credit Score Calculated: ${response.score}`, 'success');
        addLog(`Decision: ${response.approved ? 'APPROVED' : 'REJECTED'}`, response.approved ? 'success' : 'warning');
        addLog(`Risk Level: ${response.risk_level}`, 'info');
        addLog('Verdict ready. Proceeding to decision display...', 'success');

        // Wait a moment before completing to show final progress
        setTimeout(() => {
          onComplete(analysisData);
        }, 1500);

      } catch (err) {
        const apiError = err as ApiError;
        setError(apiError);
        addLog(`ERROR: ${apiError.message}`, 'error');
        addLog('Analysis failed. Please try again.', 'error');
        setIsLoading(false);
      }
    };

    processLoan();

    return () => {
      if (cleanup) cleanup();
    };
  }, [agentId, amount, onComplete]);

  return (
    <div className="pt-12 pb-24 px-4 max-w-6xl mx-auto w-full flex flex-col gap-8">
      {error && (
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border border-red-500/30 rounded-lg p-6 flex items-start gap-4"
        >
          <AlertCircle className="text-red-400 shrink-0 mt-1" size={24} />
          <div>
            <h3 className="font-display font-bold text-red-300 mb-1">Analysis Failed</h3>
            <p className="font-mono text-sm text-red-200">{error.message}</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-red-500/20 border border-red-500/50 text-red-300 rounded hover:bg-red-500/30 transition-all font-mono text-sm"
            >
              Try Again
            </button>
          </div>
        </motion.div>
      )}

      <div className="flex justify-between items-end border-b border-gold/20 pb-4">
        <div>
          <h2 className="font-display text-4xl font-bold text-gold glow-gold">Neural Processing Engine</h2>
          <div className="flex items-center gap-2 font-mono text-[10px] text-gold/60 mt-2">
            <motion.div 
              animate={{ backgroundColor: ['#FFD700', 'transparent', '#FFD700'] }}
              className="w-2 h-2 rounded-full" 
            />
            &gt; STATUS: {isLoading ? 'PROCESSING' : 'COMPLETE'} | ANALYZING_{agentId.toUpperCase().slice(0, 8)}
          </div>
        </div>
        <div className="font-mono text-[10px] text-gold/30 text-right uppercase tracking-widest hidden sm:block">
          Processing Loan Request <br /> Amount: ${amount.toLocaleString()}
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
                  className="absolute w-full h-0.5 bg-gold shadow-[0_0_15px_#ffd700] z-20"
                />
                {/* Decorative Rings */}
                <div className="absolute inset-0 rounded-full border border-gold/20" />
                <div className="absolute -inset-2.5 rounded-full border border-gold/10" />
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
                  className="absolute inset-0 rounded-full bg-linear-to-tr from-transparent via-transparent to-gold/20 origin-center"
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
