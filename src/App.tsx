/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { AppScreen, AnalysisData } from './types';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { Portal } from './components/Portal';
import { Console } from './components/Console';
import { Engine } from './components/Engine';
import { Verdict } from './components/Verdict';
import { ExecutionHub } from './components/ExecutionHub';
import { Ledger } from './components/Ledger';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>('portal');
  const [data, setData] = useState<AnalysisData>({
    agentId: '',
    allocation: '',
    creditScore: 0,
    riskLevel: 'LOW',
    interestRate: '4.2%',
    collateral: '0.00',
    approved: true
  });

  const handleInitiateAnalysis = (agentId: string, allocation: string) => {
    setData(prev => ({ ...prev, agentId, allocation }));
    setCurrentScreen('engine');
  };

  const handleEngineComplete = (score: number) => {
    setData(prev => ({ 
      ...prev, 
      creditScore: score,
      approved: score > 750 // Simple threshold for demo
    }));
    setCurrentScreen('verdict');
  };

  return (
    <div className="min-h-screen bg-void text-white selection:bg-gold selection:text-void font-sans">
      <TopBar />
      
      {currentScreen !== 'portal' && (
        <Sidebar currentScreen={currentScreen} setScreen={setCurrentScreen} />
      )}

      <main className={`transition-all duration-500 ${currentScreen === 'portal' ? 'w-full' : 'md:ml-64'} pt-16`}>
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
            {currentScreen === 'engine' && <Engine agentId={data.agentId} onComplete={handleEngineComplete} />}
            {currentScreen === 'verdict' && (
              <Verdict 
                data={data} 
                onExecute={() => setCurrentScreen('execution')} 
                onRetry={() => setCurrentScreen('console')} 
              />
            )}
            {currentScreen === 'execution' && <ExecutionHub onFinish={() => setCurrentScreen('ledger')} />}
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
  );
}
