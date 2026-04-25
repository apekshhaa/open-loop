"""
Loan routes module.

Defines API endpoints for loan operations and pipeline management.
All routes under /loan prefix.

Now integrated with Supabase for persistent storage of:
- Agent profiles and history
- Loan records and decisions
- Transaction hashes and audit trail
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.models import (
    LoanRequest,
    LoanApplicationResponse,
    LoanStatus,
    PipelineStatusResponse,
    AgentStatus
)
from app.services import (
    GatekeeperService,
    AnalystService,
    DecisionService,
    TreasuryService,
    SettlerService,
    AuditorService,
    WalletGatekeeperService
)
from app.services.wallet_utils import validate_wallet_address
from app.services.db_service import get_db_service
from app.utils import (
    generate_loan_id,
    generate_log_id,
    validate_loan_amount,
    validate_duration,
    create_error_response,
    RequestValidator
)

router = APIRouter(prefix="/loan", tags=["loan"])

# In-memory storage for loans (kept for backward compatibility)
LOANS_DB = {}
PIPELINE_STAGES = {}


@router.post("/request")
async def request_loan(wallet_address: str, amount: float):
    """
    Core loan request pipeline for AI agents using wallet-based identity.
    
    NOW WITH DATABASE PERSISTENCE:
    - Stores agent profile in Supabase
    - Records all loan requests and decisions
    - Maintains audit trail of all transactions
    
    THIS ENDPOINT NOW REQUIRES A VALID ETHEREUM WALLET ADDRESS.
    Agent identity is determined by the connected wallet, not an agent ID.
    
    This endpoint orchestrates the complete loan processing pipeline:
    1. Gatekeeper: Validates wallet address and generates deterministic profile
    2. Analyst: Calculates credit score based on wallet profile (0-100)
    3. Decision: Makes approval decision based on score and amount
    4. Treasury: Checks fund availability
    5. Auditor: Logs all events and stores in database
    
    Args:
        wallet_address: Ethereum wallet address (0x + 40 hex characters) - REQUIRED
        amount: Requested loan amount (1 - 10,000,000) - REQUIRED
    
    Returns:
        Structured response with loan decision and terms
    
    Response includes:
        - wallet_address: The wallet requesting the loan
        - credit_score: Wallet's credit score (0-100) based on deterministic profile
        - risk_level: Risk classification (low/medium/high/very_high)
        - interest_rate: Annual interest rate if approved
        - collateral_required: Required collateral amount
        - approved: True if loan approved, False otherwise
        - message: Human-readable decision message
        - funds_available: Whether treasury has funds
        - db_loan_id: Database record ID for this loan (if stored)
    
    Raises:
        HTTPException 400: If wallet_address is missing or invalid format
        HTTPException 400: If amount is invalid
        HTTPException 500: If processing error occurs
    """
    db_service = None
    db_loan_id = None
    
    try:
        # Initialize database service
        db_service = get_db_service()
        
        # ============================================================
        # INPUT VALIDATION
        # ============================================================
        
        # Check if wallet_address is provided
        if not wallet_address or not isinstance(wallet_address, str):
            raise HTTPException(
                status_code=400, 
                detail="Wallet not connected. Please connect your wallet to request a loan."
            )
        
        # Validate wallet address format (0x + 40 hex characters = 42 total)
        if not validate_wallet_address(wallet_address):
            raise HTTPException(
                status_code=400, 
                detail="Invalid wallet address format. Must be 0x... with 40 hex characters (e.g., 0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0)"
            )
        
        # Validate amount
        if amount <= 0 or amount > 10_000_000:
            raise HTTPException(
                status_code=400, 
                detail="amount must be between 1 and 10,000,000"
            )
        
        request_id = generate_loan_id()
        
        # ============================================================
        # STAGE 1: GATEKEEPER - Validate Wallet Identity & Get/Create Agent
        # ============================================================
        gatekeeper_result = await WalletGatekeeperService.validate_wallet_identity_with_db(
            wallet_address,
            db_service
        )
        
        if not gatekeeper_result.get("valid"):
            raise HTTPException(
                status_code=400,
                detail=gatekeeper_result.get("message", "Wallet validation failed")
            )
        
        # Log identity verification
        AuditorService.log_event(
            loan_id=request_id,
            agent_name="gatekeeper",
            event_type="wallet_verification_completed",
            details={
                "wallet_address": wallet_address,
                "status": gatekeeper_result.get("status"),
                "agent_tier": gatekeeper_result.get("agent_tier"),
                "db_agent_id": gatekeeper_result.get("db_agent_id")
            }
        )
        
        # ============================================================
        # STAGE 2: ANALYST - Calculate Credit Score
        # ============================================================
        # Pass wallet profile data to analyst for credit scoring
        agent_profile = {
            "success_rate": gatekeeper_result.get("success_rate", 0.70),
            "transaction_count": gatekeeper_result.get("transaction_count", 0),
            "repayment_history": gatekeeper_result.get("repayment_history", 0.70)
        }
        
        # Use wallet address as identifier for scoring
        score_result = AnalystService.calculate_agent_credit_score(wallet_address, amount, agent_profile)
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
                "wallet_address": wallet_address,
                "score": credit_score,
                "risk_level": risk_level,
                "components": score_result.get("components", {})
            }
        )
        
        # ============================================================
        # STAGE 3: DECISION - Make Approval Decision
        # ============================================================
        decision_result = DecisionService.make_agent_decision(wallet_address, credit_score, amount)
        approved = decision_result["approved"]
        interest_rate = decision_result["interest_rate"]
        collateral_required = decision_result["collateral_required"]
        
        # Log decision
        AuditorService.log_event(
            loan_id=request_id,
            agent_name="decision",
            event_type="loan_decision_made",
            details={
                "wallet_address": wallet_address,
                "approved": approved,
                "credit_score": credit_score,
                "interest_rate": interest_rate,
                "collateral_required": collateral_required,
                "message": decision_result.get("message")
            }
        )
        
        # ============================================================
        # STAGE 4: TREASURY - Check Fund Availability
        # ============================================================
        treasury_result = TreasuryService.check_fund_availability_for_agent(wallet_address, amount)
        funds_available = treasury_result["funds_available"]
        
        # Log treasury check
        AuditorService.log_event(
            loan_id=request_id,
            agent_name="treasury",
            event_type="fund_availability_checked",
            details={
                "wallet_address": wallet_address,
                "requested_amount": amount,
                "available_funds": treasury_result["available_funds"],
                "funds_available": funds_available
            }
        )
        
        # ============================================================
        # Final Decision: Approve only if approved by decision AND funds available
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
            final_message = f"Loan approved! Rate: {interest_rate}% Annual, Collateral: ${collateral_required:,.2f}"
        
        # Log final decision
        AuditorService.log_event(
            loan_id=request_id,
            agent_name="auditor",
            event_type="pipeline_complete",
            details={
                "wallet_address": wallet_address,
                "request_id": request_id,
                "final_approved": final_approved,
                "score": credit_score,
                "risk_level": risk_level,
                "interest_rate": final_interest_rate,
                "collateral_required": final_collateral,
                "funds_available": funds_available
            }
        )
        
        # ============================================================
        # STAGE 5: PERSIST TO DATABASE
        # ============================================================
        # Store loan record in Supabase
        try:
            decision_reason = decision_result.get("decision_reason", "Decision made based on credit evaluation")
            
            db_loan = await db_service.create_loan_record(
                wallet_address=wallet_address,
                amount=amount,
                interest_rate=final_interest_rate,
                collateral_required=final_collateral,
                status="approved" if final_approved else "rejected",
                credit_score=credit_score,
                risk_level=risk_level,
                tx_hash=None,  # Will be updated after blockchain transaction
                decision_reason=decision_reason
            )
            
            db_loan_id = db_loan.get("id")
            print(f"[Loan Route] Loan record created in DB: {db_loan_id}")
            
            # Log database persistence
            AuditorService.log_event(
                loan_id=request_id,
                agent_name="persistence",
                event_type="loan_stored_in_db",
                details={
                    "wallet_address": wallet_address,
                    "db_loan_id": db_loan_id,
                    "approved": final_approved
                }
            )
        
        except Exception as db_error:
            # Log database error but don't fail the request
            print(f"[Loan Route] Database error storing loan: {str(db_error)}")
            AuditorService.log_event(
                loan_id=request_id,
                agent_name="persistence",
                event_type="database_error",
                details={
                    "wallet_address": wallet_address,
                    "error": str(db_error)
                }
            )
        
        # ============================================================
        # Return Final Response
        # ============================================================
        return {
            "request_id": request_id,
            "wallet_address": wallet_address,
            "agent_id": wallet_address,  # For backward compatibility with frontend
            "amount_requested": amount,
            "score": credit_score,
            "risk_level": risk_level,
            "confidence": confidence,
            "decision_reason": decision_result.get("decision_reason", "Decision made based on credit evaluation"),
            "interest_rate": final_interest_rate,
            "collateral_required": final_collateral,
            "approved": final_approved,
            "funds_available": funds_available,
            "monthly_payment": decision_result.get("monthly_payment", 0.0) if final_approved else 0.0,
            "total_interest": decision_result.get("total_interest", 0.0) if final_approved else 0.0,
            "message": final_message,
            "db_loan_id": db_loan_id,  # Reference to database record
            "wallet_profile": {
                "success_rate": round(agent_profile.get("success_rate", 0) * 100, 1),
                "transaction_count": agent_profile.get("transaction_count", 0),
                "repayment_history": round(agent_profile.get("repayment_history", 0) * 100, 1),
                "agent_tier": agent_tier
            },
            "agent_profile": {
                "success_rate": round(agent_profile.get("success_rate", 0) * 100, 1),
                "transaction_count": agent_profile.get("transaction_count", 0),
                "repayment_history": round(agent_profile.get("repayment_history", 0) * 100, 1),
                "agent_tier": agent_tier
            },
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_status": {
                "gatekeeper": "valid" if gatekeeper_result.get("valid") else "invalid",
                "analyst": f"score_{int(credit_score)}",
                "decision": "approved" if approved else "rejected",
                "treasury": "available" if funds_available else "unavailable",
                "persistence": "saved" if db_loan_id else "pending"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Loan Route] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response("LOAN_REQUEST_ERROR", str(e))
        )


@router.post("/apply", response_model=LoanApplicationResponse)
async def apply_for_loan(request: LoanRequest) -> LoanApplicationResponse:
    """
    Submit a new loan application.
    
    This endpoint initiates the lending pipeline by creating a new loan
    application and queuing it for processing through all pipeline stages.
    
    Args:
        request: Loan application request
    
    Returns:
        LoanApplicationResponse with initial application status
    
    TODO: Implement:
        - Database persistence
        - Queue message publishing for async processing
        - Initial validation checks
    """
    try:
        # Validate request
        is_valid, errors = RequestValidator.validate_loan_request(request.model_dump())
        if not is_valid:
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        # Generate loan ID
        loan_id = generate_loan_id()
        
        # Create initial loan record
        loan_app = LoanApplicationResponse(
            loan_id=loan_id,
            borrower_id=request.borrower_id,
            status=LoanStatus.PENDING,
            amount_requested=request.amount,
            gatekeeper_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store in memory (replace with DB)
        LOANS_DB[loan_id] = loan_app.model_dump()
        
        # Initialize pipeline stages
        PIPELINE_STAGES[loan_id] = {
            "gatekeeper": None,
            "analyst": None,
            "decision": None,
            "treasury": None,
            "settler": None,
            "auditor": None
        }
        
        # Log application
        AuditorService.log_event(
            loan_id=loan_id,
            agent_name="system",
            event_type="application_submitted",
            details=request.model_dump()
        )
        
        return loan_app
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response("LOAN_APPLICATION_ERROR", str(e))
        )


@router.get("/{loan_id}", response_model=LoanApplicationResponse)
async def get_loan_status(loan_id: str) -> LoanApplicationResponse:
    """
    Get status of a loan application.
    
    Args:
        loan_id: Loan identifier
    
    Returns:
        Current loan application details
    """
    try:
        if loan_id not in LOANS_DB:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found")
        
        return LoanApplicationResponse(**LOANS_DB[loan_id])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response("LOAN_LOOKUP_ERROR", str(e))
        )


@router.post("/{loan_id}/verify")
async def verify_identity(loan_id: str, kyc_data: dict):
    """
    Trigger identity verification (gatekeeper stage).
    
    Args:
        loan_id: Loan identifier
        kyc_data: KYC verification data
    
    Returns:
        Verification result
    
    TODO: Implement:
        - Queue gatekeeper service
        - Async processing
        - Error handling and retries
    """
    try:
        if loan_id not in LOANS_DB:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found")
        
        loan = LOANS_DB[loan_id]
        
        # Call gatekeeper service
        result = GatekeeperService.verify_identity(loan["borrower_id"], kyc_data)
        
        # Update loan with verification result
        loan["gatekeeper_verified"] = result.result.get("verified", False)
        loan["status"] = LoanStatus.VERIFICATION
        loan["updated_at"] = datetime.utcnow().isoformat()
        
        PIPELINE_STAGES[loan_id]["gatekeeper"] = result.model_dump()
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response("VERIFICATION_ERROR", str(e))
        )


@router.post("/{loan_id}/score")
async def calculate_credit_score(loan_id: str, financial_data: dict):
    """
    Trigger credit scoring (analyst stage).
    
    Args:
        loan_id: Loan identifier
        financial_data: Financial information for scoring
    
    Returns:
        Credit score and analysis
    
    TODO: Implement:
        - Queue analyst service
        - Async processing
        - Integration with credit bureaus
    """
    try:
        if loan_id not in LOANS_DB:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found")
        
        loan = LOANS_DB[loan_id]
        
        # Call analyst service
        result = AnalystService.calculate_credit_score(loan["borrower_id"], financial_data)
        
        # Update loan with scoring result
        if result.status == AgentStatus.COMPLETED:
            loan["credit_score"] = result.result.get("credit_score")
            loan["status"] = LoanStatus.SCORING
            loan["updated_at"] = datetime.utcnow().isoformat()
        
        PIPELINE_STAGES[loan_id]["analyst"] = result.model_dump()
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response("SCORING_ERROR", str(e))
        )


@router.post("/{loan_id}/decide")
async def make_loan_decision(loan_id: str):
    """
    Trigger loan decision stage.
    
    Evaluates all previous pipeline results and makes approval decision.
    
    Args:
        loan_id: Loan identifier
    
    Returns:
        Loan decision and terms
    
    TODO: Implement:
        - Queue decision service
        - Collect all prior stage results
        - Async orchestration
    """
    try:
        if loan_id not in LOANS_DB:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found")
        
        loan = LOANS_DB[loan_id]
        
        # Gather pipeline results for decision
        credit_score = loan.get("credit_score", 600)
        gatekeeper_verified = loan.get("gatekeeper_verified", False)
        debt_to_income = 0.30  # Placeholder - should come from analyst stage
        
        # Call decision service
        result = DecisionService.make_decision(
            borrower_id=loan["borrower_id"],
            loan_amount=loan["amount_requested"],
            credit_score=credit_score,
            gatekeeper_verified=gatekeeper_verified,
            debt_to_income=debt_to_income,
            pipeline_data=PIPELINE_STAGES[loan_id]
        )
        
        # Update loan with decision
        if result.result.get("decision") == "approved":
            loan["decision"] = "approved"
            loan["interest_rate"] = result.result.get("interest_rate")
            loan["approved_amount"] = result.result.get("approved_amount")
            loan["status"] = LoanStatus.APPROVED
        else:
            loan["decision"] = "rejected"
            loan["status"] = LoanStatus.REJECTED
        
        loan["updated_at"] = datetime.utcnow().isoformat()
        PIPELINE_STAGES[loan_id]["decision"] = result.model_dump()
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response("DECISION_ERROR", str(e))
        )


@router.get("/{loan_id}/pipeline")
async def get_pipeline_status(loan_id: str) -> PipelineStatusResponse:
    """
    Get current status of all pipeline stages for a loan.
    
    Args:
        loan_id: Loan identifier
    
    Returns:
        Status of all pipeline stages
    """
    try:
        if loan_id not in LOANS_DB:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found")
        
        stages = PIPELINE_STAGES.get(loan_id, {})
        
        # Calculate completion percentage
        completed_stages = sum(1 for v in stages.values() if v is not None)
        total_stages = len(stages)
        completion_percentage = (completed_stages / total_stages * 100) if total_stages > 0 else 0
        
        return PipelineStatusResponse(
            loan_id=loan_id,
            stages=stages,
            overall_status=LOANS_DB[loan_id].get("status", "pending"),
            completion_percentage=completion_percentage
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response("PIPELINE_STATUS_ERROR", str(e))
        )


@router.get("/{loan_id}/audit-trail")
async def get_audit_trail(loan_id: str):
    """
    Get complete audit trail for a loan.
    
    Args:
        loan_id: Loan identifier
    
    Returns:
        Audit trail of all events for the loan
    """
    try:
        if loan_id not in LOANS_DB:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found")
        
        result = AuditorService.get_audit_trail(loan_id)
        return result.model_dump()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response("AUDIT_TRAIL_ERROR", str(e))
        )


@router.post("/{loan_id}/disburse")
async def disburse_loan(
    loan_id: str,
    disbursement_method: str = Query("bank_transfer")
):
    """
    Trigger loan fund disbursement (settler stage).
    
    Args:
        loan_id: Loan identifier
        disbursement_method: Method of disbursement
    
    Returns:
        Disbursement result
    
    TODO: Implement:
        - Queue settler service
        - Verify approval status
        - Track disbursement status
    """
    try:
        if loan_id not in LOANS_DB:
            raise HTTPException(status_code=404, detail=f"Loan {loan_id} not found")
        
        loan = LOANS_DB[loan_id]
        
        # Check if approved
        if loan.get("decision") != "approved":
            raise HTTPException(
                status_code=400,
                detail="Only approved loans can be disbursed"
            )
        
        # Call settler service
        result = SettlerService.disburse_funds(
            loan_id=loan_id,
            borrower_id=loan["borrower_id"],
            amount=loan.get("approved_amount", loan["amount_requested"]),
            disbursement_method=disbursement_method
        )
        
        # Update loan status
        if result.status == AgentStatus.COMPLETED:
            loan["status"] = LoanStatus.FUNDED
            loan["updated_at"] = datetime.utcnow().isoformat()
        
        PIPELINE_STAGES[loan_id]["settler"] = result.model_dump()
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response("DISBURSEMENT_ERROR", str(e))
        )
