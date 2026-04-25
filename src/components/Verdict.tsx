import { motion } from 'motion/react';
import { AureumPanel } from './AureumPanel';
import { Gavel, Bolt, ShieldCheck, TrendingUp, AlertTriangle } from 'lucide-react';
import { AnalysisData } from '../types';

interface VerdictProps {
  data: AnalysisData;
  onExecute: () => void;
  onRetry: () => void;
}

export function Verdict({ data, onExecute, onRetry }: VerdictProps) {
  const isApproved = data.approved;
  
  // Format risk level for display
  const riskLevelDisplay = String(data.riskLevel).toUpperCase();
  const interestRateDisplay = data.interestRate.toFixed(2);
  const confidenceDisplay = (data.confidence * 100).toFixed(1);

  return (
    <div className="pt-24 pb-24 px-4 max-w-5xl mx-auto w-full flex flex-col items-center">
      <motion.div 
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', damping: 15 }}
        className="mb-12 relative"
      >
        <div className={`
          w-24 h-24 rounded-full flex items-center justify-center relative z-10
          ${isApproved ? 'bg-gold/10' : 'bg-red-500/10'}
        `}>
          <div className="absolute inset-0 border border-gold/20 rounded-full animate-[spin_10s_linear_infinite]" />
          <div className="absolute inset-2 border border-gold/40 rounded-full animate-[spin_6s_linear_infinite_reverse]" />
          <Gavel 
            size={40} 
            className={`${isApproved ? 'text-gold' : 'text-red-400'} glow-gold`} 
          />
        </div>
      </motion.div>

      <motion.h1 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className={`
          font-display text-5xl md:text-7xl font-black uppercase tracking-tighter text-center mb-8
          ${isApproved ? 'text-gold glow-gold' : 'text-red-400 text-shadow-red'}
        `}
      >
        Loan {isApproved ? 'Approved' : 'Denied'}
      </motion.h1>

      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="h-px w-64 bg-gradient-to-r from-transparent via-gold/50 to-transparent mb-16" 
      />

      {/* Agent & Request Info */}
      <div className="w-full max-w-4xl mb-12 grid grid-cols-1 md:grid-cols-2 gap-4">
        <AureumPanel title="agent_id">
          <div className="font-mono text-sm text-gold">{data.agentId}</div>
        </AureumPanel>
        <AureumPanel title="amount_requested">
          <div className="font-mono text-lg text-gold">${data.amount.toLocaleString()}</div>
        </AureumPanel>
      </div>

      {/* Main Results */}
      {isApproved ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-4xl mb-16">
          <AureumPanel title="credit_score">
            <div className="flex items-baseline gap-4">
              <span className="font-display text-4xl font-bold text-gold glow-gold">{data.creditScore}</span>
              <span className="font-mono text-xs text-gold/40">/ 100</span>
            </div>
            <p className="font-mono text-[10px] text-gold/40 mt-2">Confidence: {confidenceDisplay}%</p>
          </AureumPanel>

          <AureumPanel title="risk_level">
            <div className="flex items-center gap-3">
              <ShieldCheck className="text-gold" />
              <span className="font-display text-3xl font-bold text-gold tracking-widest">{riskLevelDisplay}</span>
            </div>
          </AureumPanel>

          <AureumPanel title="interest_rate">
            <div className="flex items-baseline gap-4">
              <TrendingUp className="text-gold/60" size={16} />
              <span className="font-display text-4xl font-bold text-white tracking-tight">{interestRateDisplay}%</span>
            </div>
            <p className="font-mono text-[10px] text-gold/40 mt-2">Annual Rate</p>
          </AureumPanel>

          <AureumPanel title="collateral_required">
            <div className="flex items-baseline gap-2">
              <span className="font-display text-4xl font-bold text-white opacity-70">{data.collateral}</span>
              <span className="font-mono text-[10px] text-gold/40 uppercase tracking-widest">Req'd</span>
            </div>
          </AureumPanel>

          <AureumPanel title="monthly_payment">
            <div className="flex items-baseline gap-2">
              <span className="font-display text-3xl font-bold text-gold">${data.monthlyPayment.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              <span className="font-mono text-[10px] text-gold/40 uppercase tracking-widest">per month</span>
            </div>
            <p className="font-mono text-[10px] text-gold/40 mt-2">Total Interest: ${data.totalInterest.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
          </AureumPanel>

          <AureumPanel title="agent_tier">
            <div className="font-display text-2xl font-bold text-gold uppercase tracking-widest">
              {data.agentProfile?.agentTier || 'Unknown'}
            </div>
            {data.agentProfile && (
              <div className="mt-4 grid grid-cols-2 gap-2 text-[10px] font-mono text-gold/60">
                <div>
                  <span className="block text-gold/40">Success Rate</span>
                  <span className="text-gold">{data.agentProfile.successRate.toFixed(1)}%</span>
                </div>
                <div>
                  <span className="block text-gold/40">Transactions</span>
                  <span className="text-gold">{data.agentProfile.transactionCount}</span>
                </div>
              </div>
            )}
          </AureumPanel>
        </div>
      ) : (
        <div className="w-full max-w-2xl mb-16">
          <AureumPanel title="rejection_reason" className="border-red-500/20">
            <div className="flex flex-col gap-6 py-6">
              <div className="flex items-center gap-4 text-red-400">
                <AlertTriangle size={24} />
                <span className="font-display font-black text-xl uppercase tracking-widest">Application Denied</span>
              </div>
              <p className="font-mono text-sm text-red-300 leading-relaxed">
                {data.decisionReason || data.message || "Credit score below approval threshold."}
              </p>
              <div className="mt-4 border-t border-red-500/10 pt-6">
                <div className="bg-red-500/5 p-4 border border-red-500/20 rounded">
                  <div className="font-mono text-[10px] text-gold/60 uppercase mb-2">Score Details</div>
                  <div className="flex justify-between">
                    <span className="text-red-300">Credit Score:</span>
                    <span className="font-display font-bold text-red-400">{data.creditScore}/100</span>
                  </div>
                  <div className="flex justify-between mt-2">
                    <span className="text-red-300">Risk Level:</span>
                    <span className="font-display font-bold text-red-400">{riskLevelDisplay}</span>
                  </div>
                </div>
              </div>
            </div>
          </AureumPanel>
        </div>
      )}

      {/* Decision Reason / Message */}
      <div className="w-full max-w-4xl mb-16 grid grid-cols-1 gap-4">
        <AureumPanel title="decision_reason">
          <p className="font-mono text-sm text-gold/80 leading-relaxed">
            {data.decisionReason}
          </p>
        </AureumPanel>
      </div>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="w-full max-w-md"
      >
        {isApproved ? (
          <button 
            onClick={onExecute}
            className="w-full py-6 flex items-center justify-center gap-4 bg-gold text-void font-display font-black text-lg uppercase tracking-widest hover:bg-gold/90 transition-all shadow-[0_0_30px_rgba(255,215,0,0.4)] hover:shadow-[0_0_50px_rgba(255,215,0,0.6)] group"
          >
            Execute Disbursement
            <Bolt size={20} className="fill-void group-hover:scale-125 transition-transform" />
          </button>
        ) : (
          <button 
            onClick={onRetry}
            className="w-full py-6 flex items-center justify-center gap-4 border border-gold text-gold font-display font-black text-lg uppercase tracking-widest hover:bg-gold/10 transition-all"
          >
            Try Different Parameters
          </button>
        )}
      </motion.div>
    </div>
  );
}
