import { motion } from 'motion/react';
import { useState, useEffect } from 'react';
import { AureumPanel } from './AureumPanel';
import { Bolt, Wallet, CheckCircle, AlertCircle } from 'lucide-react';
import { LogEntry } from '../types';
import {
  validateWalletAddress,
  connectMetaMask,
  isMetaMaskAvailable,
  getConnectedAccount,
  setupMetaMaskListeners,
  formatAddressForDisplay,
} from '../services/walletService';

interface ConsoleProps {
  onInitiate: (walletAddress: string, amount: number) => void;
}

export function Console({ onInitiate }: ConsoleProps) {
  const [walletAddress, setWalletAddress] = useState('');
  const [amount, setAmount] = useState('50000');
  const [isLoading, setIsLoading] = useState(false);
  const [walletConnected, setWalletConnected] = useState(false);
  const [connectionError, setConnectionError] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [metaMaskAvailable, setMetaMaskAvailable] = useState(false);

  // Check MetaMask availability and restore connection on mount
  useEffect(() => {
    const initializeWallet = async () => {
      const available = isMetaMaskAvailable();
      setMetaMaskAvailable(available);
      console.log('[Console] MetaMask available:', available);

      // Try to restore previous connection
      if (available) {
        try {
          const connected = await getConnectedAccount();
          if (connected) {
            console.log('[Console] Restoring wallet connection:', connected);
            setWalletAddress(connected);
            setWalletConnected(true);
            setConnectionError('');
          }
        } catch (error) {
          console.error('[Console] Error restoring connection:', error);
        }
      }
    };

    initializeWallet();

    // Setup MetaMask listeners
    const cleanup = setupMetaMaskListeners(
      (accounts) => {
        // Handle account change
        if (accounts && accounts.length > 0) {
          console.log('[Console] Account changed via MetaMask:', accounts[0]);
          setWalletAddress(accounts[0]);
          setWalletConnected(true);
          setConnectionError('');
        } else {
          console.log('[Console] All accounts disconnected');
          setWalletAddress('');
          setWalletConnected(false);
        }
      },
      (chainId) => {
        // Handle chain change
        console.log('[Console] Chain changed:', chainId);
        // You might want to handle chain changes here
      }
    );

    return cleanup;
  }, []);

  // Connect wallet using MetaMask
  const handleConnectWallet = async () => {
    if (!metaMaskAvailable) {
      setConnectionError('MetaMask is not installed. Please install MetaMask to continue.');
      console.error('[Console] MetaMask not available');
      return;
    }

    setIsConnecting(true);
    setConnectionError('');

    try {
      console.log('[Console] Initiating MetaMask connection...');
      const connectedAddress = await connectMetaMask();
      
      // Validate the address
      const validation = validateWalletAddress(connectedAddress);
      if (!validation.isValid) {
        setConnectionError(validation.error || 'Failed to validate wallet address');
        console.error('[Console] Wallet validation failed:', validation);
        return;
      }

      console.log('[Console] Wallet connected successfully:', connectedAddress);
      setWalletAddress(connectedAddress);
      setWalletConnected(true);
      setConnectionError('');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to connect wallet';
      console.error('[Console] Connection error:', errorMessage);
      setConnectionError(errorMessage);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnectWallet = () => {
    console.log('[Console] Disconnecting wallet');
    setWalletAddress('');
    setWalletConnected(false);
    setConnectionError('');
  };

  const handleRequestLoan = () => {
    console.log('[Console] Loan request initiated', {
      walletConnected,
      walletAddress,
      amount,
    });

    // Validate wallet is connected
    if (!walletConnected || !walletAddress) {
      setConnectionError('Please connect your wallet first');
      console.warn('[Console] Loan request blocked: wallet not connected');
      return;
    }

    // Validate wallet address format using the new service
    const validation = validateWalletAddress(walletAddress);
    if (!validation.isValid) {
      setConnectionError(
        validation.error || 'Invalid wallet address format'
      );
      console.error('[Console] Wallet validation failed:', validation);
      return;
    }

    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      setConnectionError('Please enter a valid loan amount');
      console.warn('[Console] Invalid amount:', amount);
      return;
    }

    console.log('[Console] All validations passed, initiating analysis', {
      wallet: validation.address,
      amount: parsedAmount,
    });

    setIsLoading(true);
    setConnectionError('');
    onInitiate(validation.address!, parsedAmount);
  };

  return (
    <div className="pt-12 pb-24 px-4 max-w-5xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      {/* Left Column: Wallet Status & System Info */}
      <div className="lg:col-span-4 flex flex-col gap-8">
        {/* Wallet Status Panel */}
        <AureumPanel 
          title="Wallet Status"
          className={walletConnected ? 'border-green-500/30 bg-green-900/10' : 'border-gold/20'}
        >
          <div className="flex flex-col space-y-4">
            {walletConnected ? (
              <>
                <div className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-400" />
                  <span className="font-mono text-xs text-green-400">Connected</span>
                </div>
                <div className="font-mono text-[10px] text-gold/70 break-all">
                  {walletAddress}
                </div>
                <button
                  onClick={handleDisconnectWallet}
                  className="text-xs py-2 px-3 border border-gold/30 text-gold/70 hover:border-gold hover:text-gold transition-all"
                >
                  Disconnect Wallet
                </button>
              </>
            ) : (
              <>
                <div className="flex items-center gap-2">
                  <AlertCircle size={16} className="text-gold/50" />
                  <span className="font-mono text-xs text-gold/50">Not Connected</span>
                </div>
                <p className="font-mono text-[9px] text-gold/40">
                  Connect your Ethereum wallet to request a loan
                </p>
                <button
                  onClick={handleConnectWallet}
                  disabled={isConnecting || !metaMaskAvailable}
                  className={`text-sm py-3 px-4 border transition-all font-semibold flex items-center justify-center gap-2 ${
                    !metaMaskAvailable
                      ? 'bg-red-900/20 border-red-500/30 text-red-400 cursor-not-allowed'
                      : 'bg-gold/20 border-gold/50 text-gold hover:bg-gold/30 hover:border-gold'
                  }`}
                >
                  <Wallet size={16} />
                  {isConnecting ? 'Connecting...' : 'Connect Wallet'}
                </button>
                {!metaMaskAvailable && (
                  <p className="font-mono text-[9px] text-red-400 text-center">
                    MetaMask not detected. Please install MetaMask.
                  </p>
                )}
              </>
            )}
          </div>
        </AureumPanel>

        <AureumPanel title="System Uptime">
          <div className="flex flex-col">
            <div className="flex items-baseline gap-2">
              <span className="font-display font-black text-4xl text-gold glow-gold tracking-tight">99.99</span>
              <span className="font-mono text-xs text-gold/60">%</span>
            </div>
            <div className="mt-4 flex items-center gap-2">
              <motion.div 
                animate={{ opacity: [1, 0.4, 1] }}
                className="w-2 h-2 rounded-full bg-gold" 
              />
              <span className="font-mono text-[9px] text-gold/40 uppercase tracking-widest">Core Synchronized</span>
            </div>
          </div>
        </AureumPanel>

        <AureumPanel title="Active Nodes">
          <div className="space-y-4">
            {['Alpha', 'Beta', 'Gamma'].map((node) => (
              <div key={node} className="flex justify-between items-center pb-2 border-b border-gold/5">
                <span className="font-mono text-[10px] text-gold/40 uppercase tracking-widest">NODE_{node.toUpperCase()}</span>
                <span className="font-mono text-[10px] text-gold uppercase tracking-widest">Secure</span>
              </div>
            ))}
          </div>
        </AureumPanel>
      </div>

      {/* Right Column: Loan Request Terminal */}
      <div className="lg:col-span-8">
        <AureumPanel className="min-h-[500px] flex flex-col pt-12">
          <div className="max-w-2xl mx-auto w-full flex flex-col h-full">
            <div className="text-center mb-12">
              <h2 className="font-display font-bold text-2xl text-gold uppercase tracking-widest mb-2">Loan Request Terminal</h2>
              <p className="font-mono text-xs text-gold/40 tracking-widest uppercase">
                {walletConnected ? 'Wallet Connected - Ready to Request Loan' : 'Connect Wallet to Continue'}
              </p>
            </div>

            {connectionError && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8 p-3 bg-red-900/20 border border-red-500/30 rounded"
              >
                <p className="font-mono text-xs text-red-400">{connectionError}</p>
              </motion.div>
            )}

            {/* Wallet Address Display */}
            {walletConnected && (
              <div className="space-y-3 mb-8 p-4 bg-gold/5 border border-gold/20 rounded">
                <label className="font-display font-bold text-[10px] text-gold uppercase tracking-[0.3em]">Connected Wallet</label>
                <div className="font-mono text-[11px] text-gold/80 break-all">{walletAddress}</div>
              </div>
            )}

            <div className="space-y-12 flex-1">
              {/* Loan Amount Input */}
              <div className="space-y-3">
                <label className="font-display font-bold text-[10px] text-gold uppercase tracking-[0.3em] pl-4">
                  Loan Amount (USD)
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-gold/30 font-mono">$</div>
                  <input 
                    type="number" 
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-full bg-void/50 border border-gold/20 text-gold font-mono pl-10 pr-4 py-5 focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold/30 transition-all text-xl disabled:opacity-50"
                    placeholder="50000"
                    disabled={isLoading || !walletConnected}
                  />
                </div>
                <div className="flex justify-between px-4 font-mono text-[9px] text-gold/30 uppercase tracking-widest">
                  <span>Min: $1</span>
                  <span>Max: $10,000,000</span>
                </div>
              </div>

              {/* Info: Wallet Required */}
              {!walletConnected && (
                <div className="p-4 bg-gold/5 border border-gold/20 rounded">
                  <p className="font-mono text-[10px] text-gold/60">
                    ✓ Wallet connection is required to request a loan. This ensures secure, on-chain identity verification.
                  </p>
                </div>
              )}
            </div>

            <div className="mt-12 pt-8 border-t border-gold/10">
              <button 
                onClick={handleRequestLoan}
                disabled={isLoading || !walletConnected}
                className={`w-full py-6 flex items-center justify-center gap-4 font-display font-black text-lg uppercase tracking-widest transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed ${
                  walletConnected && !isLoading
                    ? 'bg-gold text-void shadow-[0_0_25px_rgba(255,215,0,0.3)] hover:bg-gold/90 hover:shadow-[0_0_40px_rgba(255,215,0,0.5)]'
                    : 'bg-gold/30 text-gold/50'
                }`}
              >
                <Bolt size={20} className={`fill-current ${isLoading ? 'animate-spin' : ''}`} />
                {!walletConnected ? 'Connect Wallet First' : isLoading ? 'Analyzing...' : 'Request Loan'}
              </button>
              {!walletConnected && (
                <p className="text-center mt-4 font-mono text-xs text-gold/40">
                  Button will be enabled after wallet connection
                </p>
              )}
            </div>
          </div>
        </AureumPanel>
      </div>
    </div>
  );
}
