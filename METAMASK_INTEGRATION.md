# MetaMask + Blockchain Integration Guide

## Overview

This guide explains how to integrate MetaMask wallet connection and blockchain transactions with the wallet-based AI Agent Credit System.

---

## Architecture

```
Frontend (React)
    ↓ User connects MetaMask
    ↓ User requests loan
    ↓ Calls /loan/wallet/request
Backend (FastAPI)
    ↓ Returns loan decision
    ↓ Response to frontend
Frontend (React)
    ↓ User approves transaction
    ↓ Calls signer.sendTransaction()
Blockchain (Testnet)
    ↓ Transaction processed
    ↓ Loan "disbursed" (simulated)
```

---

## Frontend Setup

### 1. Install Dependencies

```bash
npm install ethers @rainbow-me/rainbowkit
```

**Key libraries**:
- `ethers.js` - Blockchain interaction
- `@rainbow-me/rainbowkit` - Wallet connection UI (optional)

### 2. Create Wallet Service

**File**: `src/services/wallet.ts`

```typescript
import { BrowserProvider, Contract } from 'ethers';

export interface WalletState {
  address: string | null;
  provider: BrowserProvider | null;
  signer: any | null;
  isConnected: boolean;
}

export class WalletService {
  static async connectWallet(): Promise<string> {
    if (!window.ethereum) {
      throw new Error('MetaMask not installed');
    }

    try {
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      });

      const address = accounts[0];
      console.log('Connected wallet:', address);
      return address;
    } catch (error: any) {
      if (error.code === 4001) {
        throw new Error('User rejected connection');
      }
      throw error;
    }
  }

  static async getProvider(): Promise<BrowserProvider> {
    if (!window.ethereum) {
      throw new Error('MetaMask not installed');
    }

    return new BrowserProvider(window.ethereum);
  }

  static async getSigner(): Promise<any> {
    const provider = await this.getProvider();
    return provider.getSigner();
  }

  static async switchNetwork(chainId: string = '0xaa36a7'): Promise<void> {
    if (!window.ethereum) {
      throw new Error('MetaMask not installed');
    }

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId }]
      });
    } catch (error: any) {
      if (error.code === 4902) {
        // Network not added, add it
        await this.addNetwork();
      } else {
        throw error;
      }
    }
  }

  static async addNetwork(): Promise<void> {
    if (!window.ethereum) {
      throw new Error('MetaMask not installed');
    }

    await window.ethereum.request({
      method: 'wallet_addEthereumChain',
      params: [{
        chainId: '0xaa36a7',
        chainName: 'Sepolia Testnet',
        rpcUrls: ['https://sepolia.infura.io/v3/'],
        nativeCurrency: {
          name: 'ETH',
          symbol: 'ETH',
          decimals: 18
        },
        blockExplorerUrls: ['https://sepolia.etherscan.io']
      }]
    });
  }

  static async sendTransaction(
    to: string,
    amount: string = '0.001'
  ): Promise<string> {
    const signer = await this.getSigner();

    const tx = await signer.sendTransaction({
      to,
      value: (BigInt(amount) * BigInt(10) ** BigInt(18)).toString()
    });

    const receipt = await tx.wait();
    return tx.hash;
  }

  static async getBalance(address: string): Promise<string> {
    const provider = await this.getProvider();
    const balance = await provider.getBalance(address);
    return (Number(balance) / 10 ** 18).toFixed(4);
  }

  static formatAddress(address: string): string {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  }
}
```

### 3. Create Wallet Context (Optional)

**File**: `src/context/WalletContext.tsx`

```typescript
import { createContext, useContext, useState } from 'react';
import { WalletService, WalletState } from '../services/wallet';

interface WalletContextType {
  walletState: WalletState;
  connectWallet: () => Promise<void>;
  disconnectWallet: () => void;
  sendTransaction: (to: string, amount: string) => Promise<string>;
  getBalance: () => Promise<string>;
}

export const WalletContext = createContext<WalletContextType | null>(null);

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const [walletState, setWalletState] = useState<WalletState>({
    address: null,
    provider: null,
    signer: null,
    isConnected: false
  });

  const connectWallet = async () => {
    try {
      const address = await WalletService.connectWallet();
      const provider = await WalletService.getProvider();
      const signer = await WalletService.getSigner();

      setWalletState({
        address,
        provider,
        signer,
        isConnected: true
      });
    } catch (error) {
      console.error('Failed to connect wallet:', error);
      throw error;
    }
  };

  const disconnectWallet = () => {
    setWalletState({
      address: null,
      provider: null,
      signer: null,
      isConnected: false
    });
  };

  const sendTransaction = async (to: string, amount: string) => {
    if (!walletState.isConnected) {
      throw new Error('Wallet not connected');
    }
    return await WalletService.sendTransaction(to, amount);
  };

  const getBalance = async () => {
    if (!walletState.address) {
      throw new Error('Wallet not connected');
    }
    return await WalletService.getBalance(walletState.address);
  };

  return (
    <WalletContext.Provider
      value={{
        walletState,
        connectWallet,
        disconnectWallet,
        sendTransaction,
        getBalance
      }}
    >
      {children}
    </WalletContext.Provider>
  );
}

export function useWallet() {
  const context = useContext(WalletContext);
  if (!context) {
    throw new Error('useWallet must be used within WalletProvider');
  }
  return context;
}
```

### 4. Create Connect Wallet Component

**File**: `src/components/ConnectWallet.tsx`

```typescript
import { useState } from 'react';
import { useWallet } from '../context/WalletContext';

export function ConnectWallet() {
  const { walletState, connectWallet } = useWallet();
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleConnect = async () => {
    try {
      setLoading(true);
      setError('');
      await connectWallet();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (walletState.isConnected) {
    return (
      <div className="bg-green-900/20 border border-green-500/50 rounded px-4 py-2">
        <span className="text-green-400 font-mono text-sm">
          ✓ Connected: {walletState.address?.slice(0, 6)}...{walletState.address?.slice(-4)}
        </span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <button
        onClick={handleConnect}
        disabled={loading}
        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded font-semibold"
      >
        {loading ? 'Connecting...' : 'Connect MetaMask'}
      </button>
      {error && (
        <p className="text-red-400 text-sm">{error}</p>
      )}
    </div>
  );
}
```

### 5. Create Loan Request Component

**File**: `src/components/WalletLoanRequest.tsx`

```typescript
import { useState } from 'react';
import { useWallet } from '../context/WalletContext';

const BACKEND_URL = 'http://127.0.0.1:8000';

interface LoanDecision {
  wallet_address: string;
  credit_score: number;
  risk_level: string;
  approved: boolean;
  interest_rate: number;
  collateral_required: number;
  decision_reason: string;
  monthly_payment: number;
  total_interest: number;
}

export function WalletLoanRequest() {
  const { walletState } = useWallet();
  const [amount, setAmount] = useState('50000');
  const [loading, setLoading] = useState(false);
  const [decision, setDecision] = useState<LoanDecision | null>(null);
  const [error, setError] = useState<string>('');

  const handleRequestLoan = async () => {
    if (!walletState.address) {
      setError('Please connect wallet first');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await fetch(
        `${BACKEND_URL}/loan/wallet/request?` +
        `wallet_address=${walletState.address}&amount=${amount}`,
        { method: 'POST' }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Loan request failed');
      }

      const loanDecision = await response.json();
      setDecision(loanDecision);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Wallet Status */}
      {walletState.isConnected && (
        <div className="bg-green-900/20 border border-green-500/30 rounded p-4">
          <p className="text-green-400 font-mono text-sm">
            Wallet: {walletState.address}
          </p>
        </div>
      )}

      {/* Loan Request Form */}
      {!decision && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Loan Amount ($)</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white"
              min="1"
              max="10000000"
            />
          </div>

          <button
            onClick={handleRequestLoan}
            disabled={loading || !walletState.isConnected}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded font-semibold"
          >
            {loading ? 'Requesting Loan...' : 'Request Loan'}
          </button>

          {error && (
            <div className="bg-red-900/20 border border-red-500/30 rounded p-3">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}
        </div>
      )}

      {/* Decision Display */}
      {decision && (
        <LoanDecisionDisplay decision={decision} onReset={() => setDecision(null)} />
      )}
    </div>
  );
}

function LoanDecisionDisplay({
  decision,
  onReset
}: {
  decision: LoanDecision;
  onReset: () => void;
}) {
  const { sendTransaction } = useWallet();
  const [txLoading, setTxLoading] = useState(false);
  const [txHash, setTxHash] = useState('');
  const [txError, setTxError] = useState('');

  const handleDisburse = async () => {
    if (!decision.approved) {
      alert('Loan not approved');
      return;
    }

    try {
      setTxLoading(true);
      setTxError('');

      // Send transaction to test address
      const recipientAddress = '0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0';
      const txHash = await sendTransaction(recipientAddress, '0.001');

      setTxHash(txHash);
    } catch (err: any) {
      setTxError(err.message);
    } finally {
      setTxLoading(false);
    }
  };

  const blockExplorerUrl = `https://sepolia.etherscan.io/tx/${txHash}`;

  return (
    <div className="space-y-6">
      {/* Decision Result */}
      <div
        className={`border rounded p-6 ${
          decision.approved
            ? 'bg-green-900/20 border-green-500/30'
            : 'bg-red-900/20 border-red-500/30'
        }`}
      >
        <h3 className={`text-xl font-bold mb-4 ${
          decision.approved ? 'text-green-400' : 'text-red-400'
        }`}>
          {decision.approved ? '✓ Loan Approved' : '✗ Loan Rejected'}
        </h3>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-slate-400">Credit Score</p>
            <p className="text-xl font-bold text-white">{decision.credit_score}</p>
          </div>
          <div>
            <p className="text-slate-400">Risk Level</p>
            <p className="text-xl font-bold text-white">{decision.risk_level}</p>
          </div>
          {decision.approved && (
            <>
              <div>
                <p className="text-slate-400">Interest Rate</p>
                <p className="text-xl font-bold text-white">{decision.interest_rate}%</p>
              </div>
              <div>
                <p className="text-slate-400">Monthly Payment</p>
                <p className="text-xl font-bold text-white">${decision.monthly_payment.toFixed(2)}</p>
              </div>
            </>
          )}
        </div>

        <p className="mt-4 text-slate-300 text-sm">{decision.decision_reason}</p>
      </div>

      {/* Disburse Button */}
      {decision.approved && !txHash && (
        <button
          onClick={handleDisburse}
          disabled={txLoading}
          className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded font-semibold"
        >
          {txLoading ? 'Processing Transaction...' : 'Disburse Loan'}
        </button>
      )}

      {/* Transaction Status */}
      {txHash && (
        <div className="bg-green-900/20 border border-green-500/30 rounded p-4">
          <h4 className="text-green-400 font-semibold mb-2">Transaction Successful!</h4>
          <p className="text-sm text-slate-300 mb-2">Hash:</p>
          <code className="text-xs bg-slate-900 p-2 rounded block mb-2 break-all">
            {txHash}
          </code>
          <a
            href={blockExplorerUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:underline text-sm"
          >
            View on Etherscan ↗
          </a>
        </div>
      )}

      {txError && (
        <div className="bg-red-900/20 border border-red-500/30 rounded p-3">
          <p className="text-red-400 text-sm">{txError}</p>
        </div>
      )}

      {/* Reset Button */}
      <button
        onClick={onReset}
        className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded font-semibold"
      >
        Request Another Loan
      </button>
    </div>
  );
}
```

### 6. Update App.tsx

**File**: `src/App.tsx`

```typescript
import { WalletProvider } from './context/WalletContext';
import { ConnectWallet } from './components/ConnectWallet';
import { WalletLoanRequest } from './components/WalletLoanRequest';

function App() {
  return (
    <WalletProvider>
      <div className="min-h-screen bg-slate-900 p-8">
        <div className="max-w-2xl mx-auto space-y-8">
          <h1 className="text-4xl font-bold text-white">AI Agent Credit System</h1>

          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-white">Step 1: Connect Wallet</h2>
            <ConnectWallet />
          </div>

          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-white">Step 2: Request Loan</h2>
            <WalletLoanRequest />
          </div>
        </div>
      </div>
    </WalletProvider>
  );
}

export default App;
```

---

## Testing

### Test Flow

1. **Install MetaMask**: https://metamask.io
2. **Add Sepolia Network**:
   - Network ID: 11155111
   - RPC: https://sepolia.infura.io/v3/
3. **Get Test ETH**: https://www.alchemy.com/faucets/ethereum-sepolia
4. **Start Backend**: `python -m uvicorn app.main:app --reload`
5. **Start Frontend**: `npm run dev`
6. **Test**:
   - Click "Connect MetaMask"
   - Enter loan amount
   - Click "Request Loan"
   - View decision
   - Click "Disburse Loan"
   - Approve transaction in MetaMask
   - See transaction hash

### Test Wallets

| Wallet | Expected Profile | Result |
|--------|-----------------|--------|
| Connect any wallet | Deterministic | Depends on wallet address |
| Multiple requests | Consistent | Same score every time |

---

## Configuration

### Environment Variables

**File**: `.env.local`

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_RECIPIENT_ADDRESS=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0
VITE_TESTNET_CHAIN_ID=0xaa36a7
```

---

## Production Considerations

1. **Change Recipient Address**: Use actual loan disbursement contract
2. **Use Stablecoins**: Replace ETH with USDC/USDT for real lending
3. **Implement Smart Contract**: Store loan agreements on-chain
4. **Add Real Verification**: Integrate KYC and compliance checks
5. **Secure Backend**: Use proper authentication and rate limiting

---

## Troubleshooting

### MetaMask Not Detected
- Ensure MetaMask extension is installed
- Check browser console for errors
- Try different browser if needed

### Transaction Fails
- Check account has enough testnet ETH
- Verify network is Sepolia
- Check gas prices

### Loan Not Approved
- This is correct behavior for weak wallets
- Try different wallet address
- Check wallet profile: GET `/loan/wallet/profile/{address}`

---

## Complete Integration Checklist

- ✅ Install ethers.js and wallet libraries
- ✅ Create wallet service for MetaMask interaction
- ✅ Create wallet context for state management
- ✅ Create connect wallet component
- ✅ Create loan request component
- ✅ Create loan decision display component
- ✅ Update App.tsx with full flow
- ✅ Configure environment variables
- ✅ Test end-to-end flow

---

## Summary

This integration enables:

1. **Wallet Connection**: MetaMask integration
2. **Deterministic Profiles**: Based on wallet address
3. **Real Loan Decisions**: From backend wallet system
4. **Blockchain Transactions**: Send testnet ETH
5. **End-to-End Demo**: Complete fintech + blockchain flow

Ready for hackathon demonstration! 🚀

