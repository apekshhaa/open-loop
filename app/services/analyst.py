"""
Analyst Service - Credit Scoring Agent

Responsible for analyzing financial data and assigning credit scores.
This agent evaluates creditworthiness based on financial history and metrics.

Functions:
    - Calculate credit score
    - Analyze financial data
    - Assess credit risk
    - Generate credit recommendations
"""

from typing import Dict, Any
from app.models import AgentResponse, AgentStatus, CreditScoreResponse
from datetime import datetime


class AnalystService:
    """
    Credit scoring and analysis agent.
    
    This service analyzes financial data and assigns credit scores
    using weighted scoring models.
    """
    
    AGENT_NAME = "analyst"
    
    # Credit score weights (can be adjusted)
    WEIGHTS = {
        "payment_history": 0.35,
        "credit_utilization": 0.30,
        "credit_age": 0.15,
        "accounts_diversity": 0.10,
        "recent_inquiries": 0.10
    }
    
    @staticmethod
    def calculate_credit_score(borrower_id: str, financial_data: Dict[str, Any]) -> AgentResponse:
        """
        Calculate credit score for borrower.
        
        Args:
            borrower_id: Unique identifier for the borrower
            financial_data: Financial information including payment history, debts, etc.
        
        Returns:
            AgentResponse with credit score and analysis
        
        TODO: Implement advanced credit scoring:
            - Integrate with credit bureaus (Equifax, Experian, TransUnion)
            - Implement FICO score calculation logic
            - Machine learning models for alternative credit scoring
            - Real-time financial data aggregation
        """
        try:
            # Placeholder credit score calculation
            credit_score = _calculate_score_from_data(financial_data)
            risk_level = _determine_risk_level(credit_score)
            factors = _analyze_credit_factors(financial_data)
            recommendation = _generate_recommendation(credit_score, risk_level)
            
            return AgentResponse(
                agent_name=AnalystService.AGENT_NAME,
                status=AgentStatus.COMPLETED,
                result={
                    "credit_score": credit_score,
                    "risk_level": risk_level,
                    "factors": factors,
                    "recommendation": recommendation,
                    "score_breakdown": _get_score_breakdown(financial_data)
                },
                metadata={"borrower_id": borrower_id}
            )
        
        except Exception as e:
            return _create_error_response(str(e))
    
    @staticmethod
    def analyze_financial_health(borrower_id: str, financial_data: Dict[str, Any]) -> AgentResponse:
        """
        Perform comprehensive financial health analysis.
        
        Args:
            borrower_id: Borrower identifier
            financial_data: Financial information to analyze
        
        Returns:
            AgentResponse with financial health analysis
        
        TODO: Implement detailed financial analysis:
            - Debt-to-income ratio calculation
            - Cash flow analysis
            - Savings rate analysis
            - Income stability assessment
            - Asset evaluation
        """
        try:
            debt_to_income = _calculate_debt_to_income(financial_data)
            savings_ratio = _calculate_savings_ratio(financial_data)
            income_stability = _assess_income_stability(financial_data)
            
            return AgentResponse(
                agent_name=AnalystService.AGENT_NAME,
                status=AgentStatus.COMPLETED,
                result={
                    "debt_to_income_ratio": debt_to_income,
                    "savings_ratio": savings_ratio,
                    "income_stability": income_stability,
                    "overall_health": "healthy" if debt_to_income < 0.43 else "fair"
                },
                metadata={"borrower_id": borrower_id}
            )
        except Exception as e:
            return _create_error_response(str(e))
    
    @staticmethod
    def calculate_agent_credit_score(agent_id: str, amount: float, agent_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate credit score for an AI agent requesting a loan.
        
        FULLY DETERMINISTIC — same agent_id + same amount ALWAYS returns
        identical output. No random functions anywhere.
        
        SCORING RULES:
            agent_id ending in "1" → score 80-90, low risk, approved
            agent_id ending in "2" → score 55-70, medium risk, approved
            all others             → score 30-50, high/very_high risk, rejected
        
        The loan amount provides minor adjustment within each tier's range:
            - Smaller amounts → higher end of range
            - Larger amounts  → lower end of range
        
        Args:
            agent_id: Unique identifier for the AI agent
            amount: Loan amount requested
            agent_profile: Optional agent profile data
        
        Returns:
            Dict with credit score, risk level, confidence, and analysis
        """
        
        # ── Determine tier ──────────────────────────────────────────
        if agent_id.endswith("1"):
            tier = "strong"
        elif agent_id.endswith("2"):
            tier = "average"
        else:
            tier = "weak"
        
        # ── Fixed profiles per tier ─────────────────────────────────
        tier_profiles = {
            "strong":  {"success_rate": 0.92, "transaction_count": 48, "repayment_history": 0.98},
            "average": {"success_rate": 0.75, "transaction_count": 28, "repayment_history": 0.80},
            "weak":    {"success_rate": 0.45, "transaction_count": 8,  "repayment_history": 0.55},
        }
        
        if agent_profile is None:
            agent_profile = tier_profiles[tier]
        
        success_rate = agent_profile.get("success_rate", 0.70)
        transaction_count = agent_profile.get("transaction_count", 0)
        repayment_history = agent_profile.get("repayment_history", 0.70)
        
        # ── Amount factor: 0.0–1.0 (higher amount → lower factor) ──
        # Caps at 5,000,000. Deterministic, linear scaling.
        amount_factor = max(0.0, min(1.0, 1.0 - (amount / 5_000_000)))
        
        # ── Score calculation per tier ──────────────────────────────
        # Each tier has a [min, max] range. The amount_factor slides
        # the score within that range.  Same inputs → same output.
        tier_ranges = {
            "strong":  (80, 90),    # agent_id "1"
            "average": (55, 70),    # agent_id "2"
            "weak":    (30, 50),    # others
        }
        
        score_min, score_max = tier_ranges[tier]
        score_range = score_max - score_min
        score = round(score_min + (amount_factor * score_range), 1)
        
        # ── Fixed confidence per tier ───────────────────────────────
        tier_confidence = {
            "strong":  0.92,
            "average": 0.68,
            "weak":    0.45,
        }
        confidence = tier_confidence[tier]
        
        # ── Risk level from score ───────────────────────────────────
        if score >= 80:
            risk_level = "low"
            category = "Excellent credit profile — strong agent with proven track record"
        elif score >= 65:
            risk_level = "medium"
            category = "Good credit profile — average agent with moderate history"
        elif score >= 50:
            risk_level = "medium"
            category = "Fair credit profile — limited history, moderate risk"
        else:
            risk_level = "high" if score >= 40 else "very_high"
            category = "Poor credit profile — insufficient history or low reliability"
        
        # ── Score component breakdown (for transparency) ────────────
        success_component = round(success_rate * 40, 2)
        transaction_component = round(min((transaction_count / 50) * 35, 35), 2)
        repayment_component = round(repayment_history * 25, 2)
        amount_component = round(amount_factor * 10, 2)
        
        return {
            "agent_id": agent_id,
            "score": score,
            "risk_level": risk_level,
            "category": category,
            "confidence": confidence,
            "agent_tier": tier,
            "success_rate": round(success_rate * 100, 1),
            "transaction_count": transaction_count,
            "repayment_history": round(repayment_history * 100, 1),
            "components": {
                "success_component": success_component,
                "transaction_component": transaction_component,
                "repayment_component": repayment_component,
                "amount_component": amount_component,
                "tier": tier,
                "amount_factor": round(amount_factor, 4),
            },
        }


def _create_error_response(error_message: str) -> AgentResponse:
    """Create error response."""
    return AgentResponse(
        agent_name=AnalystService.AGENT_NAME,
        status=AgentStatus.FAILED,
        result={"error": error_message}
    )


def _calculate_score_from_data(financial_data: Dict[str, Any]) -> float:
    """
    Calculate weighted credit score based on financial data.
    
    Returns:
        Score between 0-850 (FICO scale)
    
    TODO: Implement full credit scoring model
    """
    # Placeholder calculation
    base_score = 650
    
    if financial_data.get("payment_history_clean", False):
        base_score += 100
    if financial_data.get("low_credit_utilization", False):
        base_score += 50
    if financial_data.get("long_credit_history", False):
        base_score += 50
    
    return min(850, max(300, base_score))


def _determine_risk_level(credit_score: float) -> str:
    """Determine risk level based on credit score."""
    if credit_score >= 750:
        return "low"
    elif credit_score >= 670:
        return "medium"
    else:
        return "high"


def _analyze_credit_factors(financial_data: Dict[str, Any]) -> list:
    """Analyze and list key credit factors."""
    factors = []
    
    if financial_data.get("payment_history_clean"):
        factors.append("Clean payment history")
    if financial_data.get("low_credit_utilization"):
        factors.append("Low credit utilization")
    if financial_data.get("multiple_accounts"):
        factors.append("Diverse credit mix")
    if financial_data.get("recent_inquiries", 0) > 3:
        factors.append("Recent credit inquiries")
    
    return factors


def _generate_recommendation(credit_score: float, risk_level: str) -> str:
    """Generate analyst recommendation based on score and risk."""
    if credit_score >= 750:
        return "Highly recommended for approval"
    elif credit_score >= 670:
        return "Recommended for approval with review"
    else:
        return "Recommend careful review before approval"


def _get_score_breakdown(financial_data: Dict[str, Any]) -> Dict[str, float]:
    """Get breakdown of score components."""
    return {
        "payment_history": 95.0,
        "credit_utilization": 80.0,
        "credit_age": 85.0,
        "accounts_diversity": 75.0,
        "recent_inquiries": 90.0
    }


def _calculate_debt_to_income(financial_data: Dict[str, Any]) -> float:
    """Calculate debt-to-income ratio."""
    total_debt = financial_data.get("total_monthly_debt", 0)
    gross_income = financial_data.get("monthly_gross_income", 1)
    return total_debt / gross_income if gross_income > 0 else 0.5


def _calculate_savings_ratio(financial_data: Dict[str, Any]) -> float:
    """Calculate monthly savings ratio."""
    monthly_savings = financial_data.get("monthly_savings", 0)
    monthly_income = financial_data.get("monthly_gross_income", 1)
    return monthly_savings / monthly_income if monthly_income > 0 else 0.0


def _assess_income_stability(financial_data: Dict[str, Any]) -> str:
    """Assess income stability from financial data."""
    employment_years = financial_data.get("employment_years", 0)
    
    if employment_years >= 2:
        return "stable"
    elif employment_years >= 1:
        return "moderate"
    else:
        return "unstable"


def _create_error_response(error_message: str) -> AgentResponse:
    """Create error response."""
    return AgentResponse(
        agent_name=AnalystService.AGENT_NAME,
        status=AgentStatus.FAILED,
        result={"error": error_message}
    )
