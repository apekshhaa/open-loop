"""
Wallet Utility Functions for Deterministic Profile Generation

This module provides deterministic profile generation from Ethereum wallet addresses.
Since there's no database, profiles are generated consistently from wallet hashes.
"""

import hashlib
from typing import Dict, Any


def validate_wallet_address(wallet_address: str) -> bool:
    """
    Validate Ethereum wallet address format.
    
    Args:
        wallet_address: Ethereum address string
    
    Returns:
        True if valid format, False otherwise
    """
    if not wallet_address:
        return False
    
    # Ethereum addresses are 42 characters: 0x + 40 hex characters
    if len(wallet_address) != 42:
        return False
    
    if not wallet_address.startswith("0x"):
        return False
    
    # Check if remaining 40 characters are valid hex
    try:
        int(wallet_address[2:], 16)
        return True
    except ValueError:
        return False


def normalize_wallet_address(wallet_address: str) -> str:
    """
    Normalize wallet address to lowercase.
    
    Args:
        wallet_address: Ethereum address (any case)
    
    Returns:
        Normalized lowercase address
    """
    return wallet_address.lower()


def generate_deterministic_profile(wallet_address: str) -> Dict[str, Any]:
    """
    Generate a deterministic agent profile from a wallet address.
    
    Same wallet always produces the same profile.
    Different wallets produce different profiles with realistic variation.
    
    Args:
        wallet_address: Ethereum wallet address (lowercase)
    
    Returns:
        Dict with:
        - success_rate (0-100%)
        - transaction_count (0-50)
        - repayment_history (0-100%)
        - agent_tier ("low" / "medium" / "high")
    """
    # Normalize address
    normalized = normalize_wallet_address(wallet_address)
    
    # Create deterministic hash from wallet address
    # Using SHA256 to get 64-char hex string
    wallet_hash = hashlib.sha256(normalized.encode()).hexdigest()
    
    # Extract deterministic values from hash segments
    # This ensures same wallet always gets same values
    
    # Segment 1: success_rate (50-95%)
    hash_segment_1 = int(wallet_hash[0:8], 16)
    success_rate = 50 + (hash_segment_1 % 46)  # 50-95%
    
    # Segment 2: transaction_count (2-48)
    hash_segment_2 = int(wallet_hash[8:16], 16)
    transaction_count = 2 + (hash_segment_2 % 47)  # 2-48
    
    # Segment 3: repayment_history (55-100%)
    hash_segment_3 = int(wallet_hash[16:24], 16)
    repayment_history = 55 + (hash_segment_3 % 46)  # 55-100%
    
    # Segment 4: agent_tier (based on combined score)
    hash_segment_4 = int(wallet_hash[24:32], 16)
    combined_score = success_rate + transaction_count + repayment_history
    
    if combined_score > 200:
        agent_tier = "high"
    elif combined_score > 140:
        agent_tier = "medium"
    else:
        agent_tier = "low"
    
    return {
        "success_rate": success_rate / 100.0,  # Convert to 0.0-1.0
        "transaction_count": transaction_count,
        "repayment_history": repayment_history / 100.0,  # Convert to 0.0-1.0
        "agent_tier": agent_tier,
        "wallet_address": wallet_address,
        "created_at": None  # Stateless, no creation time
    }


def get_agent_status(transaction_count: int) -> str:
    """
    Determine agent status based on transaction count.
    
    Args:
        transaction_count: Number of transactions
    
    Returns:
        "new" if limited history, "established" if good history
    """
    return "established" if transaction_count > 10 else "new"


def get_wallet_summary(wallet_address: str) -> Dict[str, Any]:
    """
    Get a summary of wallet-based agent profile.
    
    Args:
        wallet_address: Ethereum wallet address
    
    Returns:
        Summary dict with all profile details
    """
    profile = generate_deterministic_profile(wallet_address)
    
    return {
        "wallet_address": wallet_address,
        "success_rate": profile["success_rate"],
        "transaction_count": profile["transaction_count"],
        "repayment_history": profile["repayment_history"],
        "agent_tier": profile["agent_tier"],
        "agent_status": get_agent_status(profile["transaction_count"]),
        "profile_hash": hashlib.sha256(wallet_address.lower().encode()).hexdigest()[:16]
    }
