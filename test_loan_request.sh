#!/bin/bash
# Loan Request API - cURL Examples
#
# This script contains cURL examples for testing the /loan/request endpoint
# 
# Prerequisites:
#   1. Start the server: uvicorn app.main:app --reload
#   2. The server will be available at: http://localhost:8000
#
# Usage: bash test_loan_request.sh
# Or copy individual curl commands and run them manually

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "Loan Request API - cURL Examples"
echo "=========================================="
echo ""
echo "Testing POST /loan/request endpoint"
echo ""

# Test 1: Valid agent with good loan amount
echo "TEST 1: Valid Agent - $50,000 Request"
echo "========================================"
curl -X POST "$BASE_URL/loan/request?agent_id=AGENT-001&amount=50000"
echo ""
echo ""

# Test 2: Valid agent with medium amount
echo "TEST 2: Valid Agent - $20,000 Request"
echo "========================================"
curl -X POST "$BASE_URL/loan/request?agent_id=AGENT-003&amount=20000"
echo ""
echo ""

# Test 3: Valid agent with small amount
echo "TEST 3: Valid Agent - $5,000 Request"
echo "========================================"
curl -X POST "$BASE_URL/loan/request?agent_id=AGENT-TEST&amount=5000"
echo ""
echo ""

# Test 4: Invalid agent (should be rejected at gatekeeper)
echo "TEST 4: Invalid Agent"
echo "========================================"
curl -X POST "$BASE_URL/loan/request?agent_id=INVALID-AGENT&amount=30000"
echo ""
echo ""

# Test 5: Agent without amount (should return error)
echo "TEST 5: Missing Amount Parameter"
echo "========================================"
curl -X POST "$BASE_URL/loan/request?agent_id=AGENT-001"
echo ""
echo ""

# Test 6: Invalid amount (too large)
echo "TEST 6: Amount Exceeds Limit"
echo "========================================"
curl -X POST "$BASE_URL/loan/request?agent_id=AGENT-001&amount=50000000"
echo ""
echo ""

# Test 7: Amount of zero (invalid)
echo "TEST 7: Zero Amount"
echo "========================================"
curl -X POST "$BASE_URL/loan/request?agent_id=AGENT-001&amount=0"
echo ""
echo ""

echo ""
echo "=========================================="
echo "Testing Complete"
echo "=========================================="
echo ""
echo "Quick Test with Pretty Print (requires jq):"
echo "curl -X POST 'http://localhost:8000/loan/request?agent_id=AGENT-001&amount=50000' | jq ."
echo ""
