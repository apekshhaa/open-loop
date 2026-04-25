"""
Supabase Database Service

Provides database abstraction layer for agent and loan data persistence.
Handles CRUD operations for agents table and loans table.
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import asynccontextmanager

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    create_client = None
    Client = None


class SupabaseService:
    """
    Supabase database service for managing agent and loan data.
    
    Handles all database operations for the AI Agent Credit System.
    Tables: agents, loans
    """
    
    _instance: Optional["SupabaseService"] = None
    _client: Optional[Client] = None
    
    def __init__(self):
        """Initialize Supabase client from environment variables."""
        if not SUPABASE_AVAILABLE:
            print("[DB] WARNING: Supabase module not available. Database operations will fail.")
            print("[DB] Install with: pip install supabase==2.3.4")
            self.client = None
            return
        
        supabase_url = os.getenv("SUPABASE_URL")
        # Try both SUPABASE_ANON_KEY and SUPABASE_API_KEY for compatibility
        supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_API_KEY")
        
        if not supabase_url or not supabase_key:
            print("[DB] WARNING: SUPABASE_URL or SUPABASE_ANON_KEY not configured")
            print("[DB] Database operations will not work. Set environment variables to enable persistence.")
            self.client = None
            return
        
        try:
            self.client: Client = create_client(supabase_url, supabase_key)
            print(f"[DB] Supabase client initialized successfully")
        except Exception as e:
            print(f"[DB] Error initializing Supabase client: {str(e)}")
            self.client = None
    
    @classmethod
    def get_instance(cls) -> "SupabaseService":
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = SupabaseService()
        return cls._instance
    
    # ========================
    # AGENTS TABLE OPERATIONS
    # ========================
    
    async def get_or_create_agent(
        self,
        wallet_address: str,
        trust_score: float = 50.0
    ) -> Dict[str, Any]:
        """
        Get existing agent or create new one if not found.
        
        Args:
            wallet_address: Ethereum wallet address (normalized, lowercase)
            trust_score: Initial trust score for new agents (default 50.0)
        
        Returns:
            Agent record from database
        """
        if not self.client:
            # Database not configured, return mock agent
            print(f"[DB] Database not configured, using mock agent for: {wallet_address}")
            return {
                "id": None,
                "wallet_address": wallet_address,
                "trust_score": trust_score,
                "total_loans": 0,
                "successful_repays": 0,
                "failed_loans": 0,
                "avg_loan": 0.0,
                "activity": "low",
                "transactions": 0,
                "created_at": datetime.utcnow().isoformat()
            }
        
        try:
            # Check if agent exists
            response = self.client.table("agents").select("*").eq(
                "wallet_address", wallet_address
            ).execute()
            
            if response.data and len(response.data) > 0:
                # Agent exists, return it
                agent = response.data[0]
                print(f"[DB] Agent found: {wallet_address}")
                return agent
            
            # Agent doesn't exist, create new one
            new_agent = {
                "wallet_address": wallet_address,
                "created_at": datetime.utcnow().isoformat(),
                "trust_score": trust_score,
                "total_loans": 0,
                "successful_repays": 0,
                "failed_loans": 0,
                "avg_loan": 0.0,
                "activity": "low",
                "transactions": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("agents").insert(new_agent).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[DB] Agent created: {wallet_address}")
                return response.data[0]
            else:
                raise Exception("Failed to create agent")
        
        except Exception as error:
            print(f"[DB] Error in get_or_create_agent: {str(error)}")
            raise
    
    async def get_agent(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        Get agent by wallet address.
        
        Args:
            wallet_address: Ethereum wallet address
        
        Returns:
            Agent record or None if not found
        """
        try:
            response = self.client.table("agents").select("*").eq(
                "wallet_address", wallet_address
            ).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        
        except Exception as error:
            print(f"[DB] Error in get_agent: {str(error)}")
            return None
    
    async def update_agent_trust_score(
        self,
        wallet_address: str,
        trust_score: float
    ) -> Dict[str, Any]:
        """
        Update agent's trust score.
        
        Args:
            wallet_address: Ethereum wallet address
            trust_score: New trust score (0-100)
        
        Returns:
            Updated agent record
        """
        try:
            response = self.client.table("agents").update({
                "trust_score": trust_score
            }).eq("wallet_address", wallet_address).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[DB] Updated trust score for {wallet_address}: {trust_score}")
                return response.data[0]
            else:
                raise Exception("Failed to update trust score")
        
        except Exception as error:
            print(f"[DB] Error in update_agent_trust_score: {str(error)}")
            raise
    
    async def increment_agent_loans(self, wallet_address: str) -> Dict[str, Any]:
        """
        Increment total_loans counter for agent.
        
        Args:
            wallet_address: Ethereum wallet address
        
        Returns:
            Updated agent record
        """
        try:
            # Get current count
            agent = await self.get_agent(wallet_address)
            if not agent:
                raise ValueError(f"Agent not found: {wallet_address}")
            
            new_count = agent.get("total_loans", 0) + 1
            
            # Update count
            response = self.client.table("agents").update({
                "total_loans": new_count
            }).eq("wallet_address", wallet_address).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[DB] Updated loan count for {wallet_address}: {new_count}")
                return response.data[0]
            else:
                raise Exception("Failed to increment loan count")
        
        except Exception as error:
            print(f"[DB] Error in increment_agent_loans: {str(error)}")
            raise
    
    async def get_agent_loan_history(
        self,
        wallet_address: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get loan history for an agent.
        
        Args:
            wallet_address: Ethereum wallet address
            limit: Maximum number of records to return
        
        Returns:
            List of loan records
        """
        try:
            response = self.client.table("loans").select("*").eq(
                "wallet_address", wallet_address
            ).order("created_at", desc=True).limit(limit).execute()
            
            return response.data if response.data else []
        
        except Exception as error:
            print(f"[DB] Error in get_agent_loan_history: {str(error)}")
            return []
    
    # ========================
    # LOANS TABLE OPERATIONS
    # ========================
    
    async def create_loan_record(
        self,
        wallet_address: str,
        amount: float,
        interest_rate: float,
        collateral_required: float,
        status: str,  # "approved" or "rejected"
        credit_score: float,
        risk_level: str,
        tx_hash: Optional[str] = None,
        decision_reason: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new loan record.
        
        Args:
            wallet_address: Ethereum wallet address
            amount: Loan amount requested
            interest_rate: Interest rate if approved
            collateral_required: Collateral required
            status: "approved" or "rejected"
            credit_score: Credit score calculated
            risk_level: Risk level (low/medium/high/very_high)
            tx_hash: Transaction hash (optional)
            decision_reason: Reason for decision
        
        Returns:
            Created loan record
        """
        if not self.client:
            # Database not configured, return mock loan record
            print(f"[DB] Database not configured, using mock loan for: {wallet_address}")
            return {
                "id": None,
                "wallet_address": wallet_address,
                "amount": amount,
                "interest_rate": interest_rate,
                "collateral_required": collateral_required,
                "status": status,
                "credit_score": credit_score,
                "risk_level": risk_level,
                "tx_hash": tx_hash,
                "decision_reason": decision_reason,
                "created_at": datetime.utcnow().isoformat()
            }
        
        try:
            loan_record = {
                "wallet_address": wallet_address,
                "amount": amount,
                "interest_rate": interest_rate,
                "collateral_required": collateral_required,
                "status": status,
                "credit_score": credit_score,
                "risk_level": risk_level,
                "tx_hash": tx_hash,
                "decision_reason": decision_reason,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            response = self.client.table("loans").insert(loan_record).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[DB] Loan record created for {wallet_address}")
                # Increment agent's loan count if approved
                if status == "approved":
                    await self.increment_agent_loans(wallet_address)
                return response.data[0]
            else:
                raise Exception("Failed to create loan record")
        
        except Exception as error:
            print(f"[DB] Error in create_loan_record: {str(error)}")
            raise
    
    async def get_loan(self, loan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get loan by ID.
        
        Args:
            loan_id: Loan record ID
        
        Returns:
            Loan record or None if not found
        """
        try:
            response = self.client.table("loans").select("*").eq(
                "id", loan_id
            ).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        
        except Exception as error:
            print(f"[DB] Error in get_loan: {str(error)}")
            return None
    
    async def update_loan_tx_hash(
        self,
        loan_id: str,
        tx_hash: str
    ) -> Dict[str, Any]:
        """
        Update loan record with transaction hash after blockchain execution.
        
        Args:
            loan_id: Loan record ID
            tx_hash: Blockchain transaction hash
        
        Returns:
            Updated loan record
        """
        try:
            response = self.client.table("loans").update({
                "tx_hash": tx_hash
            }).eq("id", loan_id).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[DB] Updated tx_hash for loan {loan_id}: {tx_hash}")
                return response.data[0]
            else:
                raise Exception("Failed to update loan tx_hash")
        
        except Exception as error:
            print(f"[DB] Error in update_loan_tx_hash: {str(error)}")
            raise
    
    async def get_loans_by_status(
        self,
        status: str,  # "approved" or "rejected"
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all loans with a specific status.
        
        Args:
            status: Loan status ("approved" or "rejected")
            limit: Maximum number of records
        
        Returns:
            List of loan records
        """
        try:
            response = self.client.table("loans").select("*").eq(
                "status", status
            ).order("created_at", desc=True).limit(limit).execute()
            
            return response.data if response.data else []
        
        except Exception as error:
            print(f"[DB] Error in get_loans_by_status: {str(error)}")
            return []
    
    # ========================
    # STATISTICS & REPORTING
    # ========================
    
    async def get_agent_statistics(
        self,
        wallet_address: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive statistics for an agent.
        
        Args:
            wallet_address: Ethereum wallet address
        
        Returns:
            Statistics dictionary with loan counts, approval rate, etc.
        """
        try:
            agent = await self.get_agent(wallet_address)
            if not agent:
                return {"error": "Agent not found"}
            
            # Get all loans for this agent
            loans = await self.get_agent_loan_history(wallet_address, limit=1000)
            
            # Calculate statistics
            total_loans = len(loans)
            approved_loans = len([l for l in loans if l.get("status") == "approved"])
            rejected_loans = len([l for l in loans if l.get("status") == "rejected"])
            total_amount = sum([l.get("amount", 0) for l in loans])
            avg_rate = (
                sum([l.get("interest_rate", 0) for l in loans if l.get("status") == "approved"])
                / approved_loans
                if approved_loans > 0
                else 0
            )
            
            approval_rate = (
                (approved_loans / total_loans * 100)
                if total_loans > 0
                else 0
            )
            
            return {
                "wallet_address": wallet_address,
                "total_loans_requested": total_loans,
                "approved_loans": approved_loans,
                "rejected_loans": rejected_loans,
                "approval_rate_percent": round(approval_rate, 2),
                "total_amount_requested": total_amount,
                "average_interest_rate": round(avg_rate, 2),
                "current_trust_score": agent.get("trust_score", 50),
                "account_age_days": self._calculate_age_days(agent.get("created_at", "")),
            }
        
        except Exception as error:
            print(f"[DB] Error in get_agent_statistics: {str(error)}")
            return {"error": str(error)}
    
    def _calculate_age_days(self, created_at_str: str) -> int:
        """Calculate days since account creation."""
        if not created_at_str:
            return 0
        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            age = datetime.utcnow() - created_at.replace(tzinfo=None)
            return age.days
        except:
            return 0
    
    # ========================
    # REPUTATION SYSTEM
    # ========================
    
    async def increment_successful_repays(self, wallet_address: str) -> Dict[str, Any]:
        """
        Increment successful repayments counter and recalculate reputation.
        
        Args:
            wallet_address: Ethereum wallet address
        
        Returns:
            Updated agent record
        """
        if not self.client:
            print(f"[DB] Database not configured, skipping increment_successful_repays")
            return {}
        
        try:
            agent = await self.get_agent(wallet_address)
            if not agent:
                raise ValueError(f"Agent not found: {wallet_address}")
            
            new_count = agent.get("successful_repays", 0) + 1
            total_loans = agent.get("total_loans", 1)
            
            # Recalculate reputation score
            reputation_score = (new_count / total_loans * 100) if total_loans > 0 else 0
            
            # Update agent record
            response = self.client.table("agents").update({
                "successful_repays": new_count,
                "trust_score": reputation_score,
                "last_updated": datetime.utcnow().isoformat()
            }).eq("wallet_address", wallet_address).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[DB] Incremented successful_repays for {wallet_address}: {new_count}, new score: {reputation_score}")
                return response.data[0]
            else:
                raise Exception("Failed to increment successful repays")
        
        except Exception as error:
            print(f"[DB] Error in increment_successful_repays: {str(error)}")
            raise
    
    async def increment_failed_loans(self, wallet_address: str) -> Dict[str, Any]:
        """
        Increment failed loans counter and recalculate reputation.
        
        Args:
            wallet_address: Ethereum wallet address
        
        Returns:
            Updated agent record
        """
        if not self.client:
            print(f"[DB] Database not configured, skipping increment_failed_loans")
            return {}
        
        try:
            agent = await self.get_agent(wallet_address)
            if not agent:
                raise ValueError(f"Agent not found: {wallet_address}")
            
            new_count = agent.get("failed_loans", 0) + 1
            total_loans = agent.get("total_loans", 1)
            successful_repays = agent.get("successful_repays", 0)
            
            # Recalculate reputation score (based on successful repays, not all)
            reputation_score = (successful_repays / total_loans * 100) if total_loans > 0 else 0
            
            # Update agent record
            response = self.client.table("agents").update({
                "failed_loans": new_count,
                "trust_score": reputation_score,
                "last_updated": datetime.utcnow().isoformat()
            }).eq("wallet_address", wallet_address).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[DB] Incremented failed_loans for {wallet_address}: {new_count}, new score: {reputation_score}")
                return response.data[0]
            else:
                raise Exception("Failed to increment failed loans")
        
        except Exception as error:
            print(f"[DB] Error in increment_failed_loans: {str(error)}")
            raise
    
    async def update_agent_metrics(
        self,
        wallet_address: str,
        loan_amount: float
    ) -> Dict[str, Any]:
        """
        Update agent metrics including average loan amount and activity level.
        
        Args:
            wallet_address: Ethereum wallet address
            loan_amount: Amount of current loan
        
        Returns:
            Updated agent record
        """
        if not self.client:
            print(f"[DB] Database not configured, skipping update_agent_metrics")
            return {}
        
        try:
            agent = await self.get_agent(wallet_address)
            if not agent:
                raise ValueError(f"Agent not found: {wallet_address}")
            
            total_loans = agent.get("total_loans", 0)
            current_avg = agent.get("avg_loan", 0.0)
            transactions = agent.get("transactions", 0) + 1
            
            # Recalculate average loan amount
            if total_loans > 0:
                new_avg = ((current_avg * (total_loans - 1)) + loan_amount) / total_loans
            else:
                new_avg = loan_amount
            
            # Determine activity level based on transaction count
            if transactions >= 10:
                activity = "high"
            elif transactions >= 5:
                activity = "medium"
            else:
                activity = "low"
            
            # Update agent record
            response = self.client.table("agents").update({
                "avg_loan": round(new_avg, 2),
                "activity": activity,
                "transactions": transactions,
                "last_updated": datetime.utcnow().isoformat()
            }).eq("wallet_address", wallet_address).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[DB] Updated metrics for {wallet_address}: avg_loan={new_avg}, activity={activity}, transactions={transactions}")
                return response.data[0]
            else:
                raise Exception("Failed to update agent metrics")
        
        except Exception as error:
            print(f"[DB] Error in update_agent_metrics: {str(error)}")
            raise
    
    async def calculate_reputation_score(self, wallet_address: str) -> float:
        """
        Calculate reputation score based on repayment history.
        
        Formula: score = (successful_repays / total_loans) * 100
        
        Args:
            wallet_address: Ethereum wallet address
        
        Returns:
            Reputation score (0-100)
        """
        try:
            agent = await self.get_agent(wallet_address)
            if not agent:
                return 50.0  # Default for new agents
            
            total_loans = agent.get("total_loans", 0)
            successful_repays = agent.get("successful_repays", 0)
            
            if total_loans == 0:
                return 50.0  # Default for agents with no loans
            
            score = (successful_repays / total_loans) * 100
            return min(100.0, max(0.0, score))  # Clamp between 0-100
        
        except Exception as error:
            print(f"[DB] Error in calculate_reputation_score: {str(error)}")
            return 50.0
    
    async def get_agent_identity_status(self, wallet_address: str) -> Dict[str, Any]:
        """
        Get agent's identity status (Verified, Risky, or New Agent).
        
        Classification logic:
        - "Verified": total_loans > 0 AND score >= 70
        - "Risky": score < 50
        - "New Agent": total_loans == 0
        
        Args:
            wallet_address: Ethereum wallet address
        
        Returns:
            Identity status with classification
        """
        try:
            agent = await self.get_agent(wallet_address)
            if not agent:
                return {"status": "Unknown", "wallet": wallet_address}
            
            total_loans = agent.get("total_loans", 0)
            score = agent.get("trust_score", 50.0)
            
            # Classify status
            if total_loans == 0:
                status = "New Agent"
            elif score >= 70:
                status = "Verified"
            elif score < 50:
                status = "Risky"
            else:
                status = "Established"
            
            return {
                "wallet": wallet_address,
                "status": status,
                "score": score,
                "total_loans": total_loans,
                "successful_repays": agent.get("successful_repays", 0),
                "failed_loans": agent.get("failed_loans", 0),
                "activity": agent.get("activity", "low"),
                "avg_loan": agent.get("avg_loan", 0.0),
                "created_at": agent.get("created_at", "")
            }
        
        except Exception as error:
            print(f"[DB] Error in get_agent_identity_status: {str(error)}")
            return {"status": "Unknown", "error": str(error)}
    
    # ========================
    # HEALTH CHECK
    # ========================
    
    async def health_check(self) -> bool:
        """
        Check if database is reachable.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.client:
            print("[DB] Database not configured - health check skipped")
            return False
        
        try:
            response = self.client.table("agents").select("count", count="exact").execute()
            print("[DB] Health check passed")
            return True
        except Exception as error:
            print(f"[DB] Health check failed: {str(error)}")
            return False


# Singleton instance
_db_service: Optional[SupabaseService] = None


def get_db_service() -> SupabaseService:
    """Get or create the database service singleton."""
    global _db_service
    if _db_service is None:
        _db_service = SupabaseService.get_instance()
    return _db_service


async def init_db_service() -> SupabaseService:
    """Initialize the database service."""
    service = SupabaseService.get_instance()
    # Test connection
    if await service.health_check():
        print("[DB] Database service initialized successfully")
    else:
        print("[DB] Warning: Database connection failed during initialization")
    return service
