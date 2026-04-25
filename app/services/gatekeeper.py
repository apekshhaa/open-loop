"""
Gatekeeper Service - Identity Verification Agent

Responsible for verifying the identity and authenticity of loan applicants.
This is the first stage in the lending pipeline.

Functions:
    - Verify borrower identity
    - Validate KYC (Know Your Customer) data
    - Check for fraud indicators
    - Determine verification status
"""

from typing import Dict, Any, Tuple
from app.models import AgentResponse, AgentStatus
from datetime import datetime


# ============================================================
# DETERMINISTIC TIER PROFILES
# These fixed profiles are shared between gatekeeper and analyst
# to ensure consistent, predictable scoring across the pipeline.
# ============================================================
TIER_PROFILES = {
    "strong": {
        "success_rate": 0.92,
        "transaction_count": 48,
        "repayment_history": 0.98,
    },
    "average": {
        "success_rate": 0.75,
        "transaction_count": 28,
        "repayment_history": 0.80,
    },
    "weak": {
        "success_rate": 0.45,
        "transaction_count": 8,
        "repayment_history": 0.55,
    },
}


def _get_agent_tier(agent_id: str) -> str:
    """
    Determine agent tier based on agent_id.
    ALWAYS returns the same tier for the same agent_id.

    Rules:
        agent_id ending in "1" → "strong"  (scores 80-90, low risk)
        agent_id ending in "2" → "average" (scores 55-70, medium risk)
        anything else          → "weak"    (scores 30-50, high risk)
    """
    if agent_id.endswith("1"):
        return "strong"
    elif agent_id.endswith("2"):
        return "average"
    else:
        return "weak"


class GatekeeperService:
    """
    Identity verification agent for loan applicants.
    
    This service simulates the gatekeeper role, responsible for initial
    identity verification and KYC compliance checks.
    """
    
    AGENT_NAME = "gatekeeper"
    
    # Mock database of valid agents
    VALID_AGENTS = {
        "AGENT-001": {"name": "AI Agent 1", "active": True},
        "AGENT-002": {"name": "AI Agent 2", "active": True},
        "AGENT-003": {"name": "AI Agent 3", "active": True},
        "AGENT-TEST": {"name": "Test Agent", "active": True},
    }
    
    @staticmethod
    def verify_identity(borrower_id: str, kyc_data: Dict[str, Any]) -> AgentResponse:
        """
        Verify borrower identity and KYC compliance.
        
        Args:
            borrower_id: Unique identifier for the borrower
            kyc_data: KYC (Know Your Customer) verification data
        
        Returns:
            AgentResponse with verification result
        
        TODO: Implement actual KYC verification:
            - Connect to identity verification APIs (Veriff, IDology, etc.)
            - Validate government ID documents
            - Check against fraud databases
            - Verify current address
            - Cross-reference with sanctions lists
        """
        try:
            # Placeholder verification logic
            is_verified = _validate_kyc_data(kyc_data)
            fraud_score = _calculate_fraud_score(borrower_id, kyc_data)
            
            if is_verified and fraud_score < 0.3:
                status = AgentStatus.COMPLETED
                result = {
                    "verified": True,
                    "fraud_score": fraud_score,
                    "verification_method": "document_based",
                    "confidence": 0.95
                }
            else:
                status = AgentStatus.FAILED
                result = {
                    "verified": False,
                    "fraud_score": fraud_score,
                    "reason": "Identity verification failed"
                }
            
            return AgentResponse(
                agent_name=GatekeeperService.AGENT_NAME,
                status=status,
                result=result,
                metadata={"borrower_id": borrower_id}
            )
        
        except Exception as e:
            return _create_error_response(str(e))
    
    @staticmethod
    def validate_agent_identity(agent_id: str) -> Dict[str, Any]:
        """
        Validate if an agent is registered and active.
        Creates deterministic tier-based profiles for any agent_id.

        DETERMINISTIC RULES (no randomness):
            agent_id ending in "1" → strong tier (high success, many txns)
            agent_id ending in "2" → average tier (moderate metrics)
            anything else          → weak tier (low metrics)

        Same agent_id ALWAYS returns identical profile data.

        Args:
            agent_id: Unique identifier for the AI agent

        Returns:
            Dict with validation status and agent details
        """

        if agent_id not in GatekeeperService.VALID_AGENTS:
            # Assign a DETERMINISTIC tier-based profile
            tier = _get_agent_tier(agent_id)
            profile = TIER_PROFILES[tier]

            GatekeeperService.VALID_AGENTS[agent_id] = {
                "name": f"AI Agent {agent_id}",
                "active": True,
                "tier": tier,
                "success_rate": profile["success_rate"],
                "transaction_count": profile["transaction_count"],
                "repayment_history": profile["repayment_history"],
            }

        agent = GatekeeperService.VALID_AGENTS[agent_id]

        return {
            "valid": True,
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "status": "active",
            "success_rate": agent.get("success_rate", 0.70),
            "transaction_count": agent.get("transaction_count", 0),
            "repayment_history": agent.get("repayment_history", 0.70),
            "message": f"Agent {agent_id} successfully verified"
        }
    
    @staticmethod
    def check_sanctions_list(borrower_id: str, borrower_name: str) -> AgentResponse:
        """
        Check if borrower appears on sanctions lists.
        
        Args:
            borrower_id: Borrower identifier
            borrower_name: Borrower name to check
        
        Returns:
            AgentResponse with sanctions check result
        
        TODO: Implement actual sanctions checking:
            - Check OFAC (Office of Foreign Assets Control) lists
            - Verify against international sanctions databases
            - Cross-reference with PEP (Politically Exposed Person) lists
        """
        try:
            is_sanctioned = _check_sanctions_database(borrower_name)
            
            return AgentResponse(
                agent_name=GatekeeperService.AGENT_NAME,
                status=AgentStatus.COMPLETED,
                result={
                    "sanctioned": is_sanctioned,
                    "databases_checked": ["OFAC", "EU_SANCTIONS"]
                },
                metadata={"borrower_id": borrower_id}
            )
        except Exception as e:
            return _create_error_response(str(e))


def _validate_kyc_data(kyc_data: Dict[str, Any]) -> bool:
    """Validate KYC data structure and completeness."""
    required_fields = ["name", "email", "phone", "address"]
    return all(field in kyc_data for field in required_fields)


def _calculate_fraud_score(borrower_id: str, kyc_data: Dict[str, Any]) -> float:
    """
    Calculate fraud risk score (0.0 to 1.0).
    
    TODO: Implement machine learning model for fraud detection
    """
    return 0.1  # Placeholder score


def _check_sanctions_database(borrower_name: str) -> bool:
    """
    Check against sanctions database.
    
    TODO: Connect to actual sanctions APIs
    """
    return False  # Placeholder - assume not sanctioned


def _create_error_response(error_message: str) -> AgentResponse:
    """Create error response."""
    return AgentResponse(
        agent_name=GatekeeperService.AGENT_NAME,
        status=AgentStatus.FAILED,
        result={"error": error_message}
    )
