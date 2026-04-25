import { motion } from 'motion/react';
import { Radio, Network, GitBranch } from 'lucide-react';

export function TopBar() {
  return (
    <header className="fixed top-0 w-full h-16 border-b border-gold/10 bg-void/80 backdrop-blur-xl z-50 flex justify-between items-center px-8 shadow-[0_0_20px_rgba(255,215,0,0.05)]">
      <div className="font-display font-black text-gold tracking-tighter text-xl">
        AGENTIC BANK
      </div>

      <div className="flex gap-2">
        {[
          { icon: Radio, label: 'Sensors' },
          { icon: Network, label: 'Network' },
          { icon: GitBranch, label: 'Nodes' }
        ].map((item, idx) => {
          const Icon = item.icon;
          return (
            <button 
              key={idx}
              className="text-gold/40 hover:text-gold hover:bg-gold/5 transition-all p-2 rounded relative group"
            >
              <Icon size={18} />
              <div className="absolute top-full right-0 mt-2 px-2 py-1 bg-void border border-gold/20 text-[8px] font-display uppercase tracking-widest text-gold opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                {item.label} :: OK
              </div>
            </button>
          );
        })}
      </div>
    </header>
  );
}
