"""
Wallet-Based Loan Routes

Defines API endpoints for wallet-based loan operations.
Uses Ethereum wallet addresses as agent identity instead of agent_id.
All routes under /loan/wallet prefix.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.services import (
    AnalystService,
    DecisionService,
    TreasuryService,
    AuditorService,
    SupabaseService
)
from app.services.wallet_gatekeeper import WalletGatekeeperService
from app.services.wallet_utils import validate_wallet_address
from app.utils import generate_loan_id, create_error_response


router = APIRouter(prefix="/loan/wallet", tags=["wallet-loan"])


@router.post("/request")
async def request_loan_with_wallet(wallet_address: str, amount: float):
    """
    Wallet-based loan request pipeline for AI agents.
    
    Uses Ethereum wallet address as the unique agent identity instead of agent_id.
    Implements a complete loan processing pipeline:
    1. Gatekeeper: Validates wallet address and generates deterministic profile
    2. Analyst: Calculates credit score based on wallet profile
    3. Decision: Makes approval decision based on score
    4. Treasury: Checks fund availability
    5. Auditor: Logs all events
    
    Args:
        wallet_address: Ethereum wallet address (0x...)
        amount: Requested loan amount (1 - 10,000,000)
    
    Returns:
        Structured response with loan decision and terms
    
    Response includes:
        - wallet_address: The wallet requesting the loan
        - credit_score: Wallet's credit score (0-100)
        - risk_level: Risk classification
        - interest_rate: Annual interest rate if approved
        - collateral_required: Required collateral amount
        - approved: True if loan approved
        - message: Human-readable decision message
    """
    try:
        # Validate input
        if not wallet_address or not isinstance(wallet_address, str):
            raise HTTPException(status_code=400, detail="wallet_address is required (0x...)")
        
        if not validate_wallet_address(wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid wallet address format. Must be 0x followed by 40 hex characters."
            )
        
        if amount <= 0 or amount > 10_000_000:
            raise HTTPException(
                status_code=400,
                detail="amount must be between 1 and 10,000,000"
            )
        
        request_id = generate_loan_id()
        wallet_lower = wallet_address.lower()
        
        # ============================================================
        # STAGE 1: GATEKEEPER - Validate Wallet Identity
        # ============================================================
        gatekeeper_result = WalletGatekeeperService.validate_wallet_identity(wallet_lower)
        
        if not gatekeeper_result["valid"]:
            raise HTTPException(status_code=400, detail=gatekeeper_result["error"])
        
        # Log identity verification
        AuditorService.log_event(
            loan_id=request_id,
            agent_name="gatekeeper",
            event_type="wallet_verification_completed",
            details={
                "wallet_address": wallet_lower,
                "status": gatekeeper_result["status"],
                "agent_tier": gatekeeper_result["agent_tier"]
            }
        )
        
        # ============================================================
        # STAGE 2: ANALYST - Calculate Credit Score
        # ============================================================
        agent_profile = {
            "success_rate": gatekeeper_result.get("success_rate", 0.70),
            "transaction_count": gatekeeper_result.get("transaction_count", 0),
            "repayment_history": gatekeeper_result.get("repayment_history", 0.70)
        }
        
        # Use the wallet address as identifier for analyst
        score_result = AnalystService.calculate_agent_credit_score(
            wallet_lower,
            amount,
            agent_profile
        )
        credit_score = score_result["score"]
        risk_level = score_result["risk_level"]
        confidence = score_result.get("confidence", 0.65)
        agent_tier = score_result.get("agent_tier", "low")
        
        # Log scoring
        AuditorService.log_event(
            loan_id=request_id,
            agent_name="analyst",
            event_type="credit_score_calculated",
            details={
                "wallet_address": wallet_lower,
                "score": credit_score,
                "risk_level": risk_level
            }
        )
        
        # ============================================================
        # STAGE 3: DECISION - Make Approval Decision
        # ============================================================
        decision_result = DecisionService.make_agent_decision(wallet_lower, credit_score, amount)
        approved = decision_result["approved"]
        interest_rate = decision_result["interest_rate"]
        collateral_required = decision_result["collateral_required"]
        
        # Log decision
        AuditorService.log_event(
            loan_id=request_id,
            agent_name="decision",
            event_type="loan_decision_made",
            details={
                "wallet_address": wallet_lower,
                "approved": approved,
                "credit_score": credit_score,
                "interest_rate": interest_rate
            }
        )
        
        # ============================================================
        # STAGE 4: TREASURY - Check Fund Availability
        # ============================================================
        treasury_result = TreasuryService.check_fund_availability_for_agent(wallet_lower, amount)
        funds_available = treasury_result["funds_available"]
        
        # Log treasury check
        AuditorService.log_event(
            loan_id=request_id,
            agent_name="treasury",
            event_type="fund_availability_checked",
            details={
                "wallet_address": wallet_lower,
                "requested_amount": amount,
                "funds_available": funds_available
            }
        )
        
        # ============================================================
        # Final Decision
        # ============================================================
        final_approved = approved and funds_available
        final_interest_rate = interest_rate if final_approved else 0.0
        final_collateral = collateral_required if final_approved else 0.0
        
        # Determine final message
        if not final_approved:
            if not approved:
                final_message = decision_result["message"]
            else:
                final_message = "Approved pending treasury review - insufficient funds available"
        else:
            final_message = f"Loan approved! Rate: {interest_rate}% Annual"
        
        # Log final decision
        AuditorService.log_event(
            loan_id=request_id,
            agent_name="auditor",
            event_type="pipeline_complete",
            details={
                "wallet_address": wallet_lower,
                "request_id": request_id,
                "final_approved": final_approved,
                "score": credit_score
            }
        )
        
        # ============================================================
        # Update Agent Metrics (Event Handler)
        # ============================================================
        try:
            db_service = SupabaseService.get_instance()
            
            # Get or create agent in database
            agent = await db_service.get_or_create_agent(wallet_lower, trust_score=credit_score)
            
            # Update metrics for this loan request
            await db_service.update_agent_metrics(wallet_lower, amount)
            
            # If approved, increment total_loans counter
            if final_approved:
                current_total = agent.get("total_loans", 0) + 1
                await db_service.update_agent_trust_score(wallet_lower, credit_score)
                print(f"[AGENT] Updated metrics for {wallet_lower}: loan approved, total={current_total}")
        except Exception as error:
            print(f"[AGENT] Warning: Could not update agent metrics: {str(error)}")
            # Don't fail the loan request if DB update fails
        
        # ============================================================
        # Return Final Response
        # ============================================================
        return {
            "request_id": request_id,
            "wallet_address": wallet_lower,
            "amount_requested": amount,
            "score": credit_score,
            "risk_level": risk_level,
            "confidence": confidence,
            "decision_reason": decision_result.get("decision_reason", "Decision made based on wallet profile evaluation"),
            "interest_rate": final_interest_rate,
            "collateral_required": final_collateral,
            "approved": final_approved,
            "funds_available": funds_available,
            "monthly_payment": decision_result.get("monthly_payment", 0.0) if final_approved else 0.0,
            "total_interest": decision_result.get("total_interest", 0.0) if final_approved else 0.0,
            "message": final_message,
            "wallet_profile": {
                "success_rate": round(agent_profile.get("success_rate", 0) * 100, 1),
                "transaction_count": agent_profile.get("transaction_count", 0),
                "repayment_history": round(agent_profile.get("repayment_history", 0) * 100, 1),
                "agent_tier": agent_tier,
                "agent_status": gatekeeper_result.get("status", "unknown")
            },
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_status": {
                "gatekeeper": "valid" if gatekeeper_result["valid"] else "invalid",
                "analyst": f"score_{int(credit_score)}",
                "decision": "approved" if approved else "rejected",
                "treasury": "available" if funds_available else "unavailable"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response("WALLET_LOAN_REQUEST_ERROR", str(e))
        )


@router.get("/profile/{wallet_address}")
async def get_wallet_profile(wallet_address: str):
    """
    Get the deterministic profile for a wallet address.
    
    Useful for debugging and understanding wallet-based scoring.
    
    Args:
        wallet_address: Ethereum wallet address
    
    Returns:
        Wallet profile details (success_rate, transaction_count, etc.)
    """
    if not validate_wallet_address(wallet_address):
        raise HTTPException(
            status_code=400,
            detail="Invalid wallet address format"
        )
    
    from app.services.wallet_utils import get_wallet_summary
    
    wallet_lower = wallet_address.lower()
    gatekeeper_result = WalletGatekeeperService.validate_wallet_identity(wallet_lower)
    
    return {
        "wallet_address": wallet_lower,
        "profile": gatekeeper_result,
        "summary": get_wallet_summary(wallet_lower)
    }
