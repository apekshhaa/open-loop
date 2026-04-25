"""
Wallet-Based Gatekeeper Service

Handles identity verification using Ethereum wallet addresses.
Integrates with Supabase database for agent persistence and history tracking.
"""

from typing import Dict, Any
from datetime import datetime
from app.services.wallet_utils import (
    validate_wallet_address,
    normalize_wallet_address,
    generate_deterministic_profile,
    get_agent_status
)


class WalletGatekeeperService:
    """
    Wallet-based identity verification agent.
    
    Validates Ethereum wallet addresses, checks database for existing agents,
    and assigns deterministic profiles.
    """
    
    AGENT_NAME = "gatekeeper"
    
    @staticmethod
    def validate_wallet_identity(wallet_address: str) -> Dict[str, Any]:
        """
        Validate wallet address and generate agent profile.
        
        Args:
            wallet_address: Ethereum wallet address (0x...)
        
        Returns:
            Dict with validation status and agent profile
        """
        # Validate wallet format
        if not validate_wallet_address(wallet_address):
            return {
                "valid": False,
                "error": "Invalid wallet address format. Must be 0x... with 40 hex characters.",
                "wallet_address": wallet_address
            }
        
        # Normalize address (lowercase)
        normalized_address = normalize_wallet_address(wallet_address)
        
        # Generate deterministic profile from wallet address
        profile = generate_deterministic_profile(normalized_address)
        
        # Determine agent status
        agent_status = get_agent_status(profile["transaction_count"])
        
        # Return validation result with profile
        return {
            "valid": True,
            "wallet_address": normalized_address,
            "status": agent_status,  # "new" or "established"
            "success_rate": profile["success_rate"],
            "transaction_count": profile["transaction_count"],
            "repayment_history": profile["repayment_history"],
            "agent_tier": profile["agent_tier"],
            "message": f"Wallet {normalized_address[:6]}...{normalized_address[-4:]} verified as {agent_status} agent"
        }
    
    @staticmethod
    async def validate_wallet_identity_with_db(
        wallet_address: str,
        db_service
    ) -> Dict[str, Any]:
        """
        Validate wallet and get or create agent in database.
        
        This method:
        1. Validates wallet format
        2. Gets existing agent from DB or creates new one
        3. Returns validation result with database info
        
        Args:
            wallet_address: Ethereum wallet address (0x...)
            db_service: Supabase database service instance
        
        Returns:
            Dict with validation status, profile, and DB agent info
        """
        # Validate wallet format first
        if not validate_wallet_address(wallet_address):
            return {
                "valid": False,
                "error": "Invalid wallet address format. Must be 0x... with 40 hex characters.",
                "wallet_address": wallet_address
            }
        
        # Normalize address (lowercase)
        normalized_address = normalize_wallet_address(wallet_address)
        
        try:
            # Get or create agent in database
            db_agent = await db_service.get_or_create_agent(normalized_address)
            
            # Generate deterministic profile from wallet address
            profile = generate_deterministic_profile(normalized_address)
            
            # Determine agent status
            agent_status = get_agent_status(profile["transaction_count"])
            
            # Return validation result with both profile and DB data
            return {
                "valid": True,
                "wallet_address": normalized_address,
                "status": agent_status,  # "new" or "established"
                "success_rate": profile["success_rate"],
                "transaction_count": profile["transaction_count"],
                "repayment_history": profile["repayment_history"],
                "agent_tier": profile["agent_tier"],
                # Database info
                "db_agent_id": db_agent.get("id"),
                "db_trust_score": db_agent.get("trust_score", 50),
                "db_total_loans": db_agent.get("total_loans", 0),
                "db_created_at": db_agent.get("created_at"),
                "message": f"Wallet {normalized_address[:6]}...{normalized_address[-4:]} verified as {agent_status} agent"
            }
        
        except Exception as error:
            print(f"[Gatekeeper] Error validating wallet with DB: {str(error)}")
            return {
                "valid": False,
                "error": f"Database error during validation: {str(error)}",
                "wallet_address": normalized_address
            }


def create_wallet_gatekeeper_response(wallet_address: str) -> Dict[str, Any]:
    """
    Create a gatekeeper response for wallet-based identity.
    
    Args:
        wallet_address: Ethereum wallet address
    
    Returns:
        Gatekeeper response with validation result
    """
    return WalletGatekeeperService.validate_wallet_identity(wallet_address)
