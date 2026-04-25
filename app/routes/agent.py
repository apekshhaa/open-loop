"""
Agent Management Routes

Defines API endpoints for agent identity verification and management.
Implements the KYA (Know Your Agent) layer with wallet-based identity.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.services.db_service import SupabaseService
from app.services.reputation_service import ReputationService
from app.services.wallet_utils import validate_wallet_address, normalize_wallet_address
from app.utils import generate_loan_id, create_error_response


router = APIRouter(prefix="/agent", tags=["identity-kya"])


@router.get("/{wallet_address}")
async def get_agent_profile(wallet_address: str):
    """
    Get agent's complete identity profile.
    
    Returns wallet-based identity information including:
    - Reputation score
    - Status (Verified, Risky, Established, New Agent)
    - Loan history and repayment metrics
    - Activity level and behavioral data
    
    Args:
        wallet_address: Ethereum wallet address (0x...)
    
    Returns:
        Structured agent identity profile
    """
    try:
        # Validate wallet format
        if not validate_wallet_address(wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid wallet address format. Must be 0x followed by 40 hex characters."
            )
        
        # Normalize wallet address
        wallet_lower = normalize_wallet_address(wallet_address)
        
        # Get database service
        db_service = SupabaseService.get_instance()
        
        # Retrieve agent from database
        agent = await db_service.get_agent(wallet_lower)
        
        if not agent:
            # Return default profile for unknown agents
            return {
                "wallet": wallet_lower[:6] + "..." + wallet_lower[-4:],
                "wallet_full": wallet_lower,
                "status": "Unknown",
                "score": 0,
                "message": "Agent not found. Create account to get started.",
                "history": {
                    "total_loans": 0,
                    "successful_repays": 0,
                    "failed_loans": 0
                }
            }
        
        # Build comprehensive identity profile
        profile = ReputationService.build_identity_profile(agent)
        
        return {
            "success": True,
            "data": profile,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as error:
        print(f"[AGENT] Error in get_agent_profile: {str(error)}")
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/create")
async def create_agent(
    wallet_address: str = Query(..., description="Ethereum wallet address"),
    initial_trust_score: Optional[float] = Query(50.0, description="Initial trust score (0-100)")
):
    """
    Create new agent account with wallet-based identity.
    
    Initializes agent record with:
    - Wallet as unique identifier
    - Default metrics (total_loans=0, activity=low, etc.)
    - Initial trust score
    - Account creation timestamp
    
    Args:
        wallet_address: Ethereum wallet address (0x...)
        initial_trust_score: Starting reputation score (default 50.0)
    
    Returns:
        Created agent profile
    """
    try:
        # Validate wallet format
        if not validate_wallet_address(wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid wallet address format. Must be 0x followed by 40 hex characters."
            )
        
        # Validate trust score range
        if not (0 <= initial_trust_score <= 100):
            raise HTTPException(
                status_code=400,
                detail="initial_trust_score must be between 0 and 100"
            )
        
        # Normalize wallet address
        wallet_lower = normalize_wallet_address(wallet_address)
        
        # Get database service
        db_service = SupabaseService.get_instance()
        
        # Check if agent already exists
        existing_agent = await db_service.get_agent(wallet_lower)
        if existing_agent:
            raise HTTPException(
                status_code=409,
                detail=f"Agent already exists: {wallet_lower}"
            )
        
        # Create new agent
        agent = await db_service.get_or_create_agent(
            wallet_lower,
            trust_score=initial_trust_score
        )
        
        # Build response profile
        profile = ReputationService.build_identity_profile(agent)
        
        return {
            "success": True,
            "message": f"Agent created successfully",
            "data": profile,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as error:
        print(f"[AGENT] Error in create_agent: {str(error)}")
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/update")
async def update_agent(
    wallet_address: str = Query(..., description="Ethereum wallet address"),
    event_type: str = Query(..., description="Event type: 'repayment_success', 'repayment_failure', or 'loan_approval'"),
    loan_amount: Optional[float] = Query(None, description="Loan amount (for loan_approval event)")
):
    """
    Update agent metrics and reputation based on events.
    
    Supported events:
    - "repayment_success": Increment successful repayments, recalculate score
    - "repayment_failure": Increment failed loans, recalculate score
    - "loan_approval": Update metrics (avg_loan, activity, transactions)
    
    Args:
        wallet_address: Ethereum wallet address (0x...)
        event_type: Type of event that occurred
        loan_amount: Amount of loan (required for loan_approval event)
    
    Returns:
        Updated agent profile
    """
    try:
        # Validate wallet format
        if not validate_wallet_address(wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid wallet address format. Must be 0x followed by 40 hex characters."
            )
        
        # Normalize wallet address
        wallet_lower = normalize_wallet_address(wallet_address)
        
        # Validate event type
        valid_events = ["repayment_success", "repayment_failure", "loan_approval"]
        if event_type not in valid_events:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event_type. Must be one of: {', '.join(valid_events)}"
            )
        
        # Get database service
        db_service = SupabaseService.get_instance()
        
        # Check if agent exists
        agent = await db_service.get_agent(wallet_lower)
        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent not found: {wallet_lower}"
            )
        
        # Process event
        if event_type == "repayment_success":
            agent = await db_service.increment_successful_repays(wallet_lower)
        
        elif event_type == "repayment_failure":
            agent = await db_service.increment_failed_loans(wallet_lower)
        
        elif event_type == "loan_approval":
            if loan_amount is None or loan_amount <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="loan_amount is required and must be positive for loan_approval event"
                )
            agent = await db_service.update_agent_metrics(wallet_lower, loan_amount)
        
        # Recalculate reputation score
        new_score = await db_service.calculate_reputation_score(wallet_lower)
        
        # Build updated profile
        profile = ReputationService.build_identity_profile(agent)
        
        return {
            "success": True,
            "message": f"Agent updated: {event_type}",
            "data": profile,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as error:
        print(f"[AGENT] Error in update_agent: {str(error)}")
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/verify/{wallet_address}")
async def verify_agent_identity(wallet_address: str):
    """
    Verify agent identity and get identity verification status.
    
    Returns:
    - Identity status (Verified, Risky, Established, New Agent)
    - Risk assessment
    - Trust level
    - Recommendation for lending
    
    Args:
        wallet_address: Ethereum wallet address (0x...)
    
    Returns:
        Identity verification result with trust metrics
    """
    try:
        # Validate wallet format
        if not validate_wallet_address(wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid wallet address format. Must be 0x followed by 40 hex characters."
            )
        
        # Normalize wallet address
        wallet_lower = normalize_wallet_address(wallet_address)
        
        # Get database service
        db_service = SupabaseService.get_instance()
        
        # Get identity status from database
        identity_status = await db_service.get_agent_identity_status(wallet_lower)
        
        if "error" in identity_status:
            # Agent not found - return default status
            return {
                "success": True,
                "verification": {
                    "wallet": wallet_lower[:6] + "..." + wallet_lower[-4:],
                    "wallet_full": wallet_lower,
                    "status": "Unknown",
                    "verified": False,
                    "score": 0,
                    "can_approve_loan": False
                },
                "metrics": {
                    "total_loans": 0,
                    "successful_repays": 0,
                    "failed_loans": 0,
                    "activity": "low"
                },
                "risk": {
                    "risk_level": "unknown",
                    "risk_score": 50,
                    "factors": ["Agent not found in database"]
                },
                "message": "Agent not found. Create account to get started.",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get agent for risk assessment
        agent = await db_service.get_agent(wallet_lower)
        if not agent:
            risk_assessment = {
                "risk_level": "unknown",
                "risk_score": 50,
                "factors": ["Agent not found in database"]
            }
            can_approve = False
        else:
            risk_assessment = ReputationService.get_risk_assessment(
                agent.get("trust_score", 50.0),
                agent.get("failed_loans", 0),
                agent.get("total_loans", 0)
            )
            can_approve = identity_status.get("status", "Unknown") in ["Verified", "Established"]
        
        return {
            "success": True,
            "verification": {
                "wallet": wallet_lower[:6] + "..." + wallet_lower[-4:],
                "wallet_full": wallet_lower,
                "status": identity_status.get("status", "Unknown"),
                "verified": identity_status.get("status", "Unknown") == "Verified",
                "score": identity_status.get("score", 0),
                "can_approve_loan": can_approve
            },
            "metrics": {
                "total_loans": identity_status.get("total_loans", 0),
                "successful_repays": identity_status.get("successful_repays", 0),
                "failed_loans": identity_status.get("failed_loans", 0),
                "activity": identity_status.get("activity", "low")
            },
            "risk": risk_assessment,
            "message": f"Agent {identity_status.get('status', 'Unknown')}: {risk_assessment['risk_level']} risk",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as error:
        print(f"[AGENT] Error in verify_agent_identity: {str(error)}")
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/stats/{wallet_address}")
async def get_agent_stats(wallet_address: str):
    """
    Get comprehensive statistics for an agent.
    
    Includes:
    - Loan approval/rejection rates
    - Approval rate percentage
    - Total amounts
    - Average interest rates
    - Account age
    
    Args:
        wallet_address: Ethereum wallet address (0x...)
    
    Returns:
        Comprehensive agent statistics
    """
    try:
        # Validate wallet format
        if not validate_wallet_address(wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid wallet address format. Must be 0x followed by 40 hex characters."
            )
        
        # Normalize wallet address
        wallet_lower = normalize_wallet_address(wallet_address)
        
        # Get database service
        db_service = SupabaseService.get_instance()
        
        # Get statistics
        stats = await db_service.get_agent_statistics(wallet_lower)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats.get("error"))
        
        return {
            "success": True,
            "wallet": wallet_lower[:6] + "..." + wallet_lower[-4:],
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as error:
        print(f"[AGENT] Error in get_agent_stats: {str(error)}")
        raise HTTPException(status_code=500, detail=str(error))
