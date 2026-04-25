/**
 * Wallet Service - Ethereum wallet validation and MetaMask integration
 * Uses ethers.js for robust validation that handles checksum addresses,
 * lowercase, and mixed-case addresses correctly.
 */

import { getAddress } from 'ethers';

export interface MetaMaskProvider {
  request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
  on?: (event: string, callback: (args: unknown) => void) => void;
}

export interface WalletValidationResult {
  isValid: boolean;
  address: string | null;
  error: string | null;
  reason?: string;
}

/**
 * Validate Ethereum wallet address using ethers.js
 * Handles checksum, lowercase, and mixed-case addresses
 * @param address - Wallet address to validate
 * @returns Validation result with normalized address or error
 */
export function validateWalletAddress(address: string): WalletValidationResult {
  try {
    // Trim whitespace first
    const trimmedAddress = address.trim();
    
    // Log for debugging
    console.log('[WalletService] Validating address:', {
      original: address,
      trimmed: trimmedAddress,
      length: trimmedAddress.length,
    });

    // Check if address is empty
    if (!trimmedAddress) {
      console.warn('[WalletService] Address is empty');
      return {
        isValid: false,
        address: null,
        error: 'Wallet address is required',
        reason: 'Address is empty or only whitespace',
      };
    }

    // Use ethers.js to validate and normalize the address
    // getAddress() handles checksum validation and normalization
    const normalizedAddress = getAddress(trimmedAddress);

    console.log('[WalletService] Address validated successfully:', {
      original: trimmedAddress,
      normalized: normalizedAddress,
    });

    return {
      isValid: true,
      address: normalizedAddress,
      error: null,
      reason: 'Valid Ethereum address',
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('[WalletService] Validation failed:', {
      address,
      error: errorMessage,
    });

    return {
      isValid: false,
      address: null,
      error: errorMessage,
      reason: 'Address failed ethers.js validation',
    };
  }
}

/**
 * Check if MetaMask is available
 * @returns true if MetaMask is installed
 */
export function isMetaMaskAvailable(): boolean {
  if (typeof window === 'undefined') {
    console.log('[WalletService] Running in non-browser environment');
    return false;
  }

  const isAvailable =
    (window.ethereum as MetaMaskProvider | undefined)?.request !== undefined;
  
  if (isAvailable) {
    console.log('[WalletService] MetaMask detected');
  } else {
    console.warn('[WalletService] MetaMask not found in window.ethereum');
  }

  return isAvailable;
}

/**
 * Connect to MetaMask wallet
 * @returns Promise resolving to connected wallet address
 */
export async function connectMetaMask(): Promise<string> {
  if (!isMetaMaskAvailable()) {
    throw new Error('MetaMask is not installed. Please install MetaMask to continue.');
  }

  try {
    console.log('[WalletService] Requesting MetaMask accounts...');
    
    const ethereum = window.ethereum as MetaMaskProvider;
    const accounts = (await ethereum.request({
      method: 'eth_requestAccounts',
    })) as string[];

    if (!accounts || accounts.length === 0) {
      throw new Error('No accounts returned from MetaMask');
    }

    const connectedAddress = accounts[0];
    console.log('[WalletService] MetaMask connection successful:', {
      address: connectedAddress,
      accountCount: accounts.length,
    });

    // Validate the address we got from MetaMask
    const validation = validateWalletAddress(connectedAddress);
    if (!validation.isValid) {
      throw new Error(
        `MetaMask returned invalid address: ${validation.error}`
      );
    }

    return validation.address!;
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : 'Failed to connect MetaMask';
    console.error('[WalletService] MetaMask connection failed:', errorMessage);
    throw new Error(errorMessage);
  }
}

/**
 * Get currently connected MetaMask account (if any)
 * @returns Promise resolving to wallet address or null
 */
export async function getConnectedAccount(): Promise<string | null> {
  if (!isMetaMaskAvailable()) {
    console.log('[WalletService] MetaMask not available, returning null');
    return null;
  }

  try {
    const ethereum = window.ethereum as MetaMaskProvider;
    const accounts = (await ethereum.request({
      method: 'eth_accounts',
    })) as string[];

    if (accounts && accounts.length > 0) {
      console.log('[WalletService] Found connected account:', accounts[0]);
      return accounts[0];
    }

    console.log('[WalletService] No connected accounts found');
    return null;
  } catch (error) {
    console.error('[WalletService] Error getting connected account:', error);
    return null;
  }
}

/**
 * Disconnect MetaMask wallet
 * (Note: MetaMask doesn't have a native disconnect method, so we just clear local state)
 */
export function disconnectMetaMask(): void {
  console.log('[WalletService] Disconnecting wallet (clearing local state)');
  // MetaMask doesn't support programmatic disconnect
  // Clear is handled in component state management
}

/**
 * Format wallet address for display (shortened)
 * @param address - Full wallet address
 * @param chars - Number of characters to show from start and end
 * @returns Formatted address like 0x1234...5678
 */
export function formatAddressForDisplay(address: string, chars = 4): string {
  if (!address || address.length < 10) {
    return address;
  }
  return `${address.slice(0, chars + 2)}...${address.slice(-chars)}`;
}

/**
 * Setup MetaMask event listeners for account/chain changes
 * @param onAccountChanged - Callback when account changes
 * @param onChainChanged - Callback when chain changes
 */
export function setupMetaMaskListeners(
  onAccountChanged?: (accounts: string[]) => void,
  onChainChanged?: (chainId: string) => void
): () => void {
  if (!isMetaMaskAvailable()) {
    console.warn(
      '[WalletService] MetaMask not available, skipping listener setup'
    );
    return () => {};
  }

  const ethereum = window.ethereum as MetaMaskProvider;

  const handleAccountsChanged = (accounts: unknown) => {
    console.log('[WalletService] MetaMask accounts changed:', accounts);
    if (onAccountChanged) {
      onAccountChanged((accounts as string[]) || []);
    }
  };

  const handleChainChanged = (chainId: unknown) => {
    console.log('[WalletService] MetaMask chain changed:', chainId);
    if (onChainChanged) {
      onChainChanged((chainId as string) || '');
    }
  };

  if (ethereum.on) {
    ethereum.on('accountsChanged', handleAccountsChanged);
    ethereum.on('chainChanged', handleChainChanged);
  }

  // Return cleanup function
  return () => {
    console.log('[WalletService] Removing MetaMask listeners');
    // Note: MetaMask doesn't provide an 'off' method in all versions
    // We rely on component unmounting for cleanup
  };
}
