import { motion } from 'motion/react';
import { ArrowRight, BarChart3, Hourglass, Activity } from 'lucide-react';
import { AureumPanel } from './AureumPanel';

interface PortalProps {
  onEnter: () => void;
}

export function Portal({ onEnter }: PortalProps) {
  return (
    <div className="relative min-h-[calc(100vh-4rem)] flex flex-col pt-12 pb-24 overflow-x-hidden">
      {/* Background Cinematic Glows */}
      <div className="absolute top-[10%] left-[10%] w-[500px] h-[500px] bg-gold/5 blur-[150px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[10%] right-[10%] w-[400px] h-[400px] bg-gold-muted/5 blur-[120px] rounded-full pointer-events-none" />

      <motion.section 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 flex flex-col justify-center px-4 max-w-5xl mx-auto w-full mb-12"
      >
        <div className="flex items-center gap-3 mb-8">
          <motion.span 
            animate={{ scale: [1, 1.5, 1], opacity: [0.8, 1, 0.8] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-2 h-2 rounded-full bg-gold shadow-[0_0_12px_rgba(255,215,0,0.8)]" 
          />
          <span className="font-mono text-[10px] text-gold/60 uppercase tracking-[0.3em]">&gt; system_ready :: awaiting_operator</span>
        </div>

        <h1 className="font-display text-5xl md:text-7xl font-bold text-white mb-12 max-w-4xl leading-[1.1] glow-gold tracking-tighter">
          CAPITAL INFRASTRUCTURE FOR <span className="text-gold">AUTONOMOUS ENTITIES.</span>
        </h1>

        <div className="flex items-center gap-8">
          <button 
            onClick={onEnter}
            className="group relative border border-gold bg-gold text-void px-12 py-5 font-display font-black uppercase tracking-[0.3em] text-xs transition-all duration-500 overflow-hidden shadow-[0_0_20px_rgba(255,215,0,0.3)] hover:shadow-[0_0_35px_rgba(255,215,0,0.5)] active:scale-95"
          >
            <div className="absolute inset-0 bg-white/20 -translate-x-full group-hover:translate-x-0 transition-transform duration-500" />
            <span className="relative z-10 flex items-center gap-3">
              Enter Console <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
            </span>
          </button>
          
          <div className="font-mono text-[10px] text-gold/30 tracking-widest hidden sm:block">
            INIT SEQUENCE_V2.0 // EPOCH_LATENCY / 0.00ms
          </div>
        </div>
      </motion.section>

      {/* Modules Preview */}
      <section className="relative z-10 px-4 max-w-5xl mx-auto w-full grid grid-cols-1 md:grid-cols-3 gap-4">
        <AureumPanel title="MOD_01" className="h-full">
          <div className="flex flex-col gap-6">
            <BarChart3 className="text-gold h-8 w-8" />
            <div>
              <h3 className="font-display font-bold text-gold text-lg mb-2">Algorithmic Risk Assessment</h3>
              <p className="text-gold/60 text-xs leading-relaxed font-medium">
                Continuous, multi-dimensional evaluation of asset exposure utilizing deep-learning predictive models to front-run volatility.
              </p>
            </div>
            <div className="font-mono text-[9px] text-gold/40 mt-auto">&gt; STATUS: CALIBRATING...</div>
          </div>
        </AureumPanel>

        <AureumPanel title="MOD_02" className="h-full">
          <div className="flex flex-col gap-6">
            <Hourglass className="text-gold h-8 w-8" />
            <div>
              <h3 className="font-display font-bold text-gold text-lg mb-2">Temporal Escrow</h3>
              <p className="text-gold/60 text-xs leading-relaxed font-medium">
                Programmable liquidity locking mechanisms triggered by cross-chain oracle consensus and deterministic time-locks.
              </p>
            </div>
            <div className="font-mono text-[9px] text-gold/40 mt-auto">&gt; LOCK_STATE: ACTIVE</div>
          </div>
        </AureumPanel>

        <AureumPanel title="MOD_03" className="h-full">
          <div className="flex flex-col gap-6">
            <Activity className="text-gold h-8 w-8" />
            <div>
              <h3 className="font-display font-bold text-gold text-lg mb-2">Neural Credit Scoring</h3>
              <p className="text-gold/60 text-xs leading-relaxed font-medium">
                Real-time solvency analysis derived from decentralized behavioral footprints and cross-protocol historical metrics.
              </p>
            </div>
            <div className="font-mono text-[9px] text-gold/40 mt-auto">&gt; NEURAL_LOAD: OPTIMAL</div>
          </div>
        </AureumPanel>
      </section>
    </div>
  );
}
