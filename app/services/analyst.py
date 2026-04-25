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
        
        Args:
            agent_id: Unique identifier for the AI agent
            amount: Loan amount requested
            agent_profile: Agent profile data (success_rate, transaction_count, repayment_history)
        
        Returns:
            Dict with credit score (0-100), risk level, confidence, and detailed analysis
        
        Implementation:
            - Dynamic scoring based on agent profile
            - Considers success rate, transaction history, and repayment history
            - Agent-ID based variation: "1" gets high scores, "2" gets medium, others get low
            - Loan amount affects scoring (large loans reduce score slightly)
            - Provides realistic 0-100 credit score with variation
            - Includes confidence scoring and agent profile details
        """
        import random
        
        # Agent-ID based scoring tiers for meaningful variation - THREE EXPLICIT SCENARIOS
        def get_agent_tier(agent_id: str) -> str:
            """
            Determine agent tier based on agent_id for consistent, predictable variation.
            
            Returns:
                "strong" if agent_id ends with "1" → STRONG agent (scores 75-90)
                "average" if agent_id ends with "2" → AVERAGE agent (scores 50-70)
                "weak" otherwise → WEAK agent (scores 30-50)
            """
            if agent_id.endswith("1"):
                return "strong"  # agent_ids ending in 1 → STRONG agents with high scores (75-90)
            elif agent_id.endswith("2"):
                return "average"  # agent_ids ending in 2 → AVERAGE agents with medium scores (50-70)
            else:
                return "weak"  # all others → WEAK agents with low scores (30-50)
        
        # Mock agent historical data for predefined agents
        default_profiles = {
            "AGENT-001": {"success_rate": 0.92, "transaction_count": 45, "repayment_history": 0.98},
            "AGENT-002": {"success_rate": 0.85, "transaction_count": 28, "repayment_history": 0.94},
            "AGENT-003": {"success_rate": 0.78, "transaction_count": 15, "repayment_history": 0.88},
            "AGENT-TEST": {"success_rate": 0.50, "transaction_count": 2, "repayment_history": 0.75},
        }
        
        # Get agent profile
        if agent_profile is None:
            agent_profile = default_profiles.get(agent_id, {
                "success_rate": 0.70,
                "transaction_count": 0,
                "repayment_history": 0.70
            })
        
        # Extract profile metrics
        success_rate = agent_profile.get("success_rate", 0.70)
        transaction_count = agent_profile.get("transaction_count", 0)
        repayment_history = agent_profile.get("repayment_history", 0.70)
        
        # Get agent tier for consistent, predictable variation
        agent_tier = get_agent_tier(agent_id)
        
        # Apply agent-tier-based score adjustment with explicit scenario ranges
        tier_adjustments = {
            "strong": (15, 25),   # strong agents: add 15-25 points → scores 75-90
            "average": (0, 10),   # average agents: add 0-10 points → scores 50-70
            "weak": (-15, -5)     # weak agents: subtract 5-15 points → scores 30-50
        }
        tier_min, tier_max = tier_adjustments[agent_tier]
        tier_adjustment = random.uniform(tier_min, tier_max)
        
        # Calculate score components with more realistic weights
        success_component = success_rate * 40  # 0-40 points: success rate is primary factor
        
        # Transaction component: 0-35 points (more transactions = better, capped at 50 transactions)
        transaction_component = min((transaction_count / 50) * 35, 35)
        
        # Repayment history component: 0-25 points (payment reliability)
        repayment_component = repayment_history * 25
        
        # Amount component: 0-10 points (large loans slightly reduce score)
        # Very large loans indicate higher risk/uncertainty
        amount_factor = min(1.0, max(0.0, 1.0 - (amount / 5000000)))  # 0-1.0 factor
        amount_component = amount_factor * 10
        
        # Add slight randomness for demo variation (±2 points)
        randomness = random.uniform(-2, 2)
        
        # Calculate final score (0-100) with tier adjustment
        base_score = success_component + transaction_component + repayment_component + amount_component + randomness + tier_adjustment
        score = min(100, max(0, base_score))
        
        # Calculate confidence based on agent tier (explicit three-scenario support)
        # Strong agents: high confidence (0.7-0.9)
        # Average agents: medium confidence (0.5-0.7)
        # Weak agents: lower confidence (0.4-0.6)
        if agent_tier == "strong":
            confidence = random.uniform(0.75, 0.92)  # High confidence for strong agents
        elif agent_tier == "average":
            confidence = random.uniform(0.55, 0.75)  # Medium confidence for average agents
        else:  # weak
            confidence = random.uniform(0.42, 0.65)  # Lower confidence for weak agents
        
        confidence = max(0.4, min(0.99, confidence))  # Ensure reasonable bounds
        
        # Determine risk level based on score
        if score >= 80:
            risk_level = "low"
            category = "Excellent credit profile"
        elif score >= 65:
            risk_level = "medium"
            category = "Good credit profile"
        elif score >= 50:
            risk_level = "high"
            category = "Fair credit profile"
        else:
            risk_level = "very_high"
            category = "Poor credit profile or insufficient history"
        
        return {
            "agent_id": agent_id,
            "score": round(score, 1),
            "risk_level": risk_level,
            "category": category,
            "confidence": round(confidence, 2),
            "agent_tier": agent_tier,
            "success_rate": round(success_rate * 100, 1),
            "transaction_count": transaction_count,
            "repayment_history": round(repayment_history * 100, 1),
            "components": {
                "success_component": round(success_component, 2),
                "transaction_component": round(transaction_component, 2),
                "repayment_component": round(repayment_component, 2),
                "amount_component": round(amount_component, 2),
                "tier_adjustment": round(tier_adjustment, 2),
                "randomness": round(randomness, 2)
            }
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
