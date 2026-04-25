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
        Protocol {isApproved ? 'Approved' : 'Denied'}
      </motion.h1>

      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="h-px w-64 bg-gradient-to-r from-transparent via-gold/50 to-transparent mb-16" 
      />

      {isApproved ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-4xl mb-16">
          <AureumPanel title="query_credit_score">
            <div className="flex items-baseline gap-4">
              <span className="font-display text-4xl font-bold text-gold glow-gold">{data.creditScore}</span>
              <span className="font-mono text-xs text-gold/40">/ 900</span>
            </div>
          </AureumPanel>

          <AureumPanel title="analyze_risk_index">
            <div className="flex items-center gap-3">
              <ShieldCheck className="text-gold" />
              <span className="font-display text-3xl font-bold text-gold tracking-widest">{data.riskLevel}</span>
            </div>
          </AureumPanel>

          <AureumPanel title="calc_interest_rate">
            <div className="flex items-baseline gap-4">
              <TrendingUp className="text-gold/60" size={16} />
              <span className="font-display text-4xl font-bold text-white tracking-tight">{data.interestRate}</span>
            </div>
          </AureumPanel>

          <AureumPanel title="assert_collateral_req">
            <div className="flex items-baseline gap-2">
              <span className="font-display text-4xl font-bold text-white opacity-70">{data.collateral}</span>
              <span className="font-mono text-[10px] text-gold/40 uppercase tracking-widest">USD</span>
            </div>
          </AureumPanel>
        </div>
      ) : (
        <div className="w-full max-w-2xl mb-16">
          <AureumPanel title="rejection_analysis" className="border-red-500/20">
            <div className="flex flex-col gap-6 py-6">
              <div className="flex items-center gap-4 text-red-400">
                <AlertTriangle size={24} />
                <span className="font-display font-black text-xl uppercase tracking-widest">Synchronization Failure</span>
              </div>
              <p className="font-mono text-sm text-gold/60 leading-relaxed">
                {data.rejectionReason || "Entity solvency footprint fails to meet Tier 1 threshold. Collateral ratio requirements for requested allocation exceed current protocol limits."}
              </p>
              <div className="mt-4 border-t border-gold/10 pt-6">
                <span className="block font-display font-bold text-[10px] text-gold/40 uppercase tracking-widest mb-4">Recalibration Protocol</span>
                <div className="bg-gold/5 p-4 border border-gold/10">
                  <span className="block font-mono text-[10px] text-gold/60 uppercase mb-2">Maximum Viable Request</span>
                  <span className="font-display text-3xl font-bold text-gold">$450,000.00</span>
                </div>
              </div>
            </div>
          </AureumPanel>
        </div>
      )}

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
            Adjust Analysis Parameters
          </button>
        )}
      </motion.div>
    </div>
  );
}
