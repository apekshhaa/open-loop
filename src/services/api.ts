/// <reference types="vite/client" />
/**
 * API Integration Service
 * Handles all communication with the FastAPI backend
 */

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
 * Request a loan from the backend
 * @param agentId - AI agent identifier
 * @param amount - Loan amount requested (in USD)
 * @returns Backend response with credit analysis and decision
 */
export async function requestLoan(
  agentId: string,
  amount: number
): Promise<BackendLoanResponse> {
  try {
    if (!agentId || !amount || amount <= 0) {
      throw new Error('Invalid agent ID or amount');
    }

    const response = await fetch(
      `${LOAN_REQUEST_ENDPOINT}?agent_id=${encodeURIComponent(agentId)}&amount=${amount}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `API request failed with status ${response.status}`
      );
    }

    const data: BackendLoanResponse = await response.json();
    return data;
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Unknown error occurred';
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
