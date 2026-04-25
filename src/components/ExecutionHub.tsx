import { motion, AnimatePresence } from 'motion/react';
import { useState, useEffect } from 'react';
import { AureumPanel } from './AureumPanel';
import { TerminalLog } from './TerminalLog';
import { Check, Wallet, FileKey, Share2, Server, Milestone, Copy } from 'lucide-react';
import { LogEntry } from '../types';

interface ExecutionHubProps {
  onFinish: () => void;
}

export function ExecutionHub({ onFinish }: ExecutionHubProps) {
  const [step, setStep] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isSuccess, setIsSuccess] = useState(false);

  const addLog = (message: string, type: LogEntry['type'] = 'info') => {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    setLogs(prev => [...prev, { id: Math.random().toString(), timestamp, message, type }]);
  };

  const steps = [
    { title: 'Connecting Wallet', icon: Wallet, detail: 'ADDR: 0x71C...A2' },
    { title: 'Signing Transaction', icon: FileKey, detail: 'SIG: VERIFIED_OK' },
    { title: 'Broadcasting to Network', icon: Share2, detail: 'NODES: 128 REACHED' },
    { title: 'Confirming on Chain', icon: Server, detail: 'STATUS: FINALIZED' },
  ];

  useEffect(() => {
    const sequence = [
      { delay: 500, step: 1, msg: "INIT PROTOCOL: TX_EXECUTION" },
      { delay: 1500, step: 1, msg: "HANDSHAKE ESTABLISHED WITH WALLET 0x71C...A2", type: 'success' as const },
      { delay: 2500, step: 2, msg: "REQUESTING CRYPTOGRAPHIC SIGNATURE..." },
      { delay: 4000, step: 2, msg: "SIGNATURE RECEIVED. VALIDATING PROOF...", type: 'success' as const },
      { delay: 5500, step: 3, msg: "COMPILING PAYLOAD. BROADCASTING TO RPC_NODES..." },
      { delay: 7000, step: 3, msg: "MEMPOOL ACCEPTANCE CONFIRMED. AWAITING BLOCK...", type: 'warning' as const },
      { delay: 8500, step: 4, msg: "BLOCK 18492011 MINED. TX INCLUDED.", type: 'success' as const },
      { delay: 10000, step: 4, msg: "EXECUTION COMPLETE. STATUS: SUCCESS.", type: 'success' as const },
    ];

    sequence.forEach((s) => {
      setTimeout(() => {
        setStep(s.step);
        addLog(s.msg, s.type);
        if (s.delay === 10000) setIsSuccess(true);
      }, s.delay);
    });
  }, []);

  return (
    <div className="pt-12 pb-24 px-4 max-w-6xl mx-auto w-full flex flex-col gap-8">
      <div className="flex justify-between items-end border-b border-gold/20 pb-4">
        <div>
          <h1 className="font-display text-4xl font-bold text-gold uppercase tracking-tighter">Transaction Execution Hub</h1>
          <p className="font-mono text-[10px] text-gold/60 mt-2 tracking-widest uppercase">&gt; Initializing protocol_x99</p>
        </div>
        <div className="text-right">
          <div className="font-display font-medium text-[9px] text-gold/40 mb-1 uppercase tracking-[0.2em]">Execution ID</div>
          <div className="font-mono text-sm text-gold">TX-9982-ALPHA</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Sequence List */}
        <div className="lg:col-span-4 flex flex-col gap-8">
          <AureumPanel title="Execution Sequence" className="flex-1">
            <div className="space-y-8 relative py-4">
              <div className="absolute left-[11px] top-8 bottom-8 w-px bg-gold/10" />
              
              {steps.map((s, idx) => {
                const isActive = step === idx + 1;
                const isCompleted = step > idx + 1;
                const Icon = s.icon;

                return (
                  <div key={idx} className="flex gap-6 relative z-10">
                    <div className={`
                      w-6 h-6 rounded-full flex items-center justify-center shrink-0 border transition-all duration-500
                      ${isCompleted ? 'bg-gold border-gold' : isActive ? 'bg-gold/20 border-gold shadow-[0_0_10px_gold]' : 'bg-void border-gold/20'}
                    `}>
                      {isCompleted ? <Check size={12} className="text-void" strokeWidth={3} /> : <Icon size={12} className={isActive ? 'text-gold' : 'text-gold/20'} />}
                    </div>
                    <div>
                      <div className={`font-mono text-xs transition-opacity duration-500 ${isActive ? 'text-gold font-bold' : isCompleted ? 'text-gold/80' : 'text-gold/20'}`}>
                        {idx + 1}. {s.title}
                      </div>
                      <div className={`font-mono text-[9px] mt-1 transition-opacity duration-500 ${isActive ? 'text-gold/60' : 'text-gold/20'}`}>
                        {s.detail}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </AureumPanel>

          <AureumPanel title="Network metrics">
            <div className="grid grid-cols-2 gap-4">
              <div className="border border-gold/10 p-4">
                <div className="font-display font-bold text-[8px] text-gold/40 mb-1 uppercase tracking-widest">Latency</div>
                <div className="font-mono text-sm text-white">12ms</div>
              </div>
              <div className="border border-gold/10 p-4">
                <div className="font-display font-bold text-[8px] text-gold/40 mb-1 uppercase tracking-widest">Block Height</div>
                <div className="font-mono text-sm text-white">18,492,011</div>
              </div>
              <div className="border border-gold/10 p-4 col-span-2">
                <div className="font-display font-bold text-[8px] text-gold/40 mb-1 uppercase tracking-widest">Gas Used</div>
                <div className="font-mono text-sm text-white">0.0014 GWEI</div>
              </div>
            </div>
          </AureumPanel>
        </div>

        {/* Right: Stage & Logs */}
        <div className="lg:col-span-8 flex flex-col gap-8">
          <div className="relative glass-panel rounded-none p-12 flex-1 flex flex-col items-center justify-center text-center overflow-hidden">
            {/* Corner brackets */}
            <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-gold" />
            <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-gold" />
            <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-gold" />
            <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-gold" />
            
            <AnimatePresence mode="wait">
              {!isSuccess ? (
                <motion.div 
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col items-center"
                >
                  <div className="relative w-24 h-24 mb-8">
                    <motion.div 
                      animate={{ rotate: 360 }}
                      transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                      className="absolute inset-0 border-2 border-gold/20 border-t-gold rounded-full" 
                    />
                    <div className="absolute inset-4 border border-gold/40 rounded-full animate-pulse" />
                    <Milestone className="absolute inset-0 m-auto text-gold/40 h-8 w-8" />
                  </div>
                  <h2 className="font-display font-black text-3xl text-gold uppercase tracking-tighter animate-pulse mb-2">Executing...</h2>
                  <p className="font-mono text-xs text-gold/40 tracking-widest uppercase">System Broadcast in Progress</p>
                </motion.div>
              ) : (
                <motion.div 
                  key="success"
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="flex flex-col items-center max-w-md"
                >
                  <div className="relative w-32 h-32 mb-8">
                    <div className="absolute inset-0 bg-gold/10 blur-3xl opacity-50 rounded-full" />
                    <motion.div 
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: 1 }}
                      className="w-full h-full flex items-center justify-center"
                    >
                       <Check size={80} className="text-gold glow-gold" strokeWidth={3} />
                    </motion.div>
                  </div>
                  <h2 className="font-display font-black text-6xl text-gold glow-gold uppercase mb-6 tracking-tighter">Success</h2>
                  <p className="font-mono text-xs text-gold/60 mb-8 leading-relaxed">
                    TRANSACTION EXECUTED AND CONFIRMED ON MAINNET. FUNDS SECURED IN COLD STORAGE VAULT.
                  </p>
                  
                  <div className="bg-gold/5 border border-gold/20 p-4 mb-12 w-full group transition-all hover:bg-gold/10">
                    <span className="block font-display font-bold text-[8px] text-gold/40 uppercase tracking-[0.2em] mb-2 text-center">Transaction Hash</span>
                    <div className="flex items-center justify-center gap-3 font-mono text-gold selection:bg-gold/30">
                      0xA3F992B1...77D9B2
                      <Copy size={14} className="cursor-pointer hover:text-white transition-colors" />
                    </div>
                  </div>

                  <div className="flex gap-4 w-full">
                    <button 
                      onClick={() => onFinish()}
                      className="flex-1 py-4 border border-gold text-gold font-display font-black text-[10px] uppercase tracking-widest hover:bg-gold/10 transition-all"
                    >
                      View Ledger
                    </button>
                    <button className="flex-1 py-4 bg-gold text-void font-display font-black text-[10px] uppercase tracking-widest hover:bg-gold/90 transition-all shadow-[0_0_20px_rgba(255,215,0,0.3)]">
                      New Execution
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <TerminalLog logs={logs} maxHeight="10rem" />
        </div>
      </div>
    </div>
  );
}
