#!/usr/bin/env python3
"""
Test script for Identity Layer (KYA) endpoints
Tests all agent management and verification endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# Test wallet addresses
WALLET_1 = "0x1234567890123456789012345678901234567890"
WALLET_2 = "0x0987654321098765432109876543210987654321"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*80}")
    print(f"✓ {title}")
    print(f"{'='*80}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)

def test_create_agent():
    """Test: POST /agent/create"""
    url = f"{BASE_URL}/agent/create"
    params = {
        "wallet_address": WALLET_1,
        "initial_trust_score": 50.0
    }
    print(f"\nTesting: POST /agent/create")
    print(f"Wallet: {WALLET_1}")
    
    response = requests.post(url, params=params)
    print_response("Create Agent", response)
    return response.status_code == 200

def test_get_agent():
    """Test: GET /agent/{wallet}"""
    url = f"{BASE_URL}/agent/{WALLET_1}"
    print(f"\nTesting: GET /agent/{{wallet}}")
    print(f"Wallet: {WALLET_1}")
    
    response = requests.get(url)
    print_response("Get Agent Profile", response)
    return response.status_code == 200

def test_update_agent_loan_approval():
    """Test: POST /agent/update - loan_approval event"""
    url = f"{BASE_URL}/agent/update"
    params = {
        "wallet_address": WALLET_1,
        "event_type": "loan_approval",
        "loan_amount": 50000.0
    }
    print(f"\nTesting: POST /agent/update (loan_approval)")
    print(f"Wallet: {WALLET_1}, Amount: 50000")
    
    response = requests.post(url, params=params)
    print_response("Update Agent - Loan Approval", response)
    return response.status_code == 200

def test_update_agent_repayment_success():
    """Test: POST /agent/update - repayment_success event"""
    url = f"{BASE_URL}/agent/update"
    params = {
        "wallet_address": WALLET_1,
        "event_type": "repayment_success"
    }
    print(f"\nTesting: POST /agent/update (repayment_success)")
    print(f"Wallet: {WALLET_1}")
    
    response = requests.post(url, params=params)
    print_response("Update Agent - Repayment Success", response)
    return response.status_code == 200

def test_verify_agent():
    """Test: GET /agent/verify/{wallet}"""
    url = f"{BASE_URL}/agent/verify/{WALLET_1}"
    print(f"\nTesting: GET /agent/verify/{{wallet}}")
    print(f"Wallet: {WALLET_1}")
    
    response = requests.get(url)
    print_response("Verify Agent Identity", response)
    return response.status_code == 200

def test_get_agent_stats():
    """Test: GET /agent/stats/{wallet}"""
    url = f"{BASE_URL}/agent/stats/{WALLET_1}"
    print(f"\nTesting: GET /agent/stats/{{wallet}}")
    print(f"Wallet: {WALLET_1}")
    
    response = requests.get(url)
    print_response("Get Agent Stats", response)
    return response.status_code == 200

def test_loan_request_with_agent_update():
    """Test: POST /loan/wallet/request - integration with agent update"""
    url = f"{BASE_URL}/loan/wallet/request"
    params = {
        "wallet_address": WALLET_2,
        "amount": 25000.0
    }
    print(f"\nTesting: POST /loan/wallet/request (integration with agent)")
    print(f"Wallet: {WALLET_2}, Amount: 25000")
    
    response = requests.post(url, params=params)
    print_response("Loan Request (Agent Integration)", response)
    return response.status_code == 200

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("IDENTITY LAYER (KYA) TEST SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    tests = [
        ("Create Agent", test_create_agent),
        ("Get Agent Profile", test_get_agent),
        ("Update Agent - Loan Approval", test_update_agent_loan_approval),
        ("Update Agent - Repayment Success", test_update_agent_repayment_success),
        ("Verify Agent Identity", test_verify_agent),
        ("Get Agent Stats", test_get_agent_stats),
        ("Loan Request with Agent Integration", test_loan_request_with_agent_update),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"\n✗ ERROR in {test_name}: {str(e)}")
            results.append((test_name, "ERROR"))
    
    # Summary
    print(f"\n\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    for test_name, status in results:
        status_symbol = "✓" if status == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {status}")
    
    passed = sum(1 for _, s in results if s == "PASS")
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()
