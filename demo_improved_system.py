#!/usr/bin/env python3
"""
Improved AI Agent Credit System - Live Demo

This script demonstrates the improved backend logic with:
- Automatic agent creation for unknown agent_ids
- Dynamic credit scoring based on agent profiles
- Realistic decision-making with varying outcomes
- Detailed explanations for all decisions

Run with: python demo_improved_system.py
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime

BASE_URL = "http://localhost:8000"


def format_currency(value: float) -> str:
    """Format number as currency."""
    return f"${value:,.2f}"


def print_response(title: str, response: Dict[str, Any]):
    """Pretty print response with formatting."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")
    
    # Extract key info for display
    print(f"Agent ID:              {response.get('agent_id', 'N/A')}")
    print(f"Request Amount:        {format_currency(response.get('amount_requested', 0))}")
    print(f"Credit Score:          {response.get('score', 0)}/100 ({response.get('risk_level', 'N/A')} risk)")
    print()
    
    print(f"DECISION:              {'✓ APPROVED' if response.get('approved') else '✗ REJECTED'}")
    print(f"Status Message:        {response.get('message', 'N/A')}")
    print()
    
    if response.get('approved'):
        print(f"Interest Rate:         {response.get('interest_rate', 0)}% annual")
        print(f"Collateral Required:   {format_currency(response.get('collateral_required', 0))}")
        print(f"Monthly Payment:       {format_currency(response.get('monthly_payment', 0))}")
        print(f"Total Interest (12m):  {format_currency(response.get('total_interest', 0))}")
    
    print(f"\nFunds Available:       {'✓ Yes' if response.get('funds_available') else '✗ No'}")
    print(f"Timestamp:             {response.get('timestamp', 'N/A')}")
    
    # Show pipeline status
    print(f"\nPipeline Status:")
    pipeline = response.get('pipeline_status', {})
    for stage, status in pipeline.items():
        print(f"  • {stage.title()}: {status}")


def test_agent_request(agent_id: str, amount: float, description: str = ""):
    """Make a loan request and display results."""
    print(f"\n{'#'*80}")
    print(f"TEST: {description if description else f'{agent_id} - ${amount:,}'}")
    print(f"{'#'*80}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/loan/request",
            params={
                "agent_id": agent_id,
                "amount": amount
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_response(f"Loan Request Response", data)
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API at", BASE_URL)
        print("Make sure the server is running: uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def main():
    """Run comprehensive demo of improved system."""
    
    print("\n" + "="*80)
    print("  AI AGENT CREDIT SYSTEM - IMPROVED BACKEND DEMO")
    print("="*80)
    print("""
This demo showcases the realistic and dynamic improvements:

✓ Auto-creation of agent profiles for unknown agents
✓ Dynamic credit scoring (0-100) based on agent history  
✓ Realistic decision-making with graduated approval rates
✓ Varying collateral requirements based on risk
✓ Meaningful variation between different agents
    """)
    
    print("\n" + "="*80)
    print("  SECTION 1: PRE-REGISTERED HIGH-QUALITY AGENTS")
    print("="*80)
    print("These agents have established history and get favorable terms\n")
    
    # Test 1: Established agent with good history
    test_agent_request(
        "AGENT-001",
        50000,
        "Established Agent (92% success) - Standard Loan"
    )
    
    # Test 2: Another established agent
    test_agent_request(
        "AGENT-002",
        30000,
        "Established Agent (85% success) - Medium Loan"
    )
    
    # Test 3: Marginal established agent
    test_agent_request(
        "AGENT-003",
        20000,
        "Established Agent (78% success) - Conservative Loan"
    )
    
    print("\n" + "="*80)
    print("  SECTION 2: AUTOMATIC AGENT CREATION (NEW AGENTS)")
    print("="*80)
    print("Unknown agents are automatically registered with random profiles\n")
    
    # Test 4: Brand new agent (will be auto-created)
    test_agent_request(
        "NEW-STARTUP-001",
        25000,
        "Brand New Agent - First Loan Request"
    )
    
    # Test 5: Another new agent (different profile)
    test_agent_request(
        "BETA-AGENT-X",
        40000,
        "Another New Agent - Larger Loan"
    )
    
    # Test 6: Yet another new agent (should have different characteristics)
    test_agent_request(
        "GAMMA-LABS",
        15000,
        "Third New Agent - Small Loan"
    )
    
    print("\n" + "="*80)
    print("  SECTION 3: DIVERSE LOAN AMOUNTS")
    print("="*80)
    print("Testing how loan amount affects scoring and decisions\n")
    
    # Test 7: Very small loan
    test_agent_request(
        "AGENT-001",
        1000,
        "AGENT-001 - Very Small Loan (High Score)"
    )
    
    # Test 8: Large loan (same agent)
    test_agent_request(
        "AGENT-001",
        500000,
        "AGENT-001 - Large Loan (Score impact)"
    )
    
    # Test 9: Medium loan
    test_agent_request(
        "AGENT-003",
        50000,
        "AGENT-003 - Medium Loan"
    )
    
    print("\n" + "="*80)
    print("  SECTION 4: REALISTIC VARIETY")
    print("="*80)
    print("Demonstrating realistic variation in scores and decisions\n")
    
    # Test 10-12: Multiple requests to show variation
    for i in range(3):
        test_agent_request(
            "VARIABLE-AGENT",
            35000,
            f"Variable Agent - Run {i+1} (Shows slight score variation)"
        )
    
    print("\n" + "="*80)
    print("  DEMO COMPLETE")
    print("="*80)
    print("""
Key Improvements Demonstrated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. AUTO-CREATION OF AGENTS
   • Unknown agent_ids are automatically registered
   • Random profiles assigned (success_rate, transaction_count, repayment_history)
   • Always returns valid=True - pipeline continues for all agents
   
2. DYNAMIC CREDIT SCORING
   • Scores vary between 0-100 based on:
     - Success rate (40% weight)
     - Transaction history (35% weight)
     - Repayment history (25% weight)
     - Loan amount (slight reduction for very large loans)
   • Includes ±2 point randomness for realistic variation
   • Clear categorization: Low/Medium/High/Very High risk

3. NUANCED DECISION-MAKING
   • Multiple approval tiers (5 tiers instead of 3):
     - Score >= 80: 3.5% rate, 5% collateral (Excellent)
     - Score > 70: 4.5% rate, 10% collateral (Low Risk)
     - Score >= 60: 7.5% rate, 20% collateral (Medium Risk)
     - Score >= 50: 9.5% rate, 25% collateral (Higher Risk)
     - Score < 50: Rejection
   
4. REALISTIC VARIATION
   • Same agent with different amounts produces different scores
   • New agents get random profiles, leading to varied outcomes
   • Interest rates span 3.5% to 9.5% (realistic range)
   • Collateral ranges from 5% to 25% based on risk
   
5. CLEAR DECISION MESSAGING
   • Detailed, context-aware messages
   • Shows actual score, risk category, and approval reason
   • Professional tone suitable for demo

For Testing: Each request produces realistic, believable output suitable
for a live demo - NOT always approving, NOT always rejecting, but varying
based on actual computed scores.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)


if __name__ == "__main__":
    main()
