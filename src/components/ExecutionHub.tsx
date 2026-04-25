import { motion, AnimatePresence } from 'motion/react';
import { useState, useEffect, useCallback } from 'react';
import { AureumPanel } from './AureumPanel';
import { TerminalLog } from './TerminalLog';
import { Check, Wallet, FileKey, Share2, Server, Milestone, Copy, ExternalLink, AlertTriangle } from 'lucide-react';
import { LogEntry, TransactionStatus } from '../types';
import { sendDisbursement, getExplorerUrl, formatAddress } from '../services/wallet';
import type { JsonRpcSigner } from 'ethers';

interface ExecutionHubProps {
  onFinish: () => void;
  signer: JsonRpcSigner | null;
  walletAddress: string;
  isWalletConnected: boolean;
  onConnectWallet: () => void;
}

export function ExecutionHub({ onFinish, signer, walletAddress, isWalletConnected, onConnectWallet }: ExecutionHubProps) {
  const [step, setStep] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [txStatus, setTxStatus] = useState<TransactionStatus>('idle');
  const [txHash, setTxHash] = useState('');
  const [txExplorerUrl, setTxExplorerUrl] = useState('');
  const [txError, setTxError] = useState('');
  const [copied, setCopied] = useState(false);

  const isSuccess = txStatus === 'success';
  const isError = txStatus === 'error';
  const isProcessing = !['idle', 'success', 'error'].includes(txStatus);

  const addLog = useCallback((message: string, type: LogEntry['type'] = 'info') => {
    const now = new Date();
    const timestamp = now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) 
      + '.' + now.getMilliseconds().toString().padStart(3, '0');
    setLogs(prev => [...prev, { id: `${Date.now()}-${Math.random()}`, timestamp, message, type }]);
  }, []);

  const steps = [
    { title: 'Connecting Wallet', icon: Wallet, detail: walletAddress ? `ADDR: ${formatAddress(walletAddress)}` : 'ADDR: PENDING' },
    { title: 'Signing Transaction', icon: FileKey, detail: 'SIG: AWAITING_USER' },
    { title: 'Broadcasting to Network', icon: Share2, detail: 'NETWORK: SEPOLIA_TESTNET' },
    { title: 'Confirming on Chain', icon: Server, detail: 'STATUS: AWAITING_CONFIRMATION' },
  ];

  // ── Execute Real Transaction ───────────────────────────────────
  const executeTransaction = useCallback(async () => {
    if (!signer) {
      setTxError('Wallet not connected. Please connect your MetaMask wallet first.');
      setTxStatus('error');
      addLog('ERROR: No signer available — wallet not connected', 'error');
      return;
    }

    try {
      // Step 1: Connecting
      setStep(1);
      setTxStatus('connecting');
      addLog('INIT PROTOCOL: TX_EXECUTION_REAL');
      addLog(`WALLET CONNECTED: ${formatAddress(walletAddress)}`, 'success');

      // Brief delay for UI pacing
      await new Promise(r => setTimeout(r, 800));

      // Step 2: Signing
      setStep(2);
      setTxStatus('signing');
      addLog('REQUESTING CRYPTOGRAPHIC SIGNATURE FROM METAMASK...');
      addLog('AWAITING USER APPROVAL IN WALLET...', 'warning');

      // Step 3: Broadcasting (sendTransaction triggers MetaMask popup)
      const result = await sendDisbursement(signer);

      if (!result.success) {
        setTxError(result.error || 'Transaction failed');
        setTxStatus('error');
        addLog(`TRANSACTION FAILED: ${result.error}`, 'error');
        return;
      }

      // Transaction was signed and sent
      addLog('SIGNATURE VERIFIED. TRANSACTION SIGNED.', 'success');
      
      setStep(3);
      setTxStatus('broadcasting');
      addLog(`TX HASH: ${result.txHash}`);
      addLog('BROADCASTING TO SEPOLIA NETWORK...');

      await new Promise(r => setTimeout(r, 500));

      // Step 4: Confirmed (sendDisbursement already waited for confirmation)
      setStep(4);
      setTxStatus('confirming');
      addLog('TRANSACTION INCLUDED IN BLOCK. AWAITING FINALIZATION...', 'warning');

      await new Promise(r => setTimeout(r, 1000));

      // Success!
      setTxHash(result.txHash);
      setTxExplorerUrl(result.explorerUrl);
      setTxStatus('success');
      addLog('TRANSACTION CONFIRMED ON SEPOLIA TESTNET', 'success');
      addLog(`EXPLORER: ${result.explorerUrl}`, 'success');
      addLog('EXECUTION COMPLETE. STATUS: SUCCESS.', 'success');

    } catch (err: any) {
      setTxError(err.message || 'Unknown error occurred');
      setTxStatus('error');
      addLog(`CRITICAL ERROR: ${err.message || err}`, 'error');
    }
  }, [signer, walletAddress, addLog]);

  // Auto-start transaction when component mounts (if wallet is connected)
  useEffect(() => {
    if (isWalletConnected && signer && txStatus === 'idle') {
      executeTransaction();
    }
  }, [isWalletConnected, signer, txStatus, executeTransaction]);

  const handleCopyHash = () => {
    if (txHash) {
      navigator.clipboard.writeText(txHash);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // ── Wallet Not Connected State ─────────────────────────────────
  if (!isWalletConnected) {
    return (
      <div className="pt-12 pb-24 px-4 max-w-6xl mx-auto w-full flex flex-col items-center justify-center min-h-[60vh]">
        <div className="glass-panel p-16 flex flex-col items-center text-center max-w-lg">
          <div className="w-20 h-20 rounded-full bg-gold/10 border border-gold/20 flex items-center justify-center mb-8">
            <Wallet size={36} className="text-gold" />
          </div>
          <h2 className="font-display font-black text-3xl text-gold uppercase tracking-tighter mb-4">
            Wallet Required
          </h2>
          <p className="font-mono text-xs text-gold/50 mb-8 leading-relaxed max-w-sm">
            Connect your MetaMask wallet to execute a real blockchain transaction on the Sepolia testnet.
          </p>
          <button
            onClick={onConnectWallet}
            className="w-full py-5 flex items-center justify-center gap-3 bg-gold text-void font-display font-black text-sm uppercase tracking-widest hover:bg-gold/90 transition-all shadow-[0_0_25px_rgba(255,215,0,0.3)]"
          >
            <Wallet size={18} />
            Connect MetaMask
          </button>
          <p className="font-mono text-[9px] text-gold/30 mt-4 tracking-widest uppercase">
            Sepolia Testnet • Test ETH Required
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-12 pb-24 px-4 max-w-6xl mx-auto w-full flex flex-col gap-8">
      <div className="flex justify-between items-end border-b border-gold/20 pb-4">
        <div>
          <h1 className="font-display text-4xl font-bold text-gold uppercase tracking-tighter">Transaction Execution Hub</h1>
          <p className="font-mono text-[10px] text-gold/60 mt-2 tracking-widest uppercase">&gt; Sepolia Testnet • Real Blockchain Transaction</p>
        </div>
        <div className="text-right">
          <div className="font-display font-medium text-[9px] text-gold/40 mb-1 uppercase tracking-[0.2em]">Wallet</div>
          <div className="font-mono text-sm text-gold">{formatAddress(walletAddress)}</div>
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
                const isCompleted = step > idx + 1 || (step === idx + 1 && isSuccess);
                const isFailed = isActive && isError;
                const Icon = s.icon;

                return (
                  <div key={idx} className="flex gap-6 relative z-10">
                    <div className={`
                      w-6 h-6 rounded-full flex items-center justify-center shrink-0 border transition-all duration-500
                      ${isCompleted ? 'bg-gold border-gold' : 
                        isFailed ? 'bg-red-500/20 border-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]' :
                        isActive ? 'bg-gold/20 border-gold shadow-[0_0_10px_gold]' : 
                        'bg-void border-gold/20'}
                    `}>
                      {isCompleted ? <Check size={12} className="text-void" strokeWidth={3} /> : 
                       isFailed ? <AlertTriangle size={12} className="text-red-400" /> :
                       <Icon size={12} className={isActive ? 'text-gold' : 'text-gold/20'} />}
                    </div>
                    <div>
                      <div className={`font-mono text-xs transition-opacity duration-500 ${
                        isActive ? (isFailed ? 'text-red-400 font-bold' : 'text-gold font-bold') : 
                        isCompleted ? 'text-gold/80' : 'text-gold/20'
                      }`}>
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
                <div className="font-display font-bold text-[8px] text-gold/40 mb-1 uppercase tracking-widest">Network</div>
                <div className="font-mono text-sm text-white">Sepolia</div>
              </div>
              <div className="border border-gold/10 p-4">
                <div className="font-display font-bold text-[8px] text-gold/40 mb-1 uppercase tracking-widest">Amount</div>
                <div className="font-mono text-sm text-white">0.001 ETH</div>
              </div>
              <div className="border border-gold/10 p-4 col-span-2">
                <div className="font-display font-bold text-[8px] text-gold/40 mb-1 uppercase tracking-widest">Status</div>
                <div className={`font-mono text-sm ${isSuccess ? 'text-emerald-400' : isError ? 'text-red-400' : 'text-gold animate-pulse'}`}>
                  {isSuccess ? 'CONFIRMED' : isError ? 'FAILED' : isProcessing ? 'PROCESSING...' : 'READY'}
                </div>
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
              {isError ? (
                <motion.div 
                  key="error"
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="flex flex-col items-center max-w-md"
                >
                  <div className="relative w-24 h-24 mb-8">
                    <div className="absolute inset-0 bg-red-500/10 blur-3xl opacity-50 rounded-full" />
                    <div className="w-full h-full flex items-center justify-center">
                      <AlertTriangle size={60} className="text-red-400" strokeWidth={2} />
                    </div>
                  </div>
                  <h2 className="font-display font-black text-4xl text-red-400 uppercase mb-4 tracking-tighter">Transaction Failed</h2>
                  <p className="font-mono text-xs text-red-300/60 mb-8 leading-relaxed">
                    {txError}
                  </p>
                  <div className="flex gap-4 w-full">
                    <button 
                      onClick={() => {
                        setTxStatus('idle');
                        setTxError('');
                        setStep(0);
                        setLogs([]);
                      }}
                      className="flex-1 py-4 bg-gold text-void font-display font-black text-[10px] uppercase tracking-widest hover:bg-gold/90 transition-all"
                    >
                      Retry Transaction
                    </button>
                  </div>
                </motion.div>
              ) : !isSuccess ? (
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
                  <h2 className="font-display font-black text-3xl text-gold uppercase tracking-tighter animate-pulse mb-2">
                    {txStatus === 'signing' ? 'Approve in MetaMask...' : 
                     txStatus === 'broadcasting' ? 'Broadcasting...' :
                     txStatus === 'confirming' ? 'Confirming...' : 'Executing...'}
                  </h2>
                  <p className="font-mono text-xs text-gold/40 tracking-widest uppercase">
                    {txStatus === 'signing' ? 'Please sign the transaction in your wallet' :
                     txStatus === 'broadcasting' ? 'Transaction sent to Sepolia network' :
                     txStatus === 'confirming' ? 'Waiting for block confirmation' :
                     'Initializing blockchain transaction'}
                  </p>
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
                    TRANSACTION CONFIRMED ON SEPOLIA TESTNET. FUNDS DISBURSED VIA BLOCKCHAIN.
                  </p>
                  
                  {/* Transaction Hash */}
                  <div className="bg-gold/5 border border-gold/20 p-4 mb-4 w-full group transition-all hover:bg-gold/10">
                    <span className="block font-display font-bold text-[8px] text-gold/40 uppercase tracking-[0.2em] mb-2 text-center">Transaction Hash</span>
                    <div className="flex items-center justify-center gap-3 font-mono text-gold selection:bg-gold/30 text-sm">
                      <span className="truncate max-w-[280px]">{txHash}</span>
                      <button onClick={handleCopyHash} className="shrink-0">
                        <Copy size={14} className={`cursor-pointer transition-colors ${copied ? 'text-emerald-400' : 'hover:text-white'}`} />
                      </button>
                    </div>
                  </div>

                  {/* Etherscan Link */}
                  <a 
                    href={txExplorerUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-2 w-full py-3 border border-gold/10 text-gold/60 font-mono text-[10px] uppercase tracking-widest hover:bg-gold/5 hover:text-gold transition-all mb-8"
                  >
                    <ExternalLink size={12} />
                    View on Sepolia Etherscan
                  </a>

                  <div className="flex gap-4 w-full">
                    <button 
                      onClick={() => onFinish()}
                      className="flex-1 py-4 border border-gold text-gold font-display font-black text-[10px] uppercase tracking-widest hover:bg-gold/10 transition-all"
                    >
                      View Ledger
                    </button>
                    <button 
                      onClick={() => window.location.reload()}
                      className="flex-1 py-4 bg-gold text-void font-display font-black text-[10px] uppercase tracking-widest hover:bg-gold/90 transition-all shadow-[0_0_20px_rgba(255,215,0,0.3)]"
                    >
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
