export type AppScreen = 'portal' | 'console' | 'engine' | 'verdict' | 'execution' | 'ledger';

export interface AnalysisData {
  // Core input
  agentId: string;
  amount: number;
  
  // Credit analysis from backend
  creditScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'very_high' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  
  // Decision from backend
  approved: boolean;
  decisionReason: string;
  
  // Loan terms from backend
  interestRate: number;
  collateral: string; // formatted as USD string
  collateralRequired: number; // raw number
  monthlyPayment: number;
  totalInterest: number;
  
  // Optional
  rejectionReason?: string;
  message?: string;
  txHash?: string;
  
  // Agent profile
  agentProfile?: {
    successRate: number;
    transactionCount: number;
    repaymentHistory: number;
    agentTier: string;
  };
  
  // Pipeline status
  pipelineStatus?: {
    gatekeeper: string;
    analyst: string;
    decision: string;
    treasury: string;
  };
  
  // Backend metadata
  requestId?: string;
  timestamp?: string;
  fundsAvailable?: boolean;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  type?: 'info' | 'success' | 'error' | 'warning';
}

export interface ApiError {
  message: string;
  status?: number;
}

export interface WalletState {
  address: string;
  isConnected: boolean;
  chainId: string;
  isCorrectNetwork: boolean;
}

export type TransactionStatus = 'idle' | 'connecting' | 'switching_network' | 'signing' | 'broadcasting' | 'confirming' | 'success' | 'error';

export interface TransactionState {
  status: TransactionStatus;
  txHash: string;
  explorerUrl: string;
  error: string;
}
