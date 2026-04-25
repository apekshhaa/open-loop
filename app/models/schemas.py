"""
Pydantic models for API requests and responses.

This module defines the data schemas for the AI Agent Credit System,
including loan requests, agent responses, and transaction structures.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LoanStatus(str, Enum):
    """Enum for loan application statuses."""
    PENDING = "pending"
    VERIFICATION = "verification"
    SCORING = "scoring"
    DECISION_PENDING = "decision_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FUNDED = "funded"
    COMPLETED = "completed"


class AgentStatus(str, Enum):
    """Enum for agent processing statuses."""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============== Request Models ==============

class LoanRequest(BaseModel):
    """
    Initial loan application request from borrower.
    
    Attributes:
        borrower_id: Unique identifier for the borrower
        amount: Loan amount requested
        duration_months: Loan duration in months
        purpose: Purpose of the loan
        credit_history: Optional credit history data
    """
    borrower_id: str = Field(..., description="Unique borrower identifier")
    amount: float = Field(..., gt=0, description="Loan amount in USD")
    duration_months: int = Field(..., gt=0, le=120, description="Loan duration")
    purpose: str = Field(..., description="Purpose of the loan")
    credit_history: Optional[Dict[str, Any]] = Field(None, description="Credit history data")


class CreditScoreRequest(BaseModel):
    """Request for credit scoring analysis."""
    borrower_id: str
    financial_data: Dict[str, Any]
    credit_history: Optional[Dict[str, Any]] = None


# ============== Response Models ==============

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Response timestamp")
    version: str = Field(..., description="API version")


class AgentResponse(BaseModel):
    """
    Response from individual agent processing.
    
    Attributes:
        agent_name: Name of the agent that processed
        status: Processing status
        result: Processing result/decision
        metadata: Additional metadata
        timestamp: When processing occurred
    """
    agent_name: str = Field(..., description="Name of the processing agent")
    status: AgentStatus = Field(..., description="Processing status")
    result: Dict[str, Any] = Field(..., description="Processing result")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CreditScoreResponse(BaseModel):
    """Response from credit analyst agent."""
    credit_score: float = Field(..., ge=0, le=850, description="Credit score (0-850)")
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    recommendation: str = Field(..., description="Analyst recommendation")
    factors: List[str] = Field(default_factory=list, description="Key factors considered")


class LoanApprovalResponse(BaseModel):
    """Response from loan decision agent."""
    decision: str = Field(..., description="Approval decision: approved, rejected")
    interest_rate: float = Field(..., ge=0, description="Interest rate if approved")
    approved_amount: float = Field(..., ge=0, description="Approved loan amount")
    conditions: Optional[List[str]] = Field(None, description="Loan conditions")


class LoanApplicationResponse(BaseModel):
    """
    Complete loan application response after all agents process.
    
    Attributes:
        loan_id: Unique loan application identifier
        borrower_id: Borrower identifier
        status: Current status of loan application
        gatekeeper_verified: Whether identity is verified
        credit_score: Assigned credit score
        decision: Loan approval decision
        timeline: Processing timeline
    """
    loan_id: str = Field(..., description="Unique loan identifier")
    borrower_id: str = Field(..., description="Borrower identifier")
    status: LoanStatus = Field(..., description="Loan application status")
    amount_requested: float = Field(..., description="Originally requested amount")
    gatekeeper_verified: bool = Field(False, description="Identity verification status")
    credit_score: Optional[float] = Field(None, description="Assigned credit score")
    decision: Optional[str] = Field(None, description="Loan decision")
    interest_rate: Optional[float] = Field(None, description="Interest rate if approved")
    approved_amount: Optional[float] = Field(None, description="Approved amount")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PipelineStatusResponse(BaseModel):
    """Response showing pipeline status at each stage."""
    loan_id: str
    stages: Dict[str, AgentResponse]
    overall_status: str
    completion_percentage: float = Field(ge=0, le=100)
