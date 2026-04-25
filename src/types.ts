export type AppScreen = 'portal' | 'console' | 'engine' | 'verdict' | 'execution' | 'ledger';

export interface AnalysisData {
  agentId: string;
  allocation: string;
  creditScore: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  interestRate: string;
  collateral: string;
  approved: boolean;
  rejectionReason?: string;
  txHash?: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  type?: 'info' | 'success' | 'error' | 'warning';
}
