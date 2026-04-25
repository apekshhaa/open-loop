import { motion, AnimatePresence } from 'motion/react';
import { LogEntry } from '../types';
import { useEffect, useRef } from 'react';

interface TerminalLogProps {
  logs: LogEntry[];
  maxHeight?: string;
  className?: string;
}

export function TerminalLog({ logs, maxHeight = '12rem', className = '' }: TerminalLogProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className={`bg-void/80 border border-gold/20 p-4 font-mono text-[11px] relative terminal-grid ${className}`}>
      <div className="absolute top-0 right-0 bg-gold/10 border-b border-l border-gold/20 px-3 py-1 text-gold/60 font-display font-bold text-[9px] tracking-widest uppercase">
        SYSTEM_LOG // LIVE
      </div>
      
      <div 
        ref={containerRef}
        className="flex flex-col gap-1 overflow-y-auto mt-4 scroll-smooth"
        style={{ maxHeight }}
      >
        <AnimatePresence mode="popLayout">
          {logs.map((log) => (
            <motion.div 
              key={log.id}
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex gap-4"
            >
              <span className="text-gold/40 shrink-0">[{log.timestamp}]</span>
              <span className={`
                ${log.type === 'success' ? 'text-green-400' : ''}
                ${log.type === 'error' ? 'text-red-400' : ''}
                ${log.type === 'warning' ? 'text-gold' : ''}
                ${!log.type || log.type === 'info' ? 'text-gold/70' : ''}
              `}>
                &gt; {log.message}
              </span>
            </motion.div>
          ))}
        </AnimatePresence>
        <motion.div 
          animate={{ opacity: [1, 0, 1] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          className="w-1.5 h-3 bg-gold/40 mt-1"
        />
      </div>
    </div>
  );
}
