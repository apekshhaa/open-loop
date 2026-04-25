/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { AppScreen, AnalysisData, WalletState } from './types';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { Portal } from './components/Portal';
import { Console } from './components/Console';
import { Engine } from './components/Engine';
import { Verdict } from './components/Verdict';
import { ExecutionHub } from './components/ExecutionHub';
import { Ledger } from './components/Ledger';
import DarkVeil from './components/DarkVeil';
import ClickSpark from './components/ClickSpark';
import { connectWallet, switchToSepolia } from './services/wallet';
import type { JsonRpcSigner } from 'ethers';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>('portal');
  const [data, setData] = useState<AnalysisData>({
    agentId: '',
    amount: 0,
    creditScore: 0,
    riskLevel: 'low',
    confidence: 0,
    approved: true,
    decisionReason: '',
    interestRate: 0,
    collateral: '0.00',
    collateralRequired: 0,
    monthlyPayment: 0,
    totalInterest: 0,
  });

  // ── Wallet State ─────────────────────────────────────────────
  const [wallet, setWallet] = useState<WalletState>({
    address: '',
    isConnected: false,
    chainId: '',
    isCorrectNetwork: false,
  });
  const [signer, setSigner] = useState<JsonRpcSigner | null>(null);
  const [isConnectingWallet, setIsConnectingWallet] = useState(false);

  // ── Wallet Handlers ──────────────────────────────────────────
  const handleConnectWallet = useCallback(async () => {
    setIsConnectingWallet(true);
    try {
      const walletInfo = await connectWallet();

      // If not on Sepolia, prompt to switch
      if (!walletInfo.isCorrectNetwork) {
        await switchToSepolia();
        // Re-connect after network switch to get updated info
        const updated = await connectWallet();
        setWallet({
          address: updated.address,
          isConnected: true,
          chainId: updated.chainId,
          isCorrectNetwork: updated.isCorrectNetwork,
        });
        setSigner(updated.signer);
      } else {
        setWallet({
          address: walletInfo.address,
          isConnected: true,
          chainId: walletInfo.chainId,
          isCorrectNetwork: walletInfo.isCorrectNetwork,
        });
        setSigner(walletInfo.signer);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to connect wallet');
    } finally {
      setIsConnectingWallet(false);
    }
  }, []);

  const handleInitiateAnalysis = (walletAddress: string, amount: number) => {
    setData(prev => ({ 
      ...prev, 
      agentId: walletAddress,  // Store wallet address in agentId field for backward compatibility
      amount,
    }));
    setCurrentScreen('engine');
  };

  const handleEngineComplete = (analysisData: AnalysisData) => {
    setData(analysisData);
    setCurrentScreen('verdict');
  };

  return (
    <ClickSpark sparkColor="#FFD700" sparkSize={10} sparkRadius={15} sparkCount={8} duration={400}>
      <div className="min-h-screen bg-void text-white selection:bg-gold selection:text-void font-sans">
      <TopBar 
        wallet={wallet}
        onConnectWallet={handleConnectWallet}
        isConnecting={isConnectingWallet}
      />
      
      {currentScreen !== 'portal' && (
        <Sidebar currentScreen={currentScreen} setScreen={setCurrentScreen} />
      )}

      {currentScreen !== 'portal' && (
        <div className="fixed top-16 right-0 bottom-0 left-0 md:left-64 pointer-events-none z-0 opacity-80">
          <DarkVeil speed={0.2} noiseIntensity={0.02} scanlineIntensity={0.1} warpAmount={0.3} />
        </div>
      )}

      <main className={`relative z-10 transition-all duration-500 ${currentScreen === 'portal' ? 'w-full' : 'md:ml-64'} pt-16`}>
        <AnimatePresence mode="wait">
          <motion.div
            key={currentScreen}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.4, ease: 'easeInOut' }}
          >
            {currentScreen === 'portal' && <Portal onEnter={() => setCurrentScreen('console')} />}
            {currentScreen === 'console' && <Console onInitiate={handleInitiateAnalysis} />}
            {currentScreen === 'engine' && (
              <Engine 
                walletAddress={data.agentId}  // agentId field now stores wallet address
                amount={data.amount}
                onComplete={handleEngineComplete} 
              />
            )}
            {currentScreen === 'verdict' && (
              <Verdict 
                data={data} 
                onExecute={() => setCurrentScreen('execution')} 
                onRetry={() => setCurrentScreen('console')} 
                wallet={wallet}
                onConnectWallet={handleConnectWallet}
              />
            )}
            {currentScreen === 'execution' && (
              <ExecutionHub 
                onFinish={() => setCurrentScreen('ledger')}
                signer={signer}
                walletAddress={wallet.address}
                isWalletConnected={wallet.isConnected}
                onConnectWallet={handleConnectWallet}
              />
            )}
            {currentScreen === 'ledger' && <Ledger />}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Decorative Overlays */}
      <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
        {/* Subtle scanline texture across everything */}
        <div className="absolute inset-0 scanline opacity-[0.03]" />
      </div>
    </div>
    </ClickSpark>
  );
}
