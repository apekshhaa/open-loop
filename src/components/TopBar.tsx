import { motion } from 'motion/react';
import { Radio, Network, GitBranch, Wallet } from 'lucide-react';
import { WalletState } from '../types';
import { formatAddress } from '../services/wallet';

interface TopBarProps {
  wallet: WalletState;
  onConnectWallet: () => void;
  isConnecting?: boolean;
}

export function TopBar({ wallet, onConnectWallet, isConnecting }: TopBarProps) {
  return (
    <header className="fixed top-0 w-full h-16 border-b border-gold/10 bg-void/80 backdrop-blur-xl z-50 flex justify-between items-center px-8 shadow-[0_0_20px_rgba(255,215,0,0.05)]">
      <div className="font-display font-black text-gold tracking-tighter text-xl">
        AGENTIC BANK
      </div>

      <div className="flex items-center gap-3">
        {/* Status icons */}
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

        {/* Divider */}
        <div className="w-px h-6 bg-gold/10 mx-1" />

        {/* Wallet Button */}
        {wallet.isConnected ? (
          <div className="flex items-center gap-2 px-4 py-2 border border-gold/20 bg-gold/5 group hover:bg-gold/10 transition-all cursor-default">
            {/* Green dot for connected */}
            <motion.div
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]"
            />
            <span className="font-mono text-[11px] text-gold tracking-wide">
              {formatAddress(wallet.address)}
            </span>
            {/* Network badge */}
            {wallet.isCorrectNetwork && (
              <span className="font-mono text-[8px] text-emerald-400/70 uppercase tracking-widest border border-emerald-400/20 px-1.5 py-0.5">
                Sepolia
              </span>
            )}
            {!wallet.isCorrectNetwork && (
              <span className="font-mono text-[8px] text-red-400/70 uppercase tracking-widest border border-red-400/20 px-1.5 py-0.5">
                Wrong Network
              </span>
            )}
          </div>
        ) : (
          <button
            onClick={onConnectWallet}
            disabled={isConnecting}
            className="flex items-center gap-2 px-4 py-2 border border-gold/30 text-gold font-display font-bold text-[10px] uppercase tracking-widest hover:bg-gold/10 hover:border-gold/60 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            <Wallet size={14} className={`${isConnecting ? 'animate-pulse' : 'group-hover:scale-110 transition-transform'}`} />
            {isConnecting ? 'Connecting...' : 'Connect Wallet'}
          </button>
        )}
      </div>
    </header>
  );
}
