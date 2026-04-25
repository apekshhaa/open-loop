"""
Reputation Service

Manages agent reputation scoring, status classification, and behavioral metrics.
Implements the KYA (Know Your Agent) identity system.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class ReputationService:
    """
    Manages agent reputation and identity verification.
    
    Responsible for:
    - Calculating reputation scores from repayment history
    - Classifying agent status (Verified, Risky, New Agent)
    - Tracking behavioral metrics (activity, avg loan, transactions)
    """
    
    # Reputation thresholds
    VERIFIED_THRESHOLD = 70.0  # Score >= 70 for "Verified" status
    RISKY_THRESHOLD = 50.0     # Score < 50 for "Risky" status
    HIGH_ACTIVITY_MIN = 10     # 10+ transactions = high
    MEDIUM_ACTIVITY_MIN = 5    # 5-9 transactions = medium
    LOW_ACTIVITY_MIN = 1       # 1-4 transactions = low
    
    @staticmethod
    def calculate_reputation_score(
        successful_repays: int,
        total_loans: int
    ) -> float:
        """
        Calculate reputation score from repayment history.
        
        Formula: score = (successful_repays / total_loans) * 100
        
        Args:
            successful_repays: Number of successfully repaid loans
            total_loans: Total number of loans
        
        Returns:
            Reputation score (0-100)
        """
        if total_loans == 0:
            return 50.0  # Default score for new agents
        
        score = (successful_repays / total_loans) * 100
        return min(100.0, max(0.0, score))  # Clamp between 0-100
    
    @staticmethod
    def classify_agent_status(
        total_loans: int,
        reputation_score: float
    ) -> str:
        """
        Classify agent status based on loan history and reputation.
        
        Classification logic:
        - "New Agent": total_loans == 0
        - "Verified": total_loans > 0 AND score >= 70
        - "Risky": score < 50
        - "Established": all other cases
        
        Args:
            total_loans: Total number of loans
            reputation_score: Reputation score (0-100)
        
        Returns:
            Status string: "New Agent", "Verified", "Risky", or "Established"
        """
        if total_loans == 0:
            return "New Agent"
        elif reputation_score >= ReputationService.VERIFIED_THRESHOLD:
            return "Verified"
        elif reputation_score < ReputationService.RISKY_THRESHOLD:
            return "Risky"
        else:
            return "Established"
    
    @staticmethod
    def calculate_activity_level(transaction_count: int) -> str:
        """
        Calculate activity level based on transaction frequency.
        
        Activity levels:
        - "high": 10+ transactions
        - "medium": 5-9 transactions
        - "low": 1-4 transactions
        
        Args:
            transaction_count: Total number of transactions
        
        Returns:
            Activity level string: "high", "medium", or "low"
        """
        if transaction_count >= ReputationService.HIGH_ACTIVITY_MIN:
            return "high"
        elif transaction_count >= ReputationService.MEDIUM_ACTIVITY_MIN:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def calculate_approval_rate(
        approved_loans: int,
        total_loans: int
    ) -> float:
        """
        Calculate approval rate as percentage.
        
        Args:
            approved_loans: Number of approved loans
            total_loans: Total number of loans
        
        Returns:
            Approval rate (0-100)
        """
        if total_loans == 0:
            return 0.0
        return (approved_loans / total_loans) * 100
    
    @staticmethod
    def calculate_repayment_rate(
        successful_repays: int,
        total_loans: int
    ) -> float:
        """
        Calculate repayment rate as percentage.
        
        Args:
            successful_repays: Number of successfully repaid loans
            total_loans: Total number of loans
        
        Returns:
            Repayment rate (0-100)
        """
        if total_loans == 0:
            return 0.0
        return (successful_repays / total_loans) * 100
    
    @staticmethod
    def build_identity_profile(agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build comprehensive identity profile from agent data.
        
        Args:
            agent_data: Agent record from database
        
        Returns:
            Structured identity profile
        """
        wallet_address = agent_data.get("wallet_address", "")
        total_loans = agent_data.get("total_loans", 0)
        successful_repays = agent_data.get("successful_repays", 0)
        failed_loans = agent_data.get("failed_loans", 0)
        score = agent_data.get("trust_score", 50.0)
        transactions = agent_data.get("transactions", 0)
        activity = agent_data.get("activity", "low")
        avg_loan = agent_data.get("avg_loan", 0.0)
        created_at = agent_data.get("created_at", "")
        
        # Calculate rates
        repayment_rate = ReputationService.calculate_repayment_rate(successful_repays, total_loans)
        
        # Classify status
        status = ReputationService.classify_agent_status(total_loans, score)
        
        return {
            "wallet": wallet_address[:6] + "..." + wallet_address[-4:] if len(wallet_address) > 10 else wallet_address,
            "wallet_full": wallet_address,
            "score": round(score, 2),
            "status": status,
            "history": {
                "total_loans": total_loans,
                "successful_repays": successful_repays,
                "failed_loans": failed_loans,
                "repayment_rate": round(repayment_rate, 2),
            },
            "metrics": {
                "activity": activity,
                "transactions": transactions,
                "avg_loan": round(avg_loan, 2),
                "created_at": created_at,
            },
            "trust_level": ReputationService._calculate_trust_level(score, total_loans),
            "is_verified": status == "Verified"
        }
    
    @staticmethod
    def _calculate_trust_level(score: float, total_loans: int) -> str:
        """
        Calculate trust level descriptor.
        
        Args:
            score: Reputation score (0-100)
            total_loans: Total number of loans
        
        Returns:
            Trust level: "Unknown", "Low", "Fair", "Good", or "Excellent"
        """
        if total_loans == 0:
            return "Unknown"
        elif score < 25:
            return "Low"
        elif score < 50:
            return "Fair"
        elif score < 75:
            return "Good"
        else:
            return "Excellent"
    
    @staticmethod
    def get_risk_assessment(
        score: float,
        failed_loans: int,
        total_loans: int
    ) -> Dict[str, Any]:
        """
        Get risk assessment for agent.
        
        Args:
            score: Reputation score (0-100)
            failed_loans: Number of failed loans
            total_loans: Total number of loans
        
        Returns:
            Risk assessment with level and factors
        """
        if total_loans == 0:
            risk_level = "unknown"
            risk_score = 50  # Neutral for unknown agents
        elif score >= 80:
            risk_level = "low"
            risk_score = 20
        elif score >= 60:
            risk_level = "medium"
            risk_score = 50
        elif score >= 40:
            risk_level = "high"
            risk_score = 75
        else:
            risk_level = "critical"
            risk_score = 90
        
        # Adjust based on failure rate
        if total_loans > 0:
            failure_rate = (failed_loans / total_loans) * 100
            if failure_rate > 30:
                risk_score = min(100, risk_score + 20)
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "failed_loans": failed_loans,
            "total_loans": total_loans,
            "factors": [
                f"Reputation score: {score}",
                f"Failure rate: {(failed_loans / total_loans * 100) if total_loans > 0 else 0:.1f}%"
            ]
        }
