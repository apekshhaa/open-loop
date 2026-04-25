import { motion } from 'motion/react';
import { AureumPanel } from './AureumPanel';
import { LineChart, FileText, Search, Download, ChevronLeft, ChevronRight } from 'lucide-react';

export function Ledger() {
  const transactions = [
    { id: '1', ts: '2023-10-27 14:32:01', type: 'LOAN_DISBURSEMENT', hash: '0x8fB3...e9A1', delta: '+ 142,850.00', status: 'VERIFIED' },
    { id: '2', ts: '2023-10-27 14:30:45', type: 'CONTRACT_EXECUTED', hash: '0x3aC1...7bF2', delta: '--', status: 'CONFIRMED' },
    { id: '3', ts: '2023-10-27 14:28:12', type: 'IDENTITY_VERIFIED', hash: '0x1dQ5...0cP8', delta: '--', status: 'CONFIRMED' },
    { id: '4', ts: '2023-10-27 10:15:33', type: 'INCOMING_WIRE', hash: '0x9vN4...2mK5', delta: '+ 500,000.00', status: 'SETTLED' },
    { id: '5', ts: '2023-10-26 18:45:00', type: 'FEE_DEDUCTION', hash: '0x4xL9...1jH3', delta: '- 150.00', status: 'SETTLED' },
    { id: '6', ts: '2023-10-26 09:12:44', type: 'NODE_SYNC', hash: '0x7gT2...8rE6', delta: '--', status: 'ROUTINE' },
  ];

  return (
    <div className="pt-12 pb-24 px-4 max-w-6xl mx-auto w-full flex flex-col gap-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-gold/10 pb-6">
        <div>
          <h1 className="font-display text-4xl md:text-5xl font-bold text-gold glow-gold tracking-tight uppercase">Immutable Activity Ledger</h1>
          <p className="font-mono text-[10px] text-gold/40 mt-3 tracking-widest uppercase flex items-center gap-2">
            <Search size={12} />
            System Event Log // Real-Time Synchronization
          </p>
        </div>
        <div className="mt-6 md:mt-0 flex gap-4">
          <button className="px-6 py-2 border border-gold/20 text-gold/60 font-display font-bold text-[10px] uppercase tracking-widest hover:bg-gold/5 transition-all">
            Export Log
          </button>
          <button className="px-6 py-2 bg-gold text-void font-display font-black text-[10px] uppercase tracking-widest hover:bg-gold/90 transition-all shadow-[0_0_15px_rgba(255,215,0,0.2)]">
            Query Ledger
          </button>
        </div>
      </div>

      {/* Simulator Bento Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Main Chart Panel */}
        <AureumPanel className="lg:col-span-8 p-0" showScanlines={false}>
          <div className="p-8">
            <div className="flex justify-between items-start mb-12">
              <div>
                <span className="block font-mono text-[10px] text-gold/40 uppercase mb-2">&gt; net_profit_ytd</span>
                <div className="font-display font-black text-6xl text-gold tracking-tighter glow-gold">
                  $142,850<span className="text-2xl text-gold/60">.00</span>
                </div>
                <p className="font-mono text-[9px] text-gold/30 mt-3 tracking-widest uppercase">Currency: USDC // Network: Ethereum_Mainnet</p>
              </div>
              <div className="flex flex-col items-end gap-3">
                <div className="bg-green-500/10 border border-green-500/20 px-3 py-1 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                  <span className="font-mono text-[10px] text-green-400 font-bold tracking-widest">+14.2% APY</span>
                </div>
                <div className="font-mono text-[9px] text-gold/30 text-right space-y-1">
                  <div>LAST_SYNC: 14:02:44:009Z</div>
                  <div>MODEL: PRED_V3_ALPHA</div>
                </div>
              </div>
            </div>

            {/* SVG Graph */}
            <div className="h-64 w-full relative border-l border-b border-gold/5 pl-2 pb-2 mt-8">
              <svg className="w-full h-full" viewBox="0 0 1000 300" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="chartGradient" x1="0" y1="1" x2="0" y2="0">
                    <stop offset="0%" stopColor="#FFD700" stopOpacity="0" />
                    <stop offset="100%" stopColor="#FFD700" stopOpacity="0.1" />
                  </linearGradient>
                  <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#8B6914" />
                    <stop offset="50%" stopColor="#FFD700" />
                    <stop offset="100%" stopColor="#FFEA70" />
                  </linearGradient>
                </defs>
                
                {/* Horizontal Grid */}
                {[0, 75, 150, 225].map((y) => (
                  <line key={y} x1="0" y1={y} x2="1000" y2={y} stroke="rgba(255,215,0,0.03)" strokeWidth="1" />
                ))}

                {/* The Curve */}
                <motion.path
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 2 }}
                  d="M0,230 Q100,210 200,225 T400,165 T600,120 T800,90 T1000,50"
                  fill="transparent"
                  stroke="url(#lineGradient)"
                  strokeWidth="3"
                  filter="drop-shadow(0 0 8px gold)"
                />
                <motion.path
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1, duration: 1 }}
                  d="M0,230 Q100,210 200,225 T400,165 T600,120 T800,90 T1000,50 V300 H0 Z"
                  fill="url(#chartGradient)"
                />
                
                {/* Active Dot */}
                <motion.circle 
                  cx="850" cy="80" r="4" fill="#FFD700" 
                  animate={{ opacity: [1, 0.4, 1] }} 
                  transition={{ duration: 1.5, repeat: Infinity }} 
                />
              </svg>
              
              <div className="absolute bottom-0 left-0 right-0 flex justify-between font-mono text-[9px] text-gold/30 mt-4 px-2 uppercase tracking-[0.2em]">
                <span>Q1</span>
                <span>Q2</span>
                <span>Q3</span>
                <span className="text-gold">Now</span>
              </div>
            </div>
          </div>
        </AureumPanel>

        {/* Metric Cards */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <AureumPanel className="flex-1 group">
             <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-gold-muted to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
             <p className="font-mono text-[10px] text-gold/40 mb-4 tracking-widest uppercase">&gt; yield_velocity</p>
             <div className="flex items-end gap-3 mb-4">
               <span className="font-display font-medium text-3xl text-gold">4.28</span>
               <span className="font-mono text-[10px] text-gold/40 mb-1 uppercase">usdc / min</span>
             </div>
             <div className="w-full h-1 bg-gold/5 rounded-full overflow-hidden">
               <motion.div 
                 initial={{ width: 0 }}
                 animate={{ width: '78%' }}
                 transition={{ duration: 1.5 }}
                 className="h-full bg-gold"
               />
             </div>
          </AureumPanel>

          <AureumPanel className="flex-1 group">
             <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-gold-muted to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
             <p className="font-mono text-[10px] text-gold/40 mb-4 tracking-widest uppercase">&gt; risk_exposure</p>
             <div className="flex items-end gap-3 mb-4">
               <span className="font-display font-medium text-3xl text-gold">LOW</span>
               <span className="font-mono text-[10px] text-gold/40 mb-1 uppercase">index: 0.12</span>
             </div>
             <div className="grid grid-cols-4 gap-1 mt-4">
               <div className="h-1.5 bg-gold" />
               <div className="h-1.5 bg-gold/10" />
               <div className="h-1.5 bg-gold/5" />
               <div className="h-1.5 bg-gold/5" />
             </div>
          </AureumPanel>
        </div>
      </div>

      {/* Activity Table */}
      <AureumPanel title="System activity list" className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse whitespace-nowrap">
            <thead>
              <tr className="border-b border-gold/10 font-display font-bold text-[10px] text-gold/40 uppercase tracking-[0.2em] bg-white/5">
                <th className="p-5 font-normal">&gt; timestamp</th>
                <th className="p-5 font-normal">&gt; event type</th>
                <th className="p-5 font-normal">&gt; hash</th>
                <th className="p-5 font-normal text-right">&gt; delta</th>
                <th className="p-5 font-normal text-center w-32">&gt; status</th>
              </tr>
            </thead>
            <tbody className="font-mono text-[11px] text-gold/70">
              {transactions.map((tx) => (
                <tr key={tx.id} className="border-b border-gold/5 hover:bg-gold/5 transition-colors group">
                  <td className="p-5 text-gold/40">{tx.ts}</td>
                  <td className="p-5 text-gold font-bold">{tx.type}</td>
                  <td className="p-5 text-gold/20 group-hover:text-gold/40 transition-colors uppercase">{tx.hash}</td>
                  <td className={`p-5 text-right font-bold ${tx.delta.includes('+') ? 'text-gold' : tx.delta === '--' ? 'text-gold/20' : 'text-red-400'}`}>
                    {tx.delta}
                  </td>
                  <td className="p-5 text-center">
                    <span className="inline-flex px-2 py-0.5 border border-gold/30 text-[9px] uppercase tracking-tighter">
                      {tx.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="p-4 flex justify-between items-center border-t border-gold/10 bg-void/30">
          <div className="font-mono text-[10px] text-gold/30 uppercase tracking-widest">Showing 1-6 of 1,024 Records</div>
          <div className="flex gap-2">
            <button className="p-1 border border-gold/20 text-gold/40 hover:text-gold transition-colors">
              <ChevronLeft size={16} />
            </button>
            {[1, 2, 3].map(n => (
              <button key={n} className={`w-6 h-6 flex items-center justify-center font-mono text-[10px] border border-gold/20 hover:border-gold transition-colors ${n === 1 ? 'bg-gold/10 text-gold' : 'text-gold/40'}`}>
                {n}
              </button>
            ))}
            <button className="p-1 border border-gold/20 text-gold/40 hover:text-gold transition-colors">
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </AureumPanel>
    </div>
  );
}
