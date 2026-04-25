#!/usr/bin/env python3
"""
API Usage Examples - Complete Loan Processing Flow

This script demonstrates how to use the AI Agent Credit System API
to process a loan from application through disbursement.

Run with: python examples.py

Prerequisites:
1. Start the server: uvicorn app.main:app --reload
2. Install dependencies: pip install -r requirements.txt
"""

import requests
import json
import time
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000"


class LoanAPIClient:
    """Client for interacting with the Loan API."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def apply_for_loan(self, borrower_id: str, amount: float, 
                      duration_months: int, purpose: str) -> Dict[str, Any]:
        """Submit a new loan application."""
        payload = {
            "borrower_id": borrower_id,
            "amount": amount,
            "duration_months": duration_months,
            "purpose": purpose
        }
        response = self.session.post(
            f"{self.base_url}/loan/apply",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def verify_identity(self, loan_id: str, kyc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify borrower identity."""
        response = self.session.post(
            f"{self.base_url}/loan/{loan_id}/verify",
            json=kyc_data
        )
        response.raise_for_status()
        return response.json()
    
    def calculate_credit_score(self, loan_id: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate credit score."""
        response = self.session.post(
            f"{self.base_url}/loan/{loan_id}/score",
            json=financial_data
        )
        response.raise_for_status()
        return response.json()
    
    def make_decision(self, loan_id: str) -> Dict[str, Any]:
        """Make loan decision."""
        response = self.session.post(
            f"{self.base_url}/loan/{loan_id}/decide"
        )
        response.raise_for_status()
        return response.json()
    
    def get_pipeline_status(self, loan_id: str) -> Dict[str, Any]:
        """Get pipeline status."""
        response = self.session.get(
            f"{self.base_url}/loan/{loan_id}/pipeline"
        )
        response.raise_for_status()
        return response.json()
    
    def disburse_funds(self, loan_id: str, method: str = "bank_transfer") -> Dict[str, Any]:
        """Disburse funds."""
        response = self.session.post(
            f"{self.base_url}/loan/{loan_id}/disburse",
            params={"disbursement_method": method}
        )
        response.raise_for_status()
        return response.json()
    
    def get_audit_trail(self, loan_id: str) -> Dict[str, Any]:
        """Get audit trail."""
        response = self.session.get(
            f"{self.base_url}/loan/{loan_id}/audit-trail"
        )
        response.raise_for_status()
        return response.json()


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_json(data: Dict[str, Any]):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2, default=str))


def main():
    """Run complete loan processing flow."""
    
    # Initialize client
    client = LoanAPIClient()
    
    # Check API health
    print_header("1. Health Check")
    health = client.health_check()
    print_json(health)
    
    # Submit loan application
    print_header("2. Submit Loan Application")
    loan = client.apply_for_loan(
        borrower_id="BORROWER-001",
        amount=50000,
        duration_months=36,
        purpose="Business expansion"
    )
    print_json(loan)
    loan_id = loan["loan_id"]
    print(f"✓ Loan created: {loan_id}")
    
    # Small delay for demonstration
    time.sleep(1)
    
    # Verify identity
    print_header("3. Verify Identity (Gatekeeper)")
    kyc_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-1234",
        "address": "123 Main St, Anytown, USA"
    }
    verification = client.verify_identity(loan_id, kyc_data)
    print_json(verification)
    print(f"✓ Verification status: {verification['result'].get('verified')}")
    
    # Small delay for demonstration
    time.sleep(1)
    
    # Calculate credit score
    print_header("4. Calculate Credit Score (Analyst)")
    financial_data = {
        "monthly_gross_income": 8000,
        "total_monthly_debt": 2000,
        "payment_history_clean": True,
        "employment_years": 5,
        "long_credit_history": True,
        "multiple_accounts": True
    }
    score = client.calculate_credit_score(loan_id, financial_data)
    print_json(score)
    if score.get('result'):
        credit_score = score['result'].get('credit_score')
        print(f"✓ Credit score: {credit_score}")
    
    # Small delay for demonstration
    time.sleep(1)
    
    # Make loan decision
    print_header("5. Make Loan Decision (Decision)")
    decision = client.make_decision(loan_id)
    print_json(decision)
    if decision.get('result'):
        app_decision = decision['result'].get('decision')
        print(f"✓ Decision: {app_decision}")
    
    # Small delay for demonstration
    time.sleep(1)
    
    # Check pipeline status
    print_header("6. Check Pipeline Status")
    pipeline = client.get_pipeline_status(loan_id)
    print_json(pipeline)
    print(f"✓ Pipeline completion: {pipeline.get('completion_percentage', 0):.0f}%")
    
    # Small delay for demonstration
    time.sleep(1)
    
    # Disburse funds
    print_header("7. Disburse Funds (Settler)")
    disbursement = client.disburse_funds(loan_id)
    print_json(disbursement)
    if disbursement.get('result'):
        success = disbursement['result'].get('disbursement_successful')
        print(f"✓ Disbursement successful: {success}")
    
    # Small delay for demonstration
    time.sleep(1)
    
    # Get audit trail
    print_header("8. Get Audit Trail (Auditor)")
    audit = client.get_audit_trail(loan_id)
    print(f"Total audit events: {audit.get('total_events', 0)}")
    if audit.get('audit_trail'):
        for log in audit['audit_trail'][:3]:  # Show first 3 events
            print(f"  - {log.get('event_type')}: {log.get('agent_name')}")
    
    print_header("Loan Processing Complete!")
    print(f"Loan ID: {loan_id}")
    print("✓ Application submitted")
    print("✓ Identity verified")
    print("✓ Credit scored")
    print("✓ Decision made")
    print("✓ Funds disbursed")
    print("✓ Audit logged")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API")
        print("Make sure the server is running:")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
