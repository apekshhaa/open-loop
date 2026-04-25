"""
Package initialization for routes module.
"""

from app.routes.loan import router as loan_router
from app.routes.wallet_loan import router as wallet_loan_router
from app.routes.agent import router as agent_router

__all__ = ["loan_router", "wallet_loan_router", "agent_router"]
