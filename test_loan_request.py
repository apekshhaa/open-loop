#!/usr/bin/env python3
"""
Loan Request Pipeline Examples

This script demonstrates the new /loan/request endpoint that orchestrates
the complete AI agent lending pipeline.

The pipeline includes:
1. Gatekeeper: Agent identity validation
2. Analyst: Credit score calculation (0-100)
3. Decision: Approval decision based on score
4. Treasury: Fund availability check
5. Auditor: Event logging

Run with: python test_loan_request.py

Prerequisites:
1. Start the server: uvicorn app.main:app --reload
2. Install dependencies: pip install -r requirements.txt
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def pretty_print(title: str, data: Dict[str, Any]):
    """Pretty print response data."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")
    print(json.dumps(data, indent=2, default=str))


def test_loan_request(agent_id: str, amount: float):
    """Test a loan request."""
    url = f"{BASE_URL}/loan/request"
    params = {
        "agent_id": agent_id,
        "amount": amount
    }
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API at", BASE_URL)
        print("Make sure the server is running:")
        print("  uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def main():
    """Run loan request tests."""
    
    print("="*70)
    print("  AI Agent Credit System - Loan Request Pipeline Demo")
    print("="*70)
    
    # Test Case 1: Valid agent with good score
    print("\n[TEST 1] Valid Agent - Large Loan Amount")
    print("-" * 70)
    print("Scenario: AGENT-001 (high success rate) requesting $50,000")
    result = test_loan_request("AGENT-001", 50000)
    if result:
        pretty_print("RESPONSE", result)
        print("\nAnalysis:")
        print(f"  ✓ Agent validated: {result.get('agent_id')}")
        print(f"  ✓ Credit score: {result.get('score')}/100 ({result.get('risk_level')} risk)")
        print(f"  ✓ Decision: {'APPROVED' if result.get('approved') else 'REJECTED'}")
        if result.get('approved'):
            print(f"  ✓ Interest rate: {result.get('interest_rate')}%")
            print(f"  ✓ Collateral required: ${result.get('collateral_required'):,.2f}")
    
    # Test Case 2: Valid agent with medium score
    print("\n\n[TEST 2] Valid Agent - Medium Loan Amount")
    print("-" * 70)
    print("Scenario: AGENT-003 (moderate success rate) requesting $20,000")
    result = test_loan_request("AGENT-003", 20000)
    if result:
        pretty_print("RESPONSE", result)
        print("\nAnalysis:")
        print(f"  ✓ Credit score: {result.get('score')}/100 ({result.get('risk_level')} risk)")
        print(f"  ✓ Decision: {'APPROVED' if result.get('approved') else 'REJECTED'}")
        if result.get('approved'):
            print(f"  ✓ Monthly payment: ${result.get('monthly_payment'):,.2f}")
    
    # Test Case 3: Valid agent with small loan
    print("\n\n[TEST 3] Valid Agent - Small Loan Amount")
    print("-" * 70)
    print("Scenario: AGENT-TEST (new agent) requesting $5,000")
    result = test_loan_request("AGENT-TEST", 5000)
    if result:
        pretty_print("RESPONSE", result)
        print("\nAnalysis:")
        print(f"  ✓ Credit score: {result.get('score')}/100 ({result.get('risk_level')} risk)")
        print(f"  ✓ Decision: {'APPROVED' if result.get('approved') else 'REJECTED'}")
    
    # Test Case 4: Invalid agent
    print("\n\n[TEST 4] Invalid Agent")
    print("-" * 70)
    print("Scenario: Non-existent agent trying to request $30,000")
    result = test_loan_request("INVALID-AGENT", 30000)
    if result:
        pretty_print("RESPONSE", result)
        print("\nAnalysis:")
        print(f"  ✗ Agent validation: {'PASSED' if result.get('agent_id') else 'FAILED'}")
        print(f"  ✓ Decision: {'APPROVED' if result.get('approved') else 'REJECTED'}")
    
    # Test Case 5: Very small loan
    print("\n\n[TEST 5] Very Small Loan Request")
    print("-" * 70)
    print("Scenario: AGENT-001 requesting $1,000")
    result = test_loan_request("AGENT-001", 1000)
    if result:
        pretty_print("RESPONSE", result)
        print("\nAnalysis:")
        print(f"  ✓ Credit score: {result.get('score')}/100")
        print(f"  ✓ Collateral: ${result.get('collateral_required'):,.2f}")
    
    # Summary
    print("\n\n" + "="*70)
    print("  PIPELINE SUMMARY")
    print("="*70)
    print("""
The /loan/request endpoint orchestrates the following pipeline:

1. GATEKEEPER (Validation)
   - Checks if agent is registered and active
   - Returns: valid/invalid status

2. ANALYST (Scoring)
   - Calculates credit score (0-100)
   - Based on:
     * Agent's historical success rate
     * Number of past transactions
     * Loan amount requested
   - Returns: score, risk_level, components breakdown

3. DECISION (Approval Logic)
   - Score > 70:  APPROVE (4.5% interest, 10% collateral)
   - Score 50-70: APPROVE (9.5% interest, 25% collateral)
   - Score < 50:  REJECT
   - Returns: approved, interest_rate, collateral_required, monthly_payment

4. TREASURY (Fund Check)
   - Verifies sufficient capital available
   - Checks portfolio utilization
   - Returns: available_funds, funds_available status

5. AUDITOR (Logging)
   - Logs all pipeline events
   - Records decisions with timestamps
   - Returns: audit trail for compliance

FINAL DECISION: Loan approved only if:
  ✓ Agent is valid
  ✓ Credit score passes decision threshold
  ✓ Treasury has sufficient funds
    """)
    print("="*70)


if __name__ == "__main__":
    main()
