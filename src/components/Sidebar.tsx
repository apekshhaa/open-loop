import { motion } from 'motion/react';
import { AppScreen } from '../types';
import { 
  LayoutGrid, 
  Terminal, 
  Cpu, 
  Gavel, 
  Wallet,
  Activity,
  Power
} from 'lucide-react';

interface SidebarProps {
  currentScreen: AppScreen;
  setScreen: (screen: AppScreen) => void;
}

export function Sidebar({ currentScreen, setScreen }: SidebarProps) {
  const menuItems = [
    { id: 'portal', label: 'Portal', icon: LayoutGrid },
    { id: 'console', label: 'Console', icon: Terminal },
    { id: 'engine', label: 'Engine', icon: Cpu },
    { id: 'verdict', label: 'Verdict', icon: Gavel },
    { id: 'ledger', label: 'Ledger', icon: Wallet },
  ] as const;

  return (
    <nav className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 border-r border-gold/10 bg-void/90 backdrop-blur-2xl z-40 hidden md:flex flex-col pt-8 pb-8">
      <div className="px-6 mb-8">
        <div className="font-display text-lg font-bold text-gold tracking-wider uppercase mb-1">System Operator</div>
        <div className="flex items-center gap-2 text-[10px] font-display font-bold tracking-widest text-gold/60 uppercase">
          <motion.span 
            animate={{ opacity: [1, 0.4, 1] }} 
            transition={{ duration: 2, repeat: Infinity }}
            className="w-2 h-2 rounded-full bg-gold shadow-[0_0_8px_rgba(255,215,0,0.8)]" 
          />
          Synchronized
        </div>
      </div>

      <div className="flex-1 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentScreen === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => setScreen(item.id)}
              className={`
                w-full flex items-center gap-4 px-6 py-4 transition-all duration-300 group relative
                ${isActive ? 'text-gold bg-gold/10' : 'text-gold/40 hover:bg-gold/5 hover:text-gold/80'}
              `}
            >
              {isActive && (
                <motion.div 
                  layoutId="active-indicator"
                  className="absolute left-0 top-0 bottom-0 w-1 bg-gold shadow-[0_0_10px_rgba(255,215,0,0.5)]" 
                />
              )}
              <Icon size={18} />
              <span className="font-display uppercase tracking-[0.2em] text-[10px] font-bold">{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="mt-auto space-y-1 pt-4 border-t border-gold/5">
        <button className="w-full flex items-center gap-4 px-6 py-4 text-gold/40 hover:text-gold transition-all group">
          <Activity size={18} />
          <span className="font-display uppercase tracking-[0.2em] text-[10px] font-bold">Diagnostics</span>
        </button>
        <button className="w-full flex items-center gap-4 px-6 py-4 text-gold/40 hover:text-gold transition-all group">
          <Power size={18} />
          <span className="font-display uppercase tracking-[0.2em] text-[10px] font-bold">Log Out</span>
        </button>
      </div>
    </nav>
  );
}
