# API Documentation - Loan Request with Database Persistence

Complete API documentation for the core loan request endpoint with Supabase integration.

---

## Endpoint: POST /loan/request

### Overview

Single-endpoint loan request pipeline that:
1. Validates wallet identity
2. Calculates credit score (deterministic, same wallet = same score)
3. Makes approval decision
4. **Checks fund availability**
5. **Stores loan record in Supabase**
6. Returns decision with database reference

### URL

```
POST http://localhost:8000/loan/request
```

### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `wallet_address` | string | ✅ Yes | Ethereum wallet address (0x + 40 hex) | `0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0` |
| `amount` | float | ✅ Yes | Loan amount in USD | `50000` |

### Request Example

```bash
curl -X POST "http://localhost:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=50000"
```

With formatted output:
```bash
curl -s -X POST "http://localhost:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=50000" | python -m json.tool
```

---

## Response

### Success Response (HTTP 200)

```json
{
  "request_id": "REQ-1e2f3a4b-5c6d-7e8f-9g0h-1i2j3k4l5m6n",
  "wallet_address": "0x742d35cc6634c0532925a3b844bc0f5a3d0e0e0",
  "agent_id": "0x742d35cc6634c0532925a3b844bc0f5a3d0e0e0",
  "amount_requested": 50000,
  "score": 78.5,
  "risk_level": "low",
  "confidence": 0.85,
  "decision_reason": "Approved based on strong deterministic wallet profile",
  "interest_rate": 3.5,
  "collateral_required": 2500,
  "approved": true,
  "funds_available": true,
  "monthly_payment": 1458.33,
  "total_interest": 525,
  "message": "Loan approved! Rate: 3.5% Annual, Collateral: $2,500.00",
  "db_loan_id": "123",
  "wallet_profile": {
    "success_rate": 70.0,
    "transaction_count": 0,
    "repayment_history": 70.0,
    "agent_tier": "moderate"
  },
  "agent_profile": {
    "success_rate": 70.0,
    "transaction_count": 0,
    "repayment_history": 70.0,
    "agent_tier": "moderate"
  },
  "timestamp": "2026-04-25T10:30:46.123456",
  "pipeline_status": {
    "gatekeeper": "valid",
    "analyst": "score_78",
    "decision": "approved",
    "treasury": "available",
    "persistence": "saved"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Unique request identifier (system-generated) |
| `wallet_address` | string | Normalized wallet address (lowercase) |
| `agent_id` | string | Same as wallet_address (for backward compatibility) |
| `amount_requested` | float | Loan amount requested in USD |
| `score` | float | Credit score 0-100 |
| `risk_level` | string | Risk classification: `low`, `medium`, `high`, `very_high` |
| `confidence` | float | Confidence in score 0-1 |
| `decision_reason` | string | Explanation of decision |
| `interest_rate` | float | Annual interest rate % (0 if rejected) |
| `collateral_required` | float | Collateral amount $ (0 if rejected) |
| `approved` | boolean | Loan approved by decision service |
| `funds_available` | boolean | Treasury has sufficient funds |
| `monthly_payment` | float | Monthly payment amount if approved |
| `total_interest` | float | Total interest over loan term |
| `message` | string | Human-readable decision message |
| **`db_loan_id`** | string/null | **Database ID for this loan** ✅ NEW |
| `wallet_profile` | object | Agent profile metrics |
| `timestamp` | string | ISO 8601 timestamp |
| `pipeline_status` | object | Status of each pipeline stage |

### Database Persistence Field

```json
"db_loan_id": "123"
```

**Meaning**: Loan record successfully stored in Supabase

**Usage**: Use this ID to:
- Query loan history
- Update transaction hash after MetaMask execution
- Track approval status
- Link to blockchain transaction

---

## Status Codes

| Code | Scenario | Example |
|------|----------|---------|
| **200** | ✅ Success - Loan processed (approved or rejected) | See above |
| **400** | ❌ Bad Request - Invalid parameters | Wallet format, amount range |
| **500** | ❌ Server Error - Unexpected error | Database connection failure |

---

## Error Responses

### Missing Wallet (400)

```bash
curl -X POST "http://localhost:8000/loan/request?amount=50000"
```

Response:
```json
{
  "detail": "Wallet not connected. Please connect your wallet to request a loan."
}
```

### Invalid Wallet Format (400)

```bash
curl -X POST "http://localhost:8000/loan/request?wallet_address=invalid&amount=50000"
```

Response:
```json
{
  "detail": "Invalid wallet address format. Must be 0x... with 40 hex characters (e.g., 0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0)"
}
```

### Invalid Amount (400)

```bash
curl -X POST "http://localhost:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=-100"
```

Response:
```json
{
  "detail": "amount must be between 1 and 10,000,000"
}
```

### Database Error (500)

If Supabase is unavailable, request still processes but loan is not persisted:

```json
{
  "detail": "LOAN_REQUEST_ERROR: [Database connection error details]"
}
```

Response will still include decision, but `"db_loan_id": null`

---

## Approval Rules

### Credit Score Calculation

Score = (Success Rate × 0.4) + (Transaction Count × 0.3) + (Amount Component × 0.3)

Where:
- **Success Rate Component** (0-40 pts): From wallet's deterministic profile
- **Transaction Component** (0-30 pts): Based on historical volume
- **Amount Component** (0-50 pts): Relative to wallet history

### Decision Logic

| Score | Decision | Interest Rate | Collateral |
|-------|----------|---------------|-----------|
| 70+ | ✅ APPROVED | 3.5% | 10% |
| 50-69 | ✅ APPROVED | 7.5% | 25% |
| <50 | ❌ REJECTED | 0% | 0% |

### Treasury Check

Loan approval requires:
- Decision service: Approve ✅
- Treasury: Funds available ✅
- Final: Only if BOTH true

If treasury lacks funds: `"approved": true, "funds_available": false` → Final reject

---

## Deterministic Scoring (Key Feature)

### Same Wallet = Same Score

The same wallet always receives the same score because scoring is deterministic:

```
wallet_address → SHA256 hash → Deterministic profile
(success_rate=70%, transaction_count=0, repayment_history=70%)
→ Score = 78.5
```

### Test: Multiple Requests, Same Wallet

```bash
# First request
curl -s -X POST "http://localhost:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=50000" | jq '.score'
# Output: 78.5

# Second request (same wallet)
curl -s -X POST "http://localhost:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=25000" | jq '.score'
# Output: 78.5 (SAME!)

# Different wallet
curl -s -X POST "http://localhost:8000/loan/request?wallet_address=0x1234567890ABCDEF1234567890ABCDEF12345678&amount=50000" | jq '.score'
# Output: 45.2 (DIFFERENT)
```

---

## Database Integration

### What Gets Stored

**Supabase `agents` Table:**
```sql
{
  wallet_address: '0x742d35cc...',
  created_at: '2026-04-25 10:30:45',
  trust_score: 50.0,
  total_loans: 1
}
```

**Supabase `loans` Table:**
```sql
{
  id: '123',
  wallet_address: '0x742d35cc...',
  amount: 50000.0,
  interest_rate: 3.5,
  collateral_required: 2500.0,
  status: 'approved',
  credit_score: 78.5,
  risk_level: 'low',
  tx_hash: NULL,  // Will update after MetaMask
  decision_reason: '...',
  created_at: '2026-04-25 10:30:46'
}
```

### Verify in Supabase Dashboard

1. Go to https://app.supabase.com
2. Select your project
3. Click "Table Editor" (left sidebar)
4. Click "agents" table → See wallet_address, trust_score, total_loans
5. Click "loans" table → See all loan records with decisions

---

## Testing Examples

### Test 1: Approve Wallet (High Score)

```bash
curl -X POST "http://localhost:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=50000"
```

Expected:
- `"approved": true`
- `"interest_rate": 3.5`
- `"collateral_required": 2500`

### Test 2: Request Multiple Times (Same Wallet)

```bash
# First request
curl -X POST "http://localhost:8000/loan/request?wallet_address=0xABCDEF1234567890ABCDEF1234567890ABCDEF12&amount=25000"

# Second request (same wallet)
curl -X POST "http://localhost:8000/loan/request?wallet_address=0xABCDEF1234567890ABCDEF1234567890ABCDEF12&amount=100000"

# Check in Supabase: Both loans stored, total_loans = 2
```

### Test 3: Verify Database Persistence

```bash
# After loan request:
# 1. Check database has agent record
SELECT * FROM agents WHERE wallet_address = '0x742d35cc...';

# 2. Check database has loan record
SELECT * FROM loans WHERE wallet_address = '0x742d35cc...' ORDER BY created_at DESC;

# 3. Verify loan record fields
SELECT id, amount, status, interest_rate, created_at FROM loans WHERE id = 123;
```

### Test 4: Test Database Fallback

If database is down:
```bash
curl -X POST "http://localhost:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=50000"

# Response: Still returns valid loan decision
# But: "db_loan_id": null and "persistence": "pending" in pipeline_status
# Check logs: "[DB] Error in create_loan_record: ..."
```

---

## Rate Limits

Current: No rate limiting (demo/development mode)

Production recommendations:
- 100 requests per minute per wallet
- 1000 requests per minute per IP
- Implement with `slowapi` package

---

## Wallet Address Format

### Valid Formats

All these are equivalent:
```
0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0  ✅ Standard
0x742d35cc6634c0532925a3b844bc0f5a3d0e0e0  ✅ Lowercase
0x742D35CC6634C0532925A3B844BC0F5A3D0E0E0  ✅ Uppercase
```

### Invalid Formats

```
742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0   ❌ Missing 0x
0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0  ❌ Too short (39 hex)
0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E00 ❌ Too long (41 hex)
0xGG2d35Cc6634C0532925a3b844Bc0f5a3d0E0E0  ❌ Invalid hex chars
```

---

## Loan Amount Limits

Valid range: **1 to 10,000,000 USD**

```bash
curl -X POST "http://localhost:8000/loan/request?wallet_address=0x...&amount=0"
# ❌ Error: amount must be between 1 and 10,000,000

curl -X POST "http://localhost:8000/loan/request?wallet_address=0x...&amount=0.01"
# ✅ Success: $0.01 loan

curl -X POST "http://localhost:8000/loan/request?wallet_address=0x...&amount=10000000"
# ✅ Success: $10,000,000 loan

curl -X POST "http://localhost:8000/loan/request?wallet_address=0x...&amount=10000001"
# ❌ Error: exceeds maximum
```

---

## Integration with Frontend

### React Example

```javascript
// components/LoanRequest.jsx

async function requestLoan(walletAddress, amount) {
  const response = await fetch(
    `http://localhost:8000/loan/request?wallet_address=${walletAddress}&amount=${amount}`,
    { method: 'POST' }
  );
  
  const decision = await response.json();
  
  // Access database ID
  console.log('DB Loan ID:', decision.db_loan_id);
  
  return {
    approved: decision.approved,
    score: decision.score,
    rate: decision.interest_rate,
    collateral: decision.collateral_required,
    dbLoanId: decision.db_loan_id
  };
}

// After user confirms MetaMask transaction:
async function updateTransactionHash(dbLoanId, txHash) {
  // This endpoint would update the tx_hash in the loans table
  // (TODO: Create this endpoint)
}
```

---

## Troubleshooting

### Error: "Invalid wallet address"
- Ensure wallet is valid Ethereum address
- Must start with `0x`
- Must have exactly 40 hex characters after `0x`
- Try copying from MetaMask → Account Details

### Error: "amount must be between 1 and 10,000,000"
- Check amount is positive number
- Check amount is not too large
- Use numbers, not currency strings (e.g., `50000`, not `"$50,000"`)

### Response has "db_loan_id": null
- Supabase connection failed (check .env SUPABASE_URL)
- Check logs: `[DB] Error in create_loan_record: ...`
- Loan decision still valid, just not persisted
- Restart server after fixing environment variables

### Same wallet gets different scores
- Scores should be deterministic (always same for same wallet)
- If different, check for deterministic scoring implementation
- Verify no randomness in `AnalystService.calculate_agent_credit_score()`

---

## See Also

- [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md) - Full Supabase setup
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Complete schema reference
- [README.md](README.md) - Project overview
- `app/routes/loan.py` - Source code for this endpoint
- `app/services/db_service.py` - Database layer

