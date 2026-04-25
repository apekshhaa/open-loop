"""
Treasury Service - Fund Availability Agent

Responsible for checking fund availability and managing lending capital.
This agent ensures the system has sufficient capital to fund approved loans.

Functions:
    - Check available funds
    - Manage capital allocation
    - Check portfolio limits
    - Reserve funds for approved loans
"""

from typing import Dict, Any
from app.models import AgentResponse, AgentStatus
from datetime import datetime


class TreasuryService:
    """
    Fund and capital management agent.
    
    This service manages the lending capital pool and ensures
    sufficient funds are available for loan funding.
    """
    
    AGENT_NAME = "treasury"
    
    # Placeholder capital pool (in real system, would be in database)
    CAPITAL_POOL = {
        "total_available": 1_000_000.00,
        "reserved": 0.00,
        "deployed": 0.00
    }
    
    # Portfolio limits
    PORTFOLIO_LIMITS = {
        "max_loan_percentage": 0.05,  # Max 5% of capital in single loan
        "max_sector_percentage": 0.20,  # Max 20% in single sector
        "min_diversification": 5  # Minimum number of loans for diversification
    }
    
    @staticmethod
    def check_fund_availability(requested_amount: float) -> AgentResponse:
        """
        Check if sufficient funds available for loan.
        
        Args:
            requested_amount: Requested loan amount
        
        Returns:
            AgentResponse with fund availability status
        
        TODO: Implement:
            - Real-time capital pool queries
            - Reserve management system
            - Capital forecasting
            - Liquidity analysis
        """
        try:
            available = TreasuryService.CAPITAL_POOL["total_available"] - \
                       TreasuryService.CAPITAL_POOL["reserved"]
            
            fund_available = available >= requested_amount
            funding_percentage = (requested_amount / available * 100) if available > 0 else 0
            
            return AgentResponse(
                agent_name=TreasuryService.AGENT_NAME,
                status=AgentStatus.COMPLETED,
                result={
                    "fund_available": fund_available,
                    "requested_amount": requested_amount,
                    "available_capital": available,
                    "funding_percentage": round(funding_percentage, 2),
                    "total_capital": TreasuryService.CAPITAL_POOL["total_available"]
                }
            )
        
        except Exception as e:
            return _create_error_response(str(e))
    
    @staticmethod
    def check_portfolio_limits(
        requested_amount: float,
        borrower_sector: str,
        current_loans_count: int
    ) -> AgentResponse:
        """
        Check if loan fits within portfolio limits.
        
        Args:
            requested_amount: Requested loan amount
            borrower_sector: Sector/industry of borrower
            current_loans_count: Current number of loans in portfolio
        
        Returns:
            AgentResponse with portfolio limit check
        
        TODO: Implement:
            - Sector exposure tracking
            - Concentration risk analysis
            - Diversification requirements
            - Dynamic limit adjustment
        """
        try:
            total_capital = TreasuryService.CAPITAL_POOL["total_available"]
            
            # Check single loan limit
            max_single_loan = total_capital * TreasuryService.PORTFOLIO_LIMITS["max_loan_percentage"]
            single_loan_ok = requested_amount <= max_single_loan
            
            # Check diversification
            diversification_ok = current_loans_count >= \
                               TreasuryService.PORTFOLIO_LIMITS["min_diversification"] or \
                               requested_amount < (total_capital * 0.02)
            
            limits_met = single_loan_ok and diversification_ok
            
            return AgentResponse(
                agent_name=TreasuryService.AGENT_NAME,
                status=AgentStatus.COMPLETED,
                result={
                    "limits_met": limits_met,
                    "single_loan_check": {
                        "passed": single_loan_ok,
                        "requested": requested_amount,
                        "max_allowed": max_single_loan
                    },
                    "diversification_check": {
                        "passed": diversification_ok,
                        "current_loans": current_loans_count,
                        "min_required": TreasuryService.PORTFOLIO_LIMITS["min_diversification"]
                    }
                }
            )
        
        except Exception as e:
            return _create_error_response(str(e))
    
    @staticmethod
    def reserve_funds(loan_id: str, amount: float) -> AgentResponse:
        """
        Reserve funds for approved loan.
        
        Args:
            loan_id: Loan identifier
            amount: Amount to reserve
        
        Returns:
            AgentResponse with reservation status
        
        TODO: Implement:
            - Database transaction for reserves
            - Atomic fund reservation
            - Reservation tracking
            - Expiration management
        """
        try:
            available = TreasuryService.CAPITAL_POOL["total_available"] - \
                       TreasuryService.CAPITAL_POOL["reserved"]
            
            if amount <= available:
                TreasuryService.CAPITAL_POOL["reserved"] += amount
                reserved = True
                message = f"Successfully reserved ${amount:.2f} for loan {loan_id}"
            else:
                reserved = False
                message = f"Insufficient funds to reserve ${amount:.2f}"
            
            return AgentResponse(
                agent_name=TreasuryService.AGENT_NAME,
                status=AgentStatus.COMPLETED,
                result={
                    "reserved": reserved,
                    "loan_id": loan_id,
                    "amount": amount,
                    "message": message,
                    "remaining_available": available - (amount if reserved else 0)
                }
            )
        
        except Exception as e:
            return _create_error_response(str(e))
    
    @staticmethod
    def get_capital_status() -> Dict[str, Any]:
        """Get current capital pool status."""
        pool = TreasuryService.CAPITAL_POOL
        available = pool["total_available"] - pool["reserved"]
        
        return {
            "total_capital": pool["total_available"],
            "reserved": pool["reserved"],
            "deployed": pool["deployed"],
            "available": available,
            "utilization_percentage": round(
                (pool["reserved"] + pool["deployed"]) / pool["total_available"] * 100, 2
            )
        }
    
    @staticmethod
    def check_fund_availability_for_agent(agent_id: str, amount: float) -> Dict[str, Any]:
        """
        Check if sufficient funds are available for an agent loan request.
        
        Args:
            agent_id: Unique identifier for the AI agent
            amount: Requested loan amount
        
        Returns:
            Dict with availability status and fund details
        """
        available = TreasuryService.CAPITAL_POOL["total_available"] - \
                   TreasuryService.CAPITAL_POOL["reserved"]
        
        funds_available = available >= amount
        utilization = ((TreasuryService.CAPITAL_POOL["reserved"] + TreasuryService.CAPITAL_POOL["deployed"]) / 
                      TreasuryService.CAPITAL_POOL["total_available"]) * 100
        
        return {
            "agent_id": agent_id,
            "requested_amount": amount,
            "available_funds": round(available, 2),
            "total_capital": TreasuryService.CAPITAL_POOL["total_available"],
            "reserved_funds": TreasuryService.CAPITAL_POOL["reserved"],
            "deployed_funds": TreasuryService.CAPITAL_POOL["deployed"],
            "funds_available": funds_available,
            "capital_utilization": round(utilization, 2),
            "message": "Sufficient funds available" if funds_available else "Insufficient funds available"
        }


def _create_error_response(error_message: str) -> AgentResponse:
    """Create error response."""
    return AgentResponse(
        agent_name=TreasuryService.AGENT_NAME,
        status=AgentStatus.FAILED,
        result={"error": error_message}
    )
