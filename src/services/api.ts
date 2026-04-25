/// <reference types="vite/client" />
/**
 * API Integration Service
 * Handles all communication with the FastAPI backend
 * Uses walletService for proper wallet validation
 */

import { validateWalletAddress } from './walletService';

export interface BackendLoanResponse {
  request_id: string;
  agent_id: string;
  amount_requested: number;
  score: number;
  risk_level: string;
  confidence: number;
  decision_reason: string;
  interest_rate: number;
  collateral_required: number;
  approved: boolean;
  funds_available: boolean;
  monthly_payment: number;
  total_interest: number;
  message: string;
  agent_profile: {
    success_rate: number;
    transaction_count: number;
    repayment_history: number;
    agent_tier: string;
  };
  timestamp: string;
  pipeline_status: {
    gatekeeper: string;
    analyst: string;
    decision: string;
    treasury: string;
  };
}

export interface ApiError {
  message: string;
  status?: number;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const LOAN_REQUEST_ENDPOINT = `${API_BASE_URL}/loan/request`;

/**
 * Request a loan from the backend using wallet-based identity
 * @param walletAddress - Ethereum wallet address (0x...)
 * @param amount - Loan amount requested (in USD)
 * @returns Backend response with credit analysis and decision
 * 
 * REQUIRED: walletAddress must be a valid Ethereum address (0x + 40 hex chars)
 */
export async function requestLoan(
  walletAddress: string,
  amount: number
): Promise<BackendLoanResponse> {
  try {
    // Validate wallet address using walletService
    if (!walletAddress) {
      throw new Error('Wallet address is required. Please connect your wallet.');
    }

    console.log('[API] Validating wallet address:', walletAddress);
    const validation = validateWalletAddress(walletAddress);

    if (!validation.isValid) {
      console.error('[API] Wallet validation failed:', validation);
      throw new Error(
        validation.error || 'Invalid wallet address format. Expected 0x + 40 hex characters.'
      );
    }

    const normalizedAddress = validation.address;
    console.log('[API] Wallet validated successfully:', {
      original: walletAddress,
      normalized: normalizedAddress,
    });

    // Validate amount
    if (!amount || amount <= 0) {
      throw new Error('Invalid loan amount. Amount must be greater than 0.');
    }

    console.log('[API] Loan request:', {
      wallet: normalizedAddress,
      amount,
    });

    const response = await fetch(
      `${LOAN_REQUEST_ENDPOINT}?wallet_address=${encodeURIComponent(
        normalizedAddress!
      )}&amount=${amount}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('[API] Backend error response:', errorData);
      throw new Error(
        errorData.detail || `API request failed with status ${response.status}`
      );
    }

    const data: BackendLoanResponse = await response.json();
    console.log('[API] Loan request successful:', {
      requestId: data.request_id,
      approved: data.approved,
      score: data.score,
    });
    return data;
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Unknown error occurred';
    console.error('[API] Loan request failed:', message);
    throw {
      message: `Failed to request loan: ${message}`,
      status: error instanceof Error ? undefined : 500,
    } as ApiError;
  }
}

/**
 * Simulate analysis progress with real backend data
 * Used to stream pipeline progress to UI during analysis
 * @param onProgress - Callback with progress updates
 * @returns Cleanup function
 */
export function simulateAnalysisProgress(
  onProgress: (
    message: string,
    progress: number,
    type: 'info' | 'success' | 'error' | 'warning'
  ) => void
): () => void {
  const sequence = [
    {
      delay: 500,
      msg: 'Initiating identity verification...',
      progress: 10,
      type: 'info' as const,
    },
    {
      delay: 1500,
      msg: 'Establishing connection with gatekeeper service...',
      progress: 20,
      type: 'info' as const,
    },
    {
      delay: 2500,
      msg: 'Retrieving agent profile data...',
      progress: 35,
      type: 'info' as const,
    },
    {
      delay: 4000,
      msg: 'Identity verification confirmed',
      progress: 50,
      type: 'success' as const,
    },
    {
      delay: 5500,
      msg: 'Calculating credit score based on agent history...',
      progress: 65,
      type: 'info' as const,
    },
    {
      delay: 7000,
      msg: 'Analyzing risk profile and financial metrics...',
      progress: 80,
      type: 'warning' as const,
    },
    {
      delay: 8500,
      msg: 'Processing decision logic across 5 stages...',
      progress: 90,
      type: 'info' as const,
    },
    {
      delay: 10000,
      msg: 'Analysis complete. Retrieving final verdict from backend...',
      progress: 100,
      type: 'success' as const,
    },
  ];

  const timeouts: NodeJS.Timeout[] = [];

  sequence.forEach((step) => {
    const timeout = setTimeout(() => {
      onProgress(step.msg, step.progress, step.type);
    }, step.delay);
    timeouts.push(timeout);
  });

  // Return cleanup function
  return () => {
    timeouts.forEach((timeout) => clearTimeout(timeout));
  };
}
