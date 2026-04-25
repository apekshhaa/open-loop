# Loan Request Pipeline - Testing & API Guide

## Overview

The `/loan/request` endpoint is the core orchestration point for the AI Agent Credit System. It implements a complete multi-stage lending pipeline that validates agents, scores creditworthiness, makes approval decisions, checks fund availability, and logs all activities.

## Quick Start

### 1. Start the Server

```bash
cd /hackathon/open-loop
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

### 2. Access Swagger Documentation

Open your browser to:
```
http://localhost:8000/docs
```

This provides interactive API documentation where you can test endpoints directly.

### 3. Make Your First Request

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/loan/request?agent_id=AGENT-001&amount=50000"
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/loan/request",
    params={
        "agent_id": "AGENT-001",
        "amount": 50000
    }
)
print(response.json())
```

**Using JavaScript/Node.js:**
```javascript
fetch('http://localhost:8000/loan/request?agent_id=AGENT-001&amount=50000', {
  method: 'POST'
})
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err))
```

## Pipeline Architecture

### Stage 1: Gatekeeper (Identity Validation)

**Purpose:** Verify that the requesting agent is registered and active

**Agents in System:**
- `AGENT-001` - Status: Active ✓
- `AGENT-002` - Status: Active ✓
- `AGENT-003` - Status: Active ✓
- `AGENT-TEST` - Status: Active ✓

**Behavior:**
- Valid registered agents: Pass through to Analyst
- Unregistered agents: Rejected immediately with score=0, risk_level="very_high"
- Inactive agents: Rejected with appropriate message

**Example Response (Valid Agent):**
```json
{
  "request_id": "LOAN-20240115-001",
  "agent_id": "AGENT-001",
  "approved": true,
  "score": 90,
  "risk_level": "low",
  "pipeline_status": {
    "gatekeeper": "valid"
  }
}
```

### Stage 2: Analyst (Credit Scoring)

**Purpose:** Calculate a 0-100 credit score based on agent's financial history

**Score Calculation:**
The score is based on three weighted components:

1. **Success Rate Component** (0-40 points)
   - Historical success rate of agent transactions
   - Higher success rate = higher points

2. **Transaction Component** (0-30 points)
   - Number of past transactions
   - More transactions = more points (up to 30)

3. **Amount Component** (0-50 points)
   - Loan amount requested vs agent's history
   - Reasonable loan amounts relative to history = higher points

**Risk Level Classification:**
- Score ≥ 80: `low` risk ✓
- Score 60-79: `medium` risk ⚠
- Score 40-59: `high` risk ⚠⚠
- Score < 40: `very_high` risk ✗

**Mock Agent Data:**
```
AGENT-001: 92% success rate, 45 past transactions, $500K borrowed
AGENT-002: 85% success rate, 28 past transactions, $300K borrowed
AGENT-003: 78% success rate, 15 past transactions, $100K borrowed
AGENT-TEST: 50% success rate, 2 past transactions, $10K borrowed
```

**Example Response (Credit Scoring):**
```json
{
  "score": 92,
  "risk_level": "low",
  "success_rate": 0.92,
  "past_transactions": 45,
  "components": {
    "success_component": 36.8,
    "transaction_component": 30.0,
    "amount_component": 25.0
  }
}
```

### Stage 3: Decision (Approval Decision)

**Purpose:** Make loan approval decision based on credit score

**Decision Logic:**

| Score Range | Decision | Interest Rate | Collateral Required |
|-------------|----------|-----------------|---------------------|
| > 70 | APPROVE ✓ | 4.5% | 10% of amount |
| 50-70 | APPROVE ✓ | 9.5% | 25% of amount |
| < 50 | REJECT ✗ | 0% | 0% |

**Payment Calculation:**
- Loan Term: 12 months (fixed)
- Monthly Payment calculated using amortization formula
- Total Interest = (Monthly Payment × 12) - Principal

**Example: $50,000 loan at 4.5% for 12 months:**
- Monthly Payment: $4,282.81
- Total Interest: $1,393.77
- Collateral Required: $5,000.00

**Example Response (Decision):**
```json
{
  "approved": true,
  "interest_rate": 4.5,
  "collateral_required": 5000.00,
  "monthly_payment": 4282.81,
  "total_interest": 1393.77,
  "message": "Loan approved! Rate: 4.5% Annual, Collateral: $5,000.00"
}
```

### Stage 4: Treasury (Fund Availability)

**Purpose:** Verify sufficient capital is available in the lending pool

**Capital Pool Status:**
- Total Available: $1,000,000
- Current Reserved: Variable (tracks approved loans)
- Current Deployed: Variable (tracks disbursed loans)
- Capital Utilization: Percentage of total used

**Fund Check:**
```
Available Funds = Total Available - Reserved
Decision = (Available Funds >= Requested Amount)
```

**Example Response (Treasury):**
```json
{
  "agent_id": "AGENT-001",
  "funds_available": true,
  "available_funds": 950000.00,
  "capital_utilization": 5.0,
  "message": "Sufficient funds available for disbursement"
}
```

### Stage 5: Auditor (Event Logging)

**Purpose:** Create audit trail for compliance and monitoring

**Events Logged:**
1. Identity verification (Gatekeeper)
2. Credit scoring (Analyst)
3. Approval decision (Decision)
4. Fund availability check (Treasury)
5. Pipeline completion (Final status)

Each event includes:
- Timestamp (ISO format)
- Agent name (which service)
- Event type (e.g., "credit_score_calculated")
- Relevant details (scores, amounts, decisions)

## Testing Scenarios

### Scenario 1: High-Score Agent - Standard Request

**Test:** `curl -X POST "http://localhost:8000/loan/request?agent_id=AGENT-001&amount=50000"`

**Expected Results:**
- ✓ Gatekeeper: Valid agent
- ✓ Analyst: High score (85-95 range)
- ✓ Decision: Approved at 4.5% rate
- ✓ Treasury: Funds available
- **Final:** APPROVED with low interest rate

### Scenario 2: Medium-Score Agent - Moderate Request

**Test:** `curl -X POST "http://localhost:8000/loan/request?agent_id=AGENT-003&amount=20000"`

**Expected Results:**
- ✓ Gatekeeper: Valid agent
- ✓ Analyst: Medium score (70-80 range)
- ✓ Decision: Approved at 9.5% rate
- ✓ Treasury: Funds available
- **Final:** APPROVED with standard interest rate

### Scenario 3: New Agent - Small Request

**Test:** `curl -X POST "http://localhost:8000/loan/request?agent_id=AGENT-TEST&amount=5000"`

**Expected Results:**
- ✓ Gatekeeper: Valid agent
- ✓ Analyst: Low score (40-60 range)
- ✓ Decision: May be approved or rejected depending on exact score
- **Final:** APPROVED/REJECTED based on score threshold

### Scenario 4: Invalid Agent - Request Rejected

**Test:** `curl -X POST "http://localhost:8000/loan/request?agent_id=FAKE-AGENT&amount=50000"`

**Expected Results:**
- ✗ Gatekeeper: Agent not found
- Pipeline stops early
- **Final:** REJECTED with message "agent not found"

### Scenario 5: Invalid Input - Error Handling

**Tests:**
```bash
# Missing amount
curl -X POST "http://localhost:8000/loan/request?agent_id=AGENT-001"
# Expected: 400 Bad Request - amount is required

# Amount too large
curl -X POST "http://localhost:8000/loan/request?agent_id=AGENT-001&amount=50000000"
# Expected: 400 Bad Request - amount must be between 1 and 10,000,000

# Negative amount
curl -X POST "http://localhost:8000/loan/request?agent_id=AGENT-001&amount=-5000"
# Expected: 400 Bad Request - amount must be positive

# Missing agent_id
curl -X POST "http://localhost:8000/loan/request?amount=50000"
# Expected: 400 Bad Request - agent_id is required
```

## Response Format

### Success Response (Approved)

```json
{
  "request_id": "LOAN-20240115-001",
  "agent_id": "AGENT-001",
  "amount_requested": 50000.0,
  "score": 92,
  "risk_level": "low",
  "interest_rate": 4.5,
  "collateral_required": 5000.0,
  "approved": true,
  "funds_available": true,
  "monthly_payment": 4282.81,
  "total_interest": 1393.77,
  "message": "Loan approved! Rate: 4.5% Annual, Collateral: $5,000.00",
  "timestamp": "2024-01-15T10:30:45.123456",
  "pipeline_status": {
    "gatekeeper": "valid",
    "analyst": "score_92",
    "decision": "approved",
    "treasury": "available"
  }
}
```

### Success Response (Rejected)

```json
{
  "request_id": "LOAN-20240115-002",
  "agent_id": "AGENT-TEST",
  "amount_requested": 50000.0,
  "score": 45,
  "risk_level": "high",
  "interest_rate": 0.0,
  "collateral_required": 0.0,
  "approved": false,
  "funds_available": true,
  "monthly_payment": 0.0,
  "total_interest": 0.0,
  "message": "Loan request denied - credit score below minimum threshold",
  "timestamp": "2024-01-15T10:35:22.654321",
  "pipeline_status": {
    "gatekeeper": "valid",
    "analyst": "score_45",
    "decision": "rejected",
    "treasury": "available"
  }
}
```

### Error Response (Invalid Input)

```json
{
  "detail": "amount must be between 1 and 10,000,000"
}
```

## Running Test Scripts

### Python Test Suite

```bash
python test_loan_request.py
```

This runs comprehensive tests for:
- High-score agent with large loan
- Medium-score agent with medium loan
- New agent with small loan
- Invalid agent handling
- Edge cases

### Bash/cURL Tests

```bash
bash test_loan_request.sh
```

Or run individual cURL commands:
```bash
# Test high-score agent
curl -X POST "http://localhost:8000/loan/request?agent_id=AGENT-001&amount=50000" | jq .

# Test medium-score agent
curl -X POST "http://localhost:8000/loan/request?agent_id=AGENT-003&amount=20000" | jq .

# Test invalid agent
curl -X POST "http://localhost:8000/loan/request?agent_id=INVALID&amount=50000" | jq .
```

## API Response Fields

| Field | Type | Description |
|-------|------|-------------|
| request_id | string | Unique loan request identifier |
| agent_id | string | The requesting agent's ID |
| amount_requested | float | Original requested loan amount |
| score | float | Agent's credit score (0-100) |
| risk_level | string | Risk classification (low/medium/high/very_high) |
| interest_rate | float | Annual interest rate (%) |
| collateral_required | float | Required collateral amount ($) |
| approved | boolean | Final approval decision |
| funds_available | boolean | Treasury fund availability |
| monthly_payment | float | Calculated monthly payment ($) |
| total_interest | float | Total interest over 12 months ($) |
| message | string | Human-readable decision message |
| timestamp | string | ISO 8601 timestamp of request |
| pipeline_status | object | Status of each pipeline stage |

## Monitoring & Debugging

### View OpenAPI Documentation

```
http://localhost:8000/docs
```

### Check Server Health

```bash
curl http://localhost:8000/health
```

### View Swagger UI

```
http://localhost:8000/swagger
```

### Monitor Logs

The Auditor service logs all pipeline events. Check application logs for:
- "identity_verification_failed" - Agent validation failed
- "credit_score_calculated" - Scoring complete
- "loan_decision_made" - Approval decision made
- "fund_availability_checked" - Treasury checked
- "pipeline_complete" - Full pipeline finished

## Performance Notes

- **Response Time:** < 200ms typical (in-memory operations)
- **Concurrent Requests:** Handles multiple simultaneous requests
- **Scalability:** Ready for database integration to store loans/audits
- **Async Processing:** All pipeline stages are async-ready

## Next Steps

1. **Database Integration:**
   - Replace LOANS_DB dict with PostgreSQL
   - Persist loan applications and audit logs
   - Enable loan status tracking

2. **Advanced Features:**
   - Loan repayment tracking
   - Agent rating updates based on repayment
   - Dynamic interest rate adjustments
   - Collateral valuation

3. **Compliance:**
   - Full audit trail for regulatory requirements
   - Rate limits and usage tracking
   - Fraud detection algorithms

4. **Enhancements:**
   - Real-time credit score updates
   - Machine learning for risk assessment
   - Webhook notifications for loan status changes
   - Portfolio analytics and reporting

