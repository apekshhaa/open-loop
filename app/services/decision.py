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
        
        DETERMINISTIC — same inputs always produce identical output.
        
        DECISION RULES (aligned with analyst score ranges):
        
        Score 80-90 (strong tier, agent_id ending "1"):
            → APPROVED, 3.5% interest, 5% collateral
        
        Score 55-70 (average tier, agent_id ending "2"):
            Score >= 60 → APPROVED, 7.5% interest, 20% collateral
            Score <  60 → APPROVED, 9.5% interest, 25% collateral
        
        Score 30-50 (weak tier, other agent_ids):
            → REJECTED, insufficient creditworthiness
        
        Args:
            agent_id: Unique identifier for the AI agent
            credit_score: Agent's credit score (0-100)
            amount: Requested loan amount
        
        Returns:
            Dict with decision, interest rate, collateral, explanation
        """
        
        if credit_score >= 80:
            # ── STRONG AGENT → Full approval at best rate ───────────
            approved = True
            interest_rate = 3.5
            collateral_required = round(amount * 0.05, 2)
            risk_category = "Low Risk"
            decision_reason = (
                f"Approved: Agent {agent_id} has an excellent credit score of {credit_score:.1f}/100, "
                f"indicating strong repayment history and high reliability. "
                f"Qualified for premium rate of 3.5% with minimal collateral (5%)."
            )
            message = (
                f"✓ Loan APPROVED at premium rate (3.5%) — "
                f"Outstanding creditworthiness, score {credit_score:.1f}/100"
            )
        
        elif credit_score >= 60:
            # ── AVERAGE AGENT (upper) → Approved with moderate terms ─
            approved = True
            interest_rate = 7.5
            collateral_required = round(amount * 0.20, 2)
            risk_category = "Medium Risk"
            decision_reason = (
                f"Approved with conditions: Agent {agent_id} has a credit score of {credit_score:.1f}/100, "
                f"reflecting moderate performance history. "
                f"Standard rate of 7.5% applied with 20% collateral requirement."
            )
            message = (
                f"~ Loan APPROVED at standard rate (7.5%) — "
                f"Conditional approval, score {credit_score:.1f}/100"
            )
        
        elif credit_score >= 50:
            # ── AVERAGE AGENT (lower boundary) → Marginal approval ──
            approved = True
            interest_rate = 9.5
            collateral_required = round(amount * 0.25, 2)
            risk_category = "Higher Risk"
            decision_reason = (
                f"Marginal approval: Agent {agent_id} has a credit score of {credit_score:.1f}/100, "
                f"at the lower end of the acceptable range. "
                f"Premium rate of 9.5% applied with 25% collateral to offset risk."
            )
            message = (
                f"~ Loan APPROVED at premium rate (9.5%) — "
                f"Marginal approval with significant collateral, score {credit_score:.1f}/100"
            )
        
        else:
            # ── WEAK AGENT → Rejected ───────────────────────────────
            approved = False
            interest_rate = 0.0
            collateral_required = 0.0
            risk_category = "Insufficient"
            decision_reason = (
                f"Rejected: Agent {agent_id} has a credit score of {credit_score:.1f}/100, "
                f"which is below the minimum approval threshold of 50. "
                f"Insufficient credit history and low reliability score prevent approval."
            )
            message = (
                f"✗ Loan REJECTED — Score {credit_score:.1f}/100 below approval threshold. "
                f"Insufficient creditworthiness for loan disbursement."
            )
        
        # ── Calculate repayment terms if approved ───────────────────
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
            "total_interest": round(total_interest, 2),
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
