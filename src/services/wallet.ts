/**
 * Wallet Service — MetaMask Integration for Sepolia Testnet
 *
 * All blockchain logic is isolated here. Components only call
 * these functions and never touch window.ethereum directly.
 */

import { BrowserProvider, JsonRpcSigner, parseEther, formatEther } from 'ethers';

// ── Sepolia network config ──────────────────────────────────────
const SEPOLIA_CHAIN_ID = '0xaa36a7'; // 11155111 in hex
const SEPOLIA_NETWORK = {
  chainId: SEPOLIA_CHAIN_ID,
  chainName: 'Sepolia Testnet',
  nativeCurrency: { name: 'Sepolia ETH', symbol: 'ETH', decimals: 18 },
  rpcUrls: ['https://rpc.sepolia.org'],
  blockExplorerUrls: ['https://sepolia.etherscan.io'],
};

// Hardcoded test recipient (burn address — safe for demos)
const DEFAULT_RECIPIENT = '0x000000000000000000000000000000000000dEaD';

// Small amount for demo transactions
const DEFAULT_AMOUNT_ETH = '0.001';

// ── Types ───────────────────────────────────────────────────────

export interface WalletInfo {
  address: string;
  provider: BrowserProvider;
  signer: JsonRpcSigner;
  chainId: string;
  isCorrectNetwork: boolean;
}

export interface TransactionResult {
  success: boolean;
  txHash: string;
  explorerUrl: string;
  error?: string;
}

// ── Helpers ─────────────────────────────────────────────────────

/**
 * Truncate an Ethereum address for UI display.
 * e.g. 0x71C7…3fA2
 */
export function formatAddress(address: string): string {
  if (!address) return '';
  return `${address.slice(0, 6)}…${address.slice(-4)}`;
}

/**
 * Build Sepolia Etherscan link for a transaction hash.
 */
export function getExplorerUrl(txHash: string): string {
  return `https://sepolia.etherscan.io/tx/${txHash}`;
}

/**
 * Check whether MetaMask (or another injected provider) is available.
 */
export function isMetaMaskAvailable(): boolean {
  return typeof window !== 'undefined' && typeof window.ethereum !== 'undefined';
}

// ── Core Wallet Functions ───────────────────────────────────────

/**
 * Connect to MetaMask wallet.
 *
 * 1. Requests account access
 * 2. Creates ethers provider + signer
 * 3. Checks the current network
 *
 * Throws descriptive errors for:
 *   - MetaMask not installed
 *   - User rejected the connection request
 */
export async function connectWallet(): Promise<WalletInfo> {
  if (!isMetaMaskAvailable()) {
    throw new Error(
      'MetaMask is not installed. Please install the MetaMask browser extension to continue.'
    );
  }

  try {
    // Request accounts — this triggers the MetaMask popup
    await window.ethereum!.request({ method: 'eth_requestAccounts' });

    const provider = new BrowserProvider(window.ethereum!);
    const signer = await provider.getSigner();
    const address = await signer.getAddress();
    const network = await provider.getNetwork();
    const chainId = '0x' + network.chainId.toString(16);
    const isCorrectNetwork = chainId.toLowerCase() === SEPOLIA_CHAIN_ID.toLowerCase();

    return { address, provider, signer, chainId, isCorrectNetwork };
  } catch (err: any) {
    if (err.code === 4001) {
      throw new Error('Wallet connection was rejected. Please approve the MetaMask request.');
    }
    throw new Error(`Failed to connect wallet: ${err.message || err}`);
  }
}

/**
 * Prompt MetaMask to switch to Sepolia testnet.
 * If Sepolia isn't added yet, it will add the network first.
 */
export async function switchToSepolia(): Promise<void> {
  if (!isMetaMaskAvailable()) {
    throw new Error('MetaMask is not installed.');
  }

  try {
    await window.ethereum!.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId: SEPOLIA_CHAIN_ID }],
    });
  } catch (err: any) {
    // Error 4902 = chain not added yet
    if (err.code === 4902) {
      try {
        await window.ethereum!.request({
          method: 'wallet_addEthereumChain',
          params: [SEPOLIA_NETWORK],
        });
      } catch (addErr: any) {
        throw new Error(`Failed to add Sepolia network: ${addErr.message || addErr}`);
      }
    } else {
      throw new Error(`Failed to switch to Sepolia: ${err.message || err}`);
    }
  }
}

/**
 * Send a small test ETH transaction on Sepolia.
 *
 * @param signer  – ethers JsonRpcSigner from connectWallet()
 * @param amount  – amount in ETH (default 0.001)
 * @returns TransactionResult with hash and explorer link
 *
 * Handles errors:
 *   - User rejects the transaction
 *   - Insufficient balance
 *   - Network issues
 */
export async function sendDisbursement(
  signer: JsonRpcSigner,
  amount: string = DEFAULT_AMOUNT_ETH
): Promise<TransactionResult> {
  try {
    const tx = await signer.sendTransaction({
      to: DEFAULT_RECIPIENT,
      value: parseEther(amount),
    });

    // Wait for 1 confirmation
    const receipt = await tx.wait(1);

    const txHash = receipt?.hash || tx.hash;

    return {
      success: true,
      txHash,
      explorerUrl: getExplorerUrl(txHash),
    };
  } catch (err: any) {
    // User rejected the transaction
    if (err.code === 'ACTION_REJECTED' || err.code === 4001) {
      return {
        success: false,
        txHash: '',
        explorerUrl: '',
        error: 'Transaction was rejected by user.',
      };
    }

    // Insufficient funds
    if (err.message?.includes('insufficient funds') || err.code === 'INSUFFICIENT_FUNDS') {
      return {
        success: false,
        txHash: '',
        explorerUrl: '',
        error: 'Insufficient Sepolia ETH balance. Get free test ETH from a Sepolia faucet.',
      };
    }

    return {
      success: false,
      txHash: '',
      explorerUrl: '',
      error: `Transaction failed: ${err.message || err}`,
    };
  }
}

/**
 * Get wallet balance in ETH.
 */
export async function getBalance(provider: BrowserProvider, address: string): Promise<string> {
  const balance = await provider.getBalance(address);
  return formatEther(balance);
}

// ── Global type augmentation for window.ethereum ────────────────
declare global {
  interface Window {
    ethereum?: any;
  }
}
