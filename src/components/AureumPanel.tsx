import { motion } from 'motion/react';
import { ReactNode } from 'react';

interface AureumPanelProps {
  children: ReactNode;
  className?: string;
  title?: string;
  showScanlines?: boolean;
}

export function AureumPanel({ children, className = '', title, showScanlines = true }: AureumPanelProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative glass-panel p-6 overflow-hidden ${className}`}
    >
      {/* Corner Brackets */}
      <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-gold/50" />
      <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-gold/50" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-gold/50" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-gold/50" />

      {/* Scanline Overlay */}
      {showScanlines && <div className="absolute inset-0 scanline pointer-events-none mix-blend-overlay opacity-30" />}

      {/* Decorative Title/Module Tag */}
      {title && (
        <div className="flex justify-between items-center mb-6 border-b border-gold/10 pb-2 relative z-10">
          <span className="font-display font-bold text-[10px] uppercase tracking-widest text-gold/60">{title}</span>
          <div className="w-1 h-1 bg-gold/40 rounded-full" />
        </div>
      )}

      <div className="relative z-10">
        {children}
      </div>
    </motion.div>
  );
}
