"""
Decision Service - Loan Approval Decision Agent

Responsible for making final loan approval/rejection decisions based on
analysis from other agents (gatekeeper, analyst, treasury).

Functions:
    - Make approval/rejection decision
    - Determine interest rates
    - Set loan terms
    - Apply risk adjustments
"""

from typing import Dict, Any
from app.models import AgentResponse, AgentStatus, LoanApprovalResponse
from datetime import datetime


class DecisionService:
    """
    Loan approval decision-making agent.
    
    This service makes final approval decisions by evaluating all
    pipeline stage results with configurable decision rules.
    """
    
    AGENT_NAME = "decision"
    
    # Interest rate tiers based on credit score
    INTEREST_RATE_TIERS = {
        "excellent": {"min_score": 750, "base_rate": 0.045},
        "good": {"min_score": 670, "base_rate": 0.065},
        "fair": {"min_score": 580, "base_rate": 0.095},
        "poor": {"min_score": 0, "base_rate": 0.125}
    }
    
    @staticmethod
    def make_decision(
        borrower_id: str,
        loan_amount: float,
        credit_score: float,
        gatekeeper_verified: bool,
        debt_to_income: float,
        pipeline_data: Dict[str, Any]
    ) -> AgentResponse:
        """
        Make final loan approval decision.
        
        Args:
            borrower_id: Borrower identifier
            loan_amount: Requested loan amount
            credit_score: Credit score from analyst
            gatekeeper_verified: Whether identity is verified
            debt_to_income: Debt-to-income ratio
            pipeline_data: Complete pipeline data for decision context
        
        Returns:
            AgentResponse with approval decision and terms
        
        TODO: Implement advanced decision logic:
            - Machine learning model for approval prediction
            - Dynamic interest rate calculation
            - Risk-adjusted pricing
            - Portfolio diversification considerations
            - Regulatory compliance checks
        """
        try:
            # Check decision criteria
            decision, approval_amount = _evaluate_criteria(
                credit_score, gatekeeper_verified, debt_to_income, loan_amount
            )
            
            if decision == "approved":
                interest_rate = _calculate_interest_rate(credit_score, debt_to_income)
                conditions = _generate_loan_conditions(credit_score, debt_to_income)
                status = AgentStatus.COMPLETED
                
                result = {
                    "decision": decision,
                    "approved_amount": approval_amount,
                    "interest_rate": interest_rate,
                    "conditions": conditions,
                    "approval_reason": "All criteria met"
                }
            else:
                status = AgentStatus.COMPLETED
                result = {
                    "decision": decision,
                    "approved_amount": 0,
                    "rejection_reason": _get_rejection_reason(
                        credit_score, gatekeeper_verified, debt_to_income
                    )
                }
            
            return AgentResponse(
                agent_name=DecisionService.AGENT_NAME,
                status=status,
                result=result,
                metadata={"borrower_id": borrower_id}
            )
        
        except Exception as e:
            return _create_error_response(str(e))
    
    @staticmethod
    def calculate_loan_terms(
        approval_amount: float,
        interest_rate: float,
        duration_months: int
    ) -> AgentResponse:
        """
        Calculate detailed loan terms and amortization.
        
        Args:
            approval_amount: Approved loan amount
            interest_rate: Annual interest rate
            duration_months: Loan duration in months
        
        Returns:
            AgentResponse with loan terms
        
        TODO: Implement:
            - Amortization schedule generation
            - Monthly payment calculation
            - Total interest calculation
            - Payment breakdown details
        """
        try:
            monthly_rate = interest_rate / 12
            num_payments = duration_months
            
            # Calculate monthly payment using amortization formula
            if monthly_rate > 0:
                monthly_payment = approval_amount * (
                    monthly_rate * (1 + monthly_rate) ** num_payments
                ) / ((1 + monthly_rate) ** num_payments - 1)
            else:
                monthly_payment = approval_amount / num_payments
            
            total_interest = (monthly_payment * num_payments) - approval_amount
            
            return AgentResponse(
                agent_name=DecisionService.AGENT_NAME,
                status=AgentStatus.COMPLETED,
                result={
                    "loan_amount": approval_amount,
                    "monthly_payment": round(monthly_payment, 2),
                    "total_interest": round(total_interest, 2),
                    "total_payment": round(approval_amount + total_interest, 2),
                    "duration_months": duration_months,
                    "annual_interest_rate": interest_rate
                }
            )
        
        except Exception as e:
            return _create_error_response(str(e))
    
    @staticmethod
    def make_agent_decision(agent_id: str, credit_score: float, amount: float) -> Dict[str, Any]:
        """
        Make loan approval decision for an AI agent based on credit score.
        EXPLICITLY SUPPORTS THREE DISTINCT EVALUATION SCENARIOS.
        
        Args:
            agent_id: Unique identifier for the AI agent
            credit_score: Agent's credit score (0-100)
            amount: Requested loan amount
        
        Returns:
            Dict with decision, interest rate, collateral requirements, and explanation
        
        THREE EVALUATION SCENARIOS:
        
        SCENARIO 1 - STRONG AGENTS (credit_score 75-90):
            - risk_level: low
            - interest_rate: 3.5%-4.5% (best available)
            - collateral_required: minimal (5%-10%)
            - approved: True
            - decision_reason: strong repayment history
            - confidence: high (0.75-0.92)
        
        SCENARIO 2 - AVERAGE AGENTS (credit_score 50-70):
            - risk_level: medium/high
            - interest_rate: 7.5%-9.5% (moderate to premium)
            - collateral_required: moderate (20%-25%)
            - approved: True (with caution)
            - decision_reason: moderate risk/average performance
            - confidence: medium (0.55-0.75)
        
        SCENARIO 3 - WEAK AGENTS (credit_score 30-50):
            - risk_level: high/very_high
            - interest_rate: N/A or high if approved
            - collateral_required: high or N/A
            - approved: False (may be approved at margin)
            - decision_reason: low reliability/insufficient history
            - confidence: low (0.42-0.65)
        """
        # EXPLICIT THREE-SCENARIO DECISION LOGIC:
        # Scenario 1: STRONG AGENTS (scores 75-90) → APPROVED with low rates
        # Scenario 2: AVERAGE AGENTS (scores 50-70) → APPROVED with moderate rates
        # Scenario 3: WEAK AGENTS (scores 30-50) → May be REJECTED or approved with high rates
        
        if credit_score >= 80:
            # STRONG AGENT: Excellent approval
            approved = True
            interest_rate = 3.5  # Best available rate for strong agents
            collateral_required = amount * 0.05  # Minimal collateral needed
            risk_category = "Excellent"  # Explicitly "Excellent" for strong agents
            decision_reason = "Approved due to strong repayment history and low risk profile"
            message = f"✓ Loan APPROVED at premium rate (3.5%) - Strong agent with outstanding creditworthiness"
        elif credit_score > 70:
            # STRONG AGENT: Good approval
            approved = True
            interest_rate = 4.5  # Competitive low rate
            collateral_required = amount * 0.10  # 10% collateral
            risk_category = "Low Risk"
            decision_reason = "Approved based on solid transaction history and positive financial metrics"
            message = f"✓ Loan APPROVED at competitive rate (4.5%) - Strong financial profile"
        elif credit_score >= 60:
            # AVERAGE AGENT: Moderate approval
            approved = True
            interest_rate = 7.5  # Moderate rate for average agents
            collateral_required = amount * 0.20  # 20% collateral required
            risk_category = "Medium Risk"
            decision_reason = "Approved with caution due to moderate risk and average performance"
            message = f"~ Loan APPROVED at standard rate (7.5%) - Conditional approval with moderate collateral requirement"
        elif credit_score >= 50:
            # AVERAGE/WEAK BOUNDARY: Marginal approval
            approved = True
            interest_rate = 9.5  # Higher rate for marginal cases
            collateral_required = amount * 0.25  # 25% collateral required
            risk_category = "Higher Risk"
            decision_reason = "Approved at premium rate due to higher perceived risk and limited transaction history"
            message = f"~ Loan APPROVED at premium rate (9.5%) - Marginal approval with significant risk premium"
        else:
            # WEAK AGENT: Rejection
            approved = False
            interest_rate = 0.0
            collateral_required = 0.0
            risk_category = "Insufficient"
            decision_reason = "Rejected due to low reliability score and insufficient credit history"
            message = f"✗ Loan REJECTED - Score {credit_score:.1f} below approval threshold. Insufficient creditworthiness."
        
        # Calculate monthly payment and total interest if approved
        if approved:
            monthly_rate = interest_rate / 100 / 12
            num_payments = 12  # 1-year term
            if monthly_rate > 0:
                monthly_payment = amount * (
                    monthly_rate * (1 + monthly_rate) ** num_payments
                ) / ((1 + monthly_rate) ** num_payments - 1)
            else:
                monthly_payment = amount / num_payments
            total_interest = (monthly_payment * num_payments) - amount
        else:
            monthly_payment = 0.0
            total_interest = 0.0
        
        return {
            "agent_id": agent_id,
            "approved": approved,
            "interest_rate": interest_rate,
            "collateral_required": round(collateral_required, 2),
            "risk_category": risk_category,
            "decision_reason": decision_reason,
            "message": message,
            "credit_score": credit_score,
            "requested_amount": amount,
            "monthly_payment": round(monthly_payment, 2),
            "total_interest": round(total_interest, 2)
        }


def _create_error_response(error_message: str) -> AgentResponse:
    """Create error response."""
    return AgentResponse(
        agent_name=DecisionService.AGENT_NAME,
        status=AgentStatus.FAILED,
        result={"error": error_message}
    )


def _evaluate_criteria(
    credit_score: float,
    gatekeeper_verified: bool,
    debt_to_income: float,
    loan_amount: float
) -> tuple:
    """
    Evaluate all decision criteria.
    
    Returns:
        Tuple of (decision, approval_amount)
    """
    # Must pass identity verification
    if not gatekeeper_verified:
        return ("rejected", 0)
    
    # Credit score thresholds
    if credit_score < 580:
        return ("rejected", 0)
    
    # Debt-to-income ratio limits
    if debt_to_income > 0.43:
        return ("rejected", 0)
    
    # Approval with possible amount adjustment
    approval_amount = loan_amount
    
    if credit_score < 620 and debt_to_income > 0.40:
        approval_amount = loan_amount * 0.80
    
    return ("approved", approval_amount)


def _calculate_interest_rate(credit_score: float, debt_to_income: float) -> float:
    """
    Calculate interest rate based on credit score and debt-to-income.
    
    Returns:
        Annual interest rate as decimal (e.g., 0.065 for 6.5%)
    """
    # Determine tier
    tier = "poor"
    for tier_name, tier_info in DecisionService.INTEREST_RATE_TIERS.items():
        if credit_score >= tier_info["min_score"]:
            tier = tier_name
            break
    
    base_rate = DecisionService.INTEREST_RATE_TIERS[tier]["base_rate"]
    
    # Adjust for debt-to-income
    dti_adjustment = max(0, debt_to_income - 0.30) * 0.05
    
    return base_rate + dti_adjustment


def _generate_loan_conditions(credit_score: float, debt_to_income: float) -> list:
    """Generate loan conditions based on risk profile."""
    conditions = []
    
    if credit_score < 620:
        conditions.append("Requires co-signer")
    
    if debt_to_income > 0.35:
        conditions.append("Monthly debt verification required")
    
    conditions.append("Standard loan agreement terms apply")
    
    return conditions


def _get_rejection_reason(
    credit_score: float,
    gatekeeper_verified: bool,
    debt_to_income: float
) -> str:
    """Generate rejection reason."""
    if not gatekeeper_verified:
        return "Identity verification failed"
    if credit_score < 580:
        return f"Credit score too low ({credit_score})"
    if debt_to_income > 0.43:
        return f"Debt-to-income ratio too high ({debt_to_income:.2%})"
    return "Application did not meet approval criteria"


def _create_error_response(error_message: str) -> AgentResponse:
    """Create error response."""
    return AgentResponse(
        agent_name=DecisionService.AGENT_NAME,
        status=AgentStatus.FAILED,
        result={"error": error_message}
    )
