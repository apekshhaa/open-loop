"""
Database models/schema definitions.

Currently serves as placeholder for database collections/tables.
Will be expanded with actual ORM models when database is integrated.
"""

from typing import Optional, Dict, Any
from datetime import datetime


class LoanApplicationDB:
    """
    Database model for loan applications.
    
    This placeholder demonstrates the structure that will be stored
    in MongoDB, Supabase, or other persistence layer.
    """
    
    def __init__(
        self,
        loan_id: str,
        borrower_id: str,
        amount: float,
        duration_months: int,
        purpose: str,
        status: str = "pending",
        gatekeeper_verified: bool = False,
        credit_score: Optional[float] = None,
        decision: Optional[str] = None,
        interest_rate: Optional[float] = None,
        approved_amount: Optional[float] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        agent_responses: Optional[Dict[str, Any]] = None
    ):
        self.loan_id = loan_id
        self.borrower_id = borrower_id
        self.amount = amount
        self.duration_months = duration_months
        self.purpose = purpose
        self.status = status
        self.gatekeeper_verified = gatekeeper_verified
        self.credit_score = credit_score
        self.decision = decision
        self.interest_rate = interest_rate
        self.approved_amount = approved_amount
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.agent_responses = agent_responses or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for database storage."""
        return {
            "loan_id": self.loan_id,
            "borrower_id": self.borrower_id,
            "amount": self.amount,
            "duration_months": self.duration_months,
            "purpose": self.purpose,
            "status": self.status,
            "gatekeeper_verified": self.gatekeeper_verified,
            "credit_score": self.credit_score,
            "decision": self.decision,
            "interest_rate": self.interest_rate,
            "approved_amount": self.approved_amount,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "agent_responses": self.agent_responses
        }


class AuditLogDB:
    """Database model for audit logs."""
    
    def __init__(
        self,
        log_id: str,
        loan_id: str,
        agent_name: str,
        action: str,
        details: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        self.log_id = log_id
        self.loan_id = loan_id
        self.agent_name = agent_name
        self.action = action
        self.details = details
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for database storage."""
        return {
            "log_id": self.log_id,
            "loan_id": self.loan_id,
            "agent_name": self.agent_name,
            "action": self.action,
            "details": self.details,
            "timestamp": self.timestamp
        }
