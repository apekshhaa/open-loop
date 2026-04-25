# KYA Identity Layer - Complete Implementation Guide

**Status**: ✅ IMPLEMENTATION COMPLETE (100%)
**Date**: April 25, 2026

---

## 📋 What's Been Built

### Phase 1: Database Schema ✅
- Enhanced `SupabaseService` with all new fields:
  - `successful_repays`, `failed_loans`, `avg_loan`, `activity`, `transactions`, `last_updated`
- New methods for reputation management:
  - `increment_successful_repays()` - Updates score on repayment
  - `increment_failed_loans()` - Updates score on failure  
  - `update_agent_metrics()` - Updates activity level and averages
  - `calculate_reputation_score()` - Formula-based score calculation
  - `get_agent_identity_status()` - Returns Verified/Risky/New Agent status

### Phase 2: Reputation Service ✅
- Created `app/services/reputation_service.py` with:
  - `calculate_reputation_score()` - Implements: score = (successful_repays / total_loans) * 100
  - `classify_agent_status()` - Returns status based on score/history
  - `calculate_activity_level()` - low/medium/high based on transaction count
  - `build_identity_profile()` - Complete profile with trust level and metrics
  - `get_risk_assessment()` - Risk level and factors
  - Configurable thresholds (VERIFIED_THRESHOLD=70, RISKY_THRESHOLD=50)

### Phase 3: Agent Management API ✅
Four new endpoints in `app/routes/agent.py`:

#### 1. **POST /agent/create** - Create new agent
```bash
curl -X POST "http://localhost:8000/agent/create?wallet_address=0x1234...&initial_trust_score=50"
```
Response:
```json
{
  "success": true,
  "message": "Agent created successfully",
  "data": {
    "wallet": "0x1234...7890",
    "score": 50.0,
    "status": "New Agent",
    "history": {"total_loans": 0, "successful_repays": 0, "failed_loans": 0},
    "metrics": {"activity": "low", "transactions": 0, "avg_loan": 0.0}
  }
}
```

#### 2. **GET /agent/{wallet}** - Get agent profile
```bash
curl "http://localhost:8000/agent/0x1234567890123456789012345678901234567890"
```
Response includes: wallet, score, status, history, metrics, trust_level, is_verified

#### 3. **POST /agent/update** - Update agent on events
```bash
# Event: loan_approval
curl -X POST "http://localhost:8000/agent/update?wallet_address=0x1234...&event_type=loan_approval&loan_amount=50000"

# Event: repayment_success
curl -X POST "http://localhost:8000/agent/update?wallet_address=0x1234...&event_type=repayment_success"

# Event: repayment_failure
curl -X POST "http://localhost:8000/agent/update?wallet_address=0x1234...&event_type=repayment_failure"
```

#### 4. **GET /agent/verify/{wallet}** - Verify identity
```bash
curl "http://localhost:8000/agent/verify/0x1234567890123456789012345678901234567890"
```
Response includes: status (Verified/Risky/Established/New Agent), score, risk_level, can_approve_loan

#### 5. **GET /agent/stats/{wallet}** - Get comprehensive stats
```bash
curl "http://localhost:8000/agent/stats/0x1234567890123456789012345678901234567890"
```

### Phase 4: Event Handlers ✅
- Integrated into `/loan/wallet/request` endpoint
- On loan approval:
  - Creates agent if doesn't exist
  - Updates metrics (avg_loan, activity, transactions)
  - Updates trust score based on credit score
  - Gracefully handles DB errors (continues if DB unavailable)

---

## 🗄️ Database Setup (REQUIRED NEXT STEP)

**Status**: Pending table creation in your Supabase instance

### SQL to Create agents Table

Run this in your Supabase SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS agents (
    id BIGSERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trust_score FLOAT DEFAULT 50.0,
    total_loans INT DEFAULT 0,
    successful_repays INT DEFAULT 0,
    failed_loans INT DEFAULT 0,
    avg_loan FLOAT DEFAULT 0.0,
    activity VARCHAR(20) DEFAULT 'low',
    transactions INT DEFAULT 0
);

-- Create index for fast wallet lookups
CREATE INDEX idx_agents_wallet ON agents(wallet_address);
CREATE INDEX idx_agents_activity ON agents(activity);
```

### Verification

After creating the table, verify in Supabase SQL Editor:

```sql
SELECT * FROM agents;
-- Should return empty table with correct schema
```

---

## 🔄 How the KYA System Works

### Agent Lifecycle

```
1. First Loan Request
   ↓
   Create Agent (trust_score=50, activity=low, total_loans=0)
   ↓
   Update Metrics (avg_loan, activity, transactions++)
   
2. Loan Approved
   ↓
   Loan stored in database
   ↓
   Agent metrics updated
   
3. Repayment Success
   ↓
   Increment successful_repays
   ↓
   Recalculate: score = (successful_repays / total_loans) * 100
   ↓
   Status updated based on new score
   
4. Repeat Loan Requests
   ↓
   Agent profile improves with successful repayments
   ↓
   Eventually reach "Verified" status (score >= 70)
```

### Identity Status Classification

```
New Agent          → total_loans == 0
                    (regardless of score)

Verified           → total_loans > 0 AND score >= 70
                    (trusted, low risk)

Established        → total_loans > 0 AND 50 <= score < 70
                    (proven but room for improvement)

Risky              → score < 50
                    (high failure rate)
```

### Activity Levels

```
Low    → 1-4 transactions   (new/inactive agents)
Medium → 5-9 transactions   (moderate activity)
High   → 10+ transactions   (very active agents)
```

### Trust Levels

```
Unknown   → total_loans == 0
Low       → score < 25
Fair      → 25 <= score < 50
Good      → 50 <= score < 75
Excellent → score >= 75
```

---

## 📊 Complete Endpoint Reference

### GET /agent/{wallet_address}
Get agent's identity profile

**Parameters**: wallet_address (query param, 0x format)

**Response**:
```json
{
  "wallet": "0x1234...7890",
  "wallet_full": "0x1234567890...",
  "score": 65.5,
  "status": "Established",
  "history": {
    "total_loans": 10,
    "successful_repays": 6,
    "failed_loans": 2,
    "repayment_rate": 60.0
  },
  "metrics": {
    "activity": "medium",
    "transactions": 8,
    "avg_loan": 45000.0,
    "created_at": "2026-04-25T..."
  },
  "trust_level": "Good",
  "is_verified": false
}
```

### POST /agent/create
Create new agent account

**Parameters**:
- `wallet_address` (required): 0x... format
- `initial_trust_score` (optional): 0-100, default 50.0

**Response**: Agent profile (see GET example)

### POST /agent/update
Update agent on events

**Parameters**:
- `wallet_address` (required): 0x... format
- `event_type` (required): "loan_approval", "repayment_success", or "repayment_failure"
- `loan_amount` (required for loan_approval): positive float

**Event Processing**:
- `loan_approval`: Updates avg_loan, activity, transactions
- `repayment_success`: Increments successful_repays, recalculates score
- `repayment_failure`: Increments failed_loans, recalculates score

### GET /agent/verify/{wallet_address}
Verify agent identity and trust

**Response**:
```json
{
  "success": true,
  "verification": {
    "wallet": "0x1234...7890",
    "status": "Verified",
    "verified": true,
    "score": 75.0,
    "can_approve_loan": true
  },
  "metrics": {
    "total_loans": 10,
    "successful_repays": 7,
    "failed_loans": 1,
    "activity": "high"
  },
  "risk": {
    "risk_level": "low",
    "risk_score": 25,
    "factors": ["Reputation score: 75.0", "Failure rate: 10.0%"]
  },
  "message": "Agent Verified: low risk"
}
```

### GET /agent/stats/{wallet_address}
Get comprehensive statistics

**Response**:
```json
{
  "success": true,
  "statistics": {
    "total_loans_requested": 15,
    "approved_loans": 12,
    "rejected_loans": 3,
    "approval_rate_percent": 80.0,
    "total_amount_requested": 750000.0,
    "average_interest_rate": 4.2,
    "current_trust_score": 70.0,
    "account_age_days": 45
  }
}
```

---

## 🧪 Testing

### Test Wallet Addresses (for manual testing)

```python
WALLET_1 = "0x1234567890123456789012345678901234567890"
WALLET_2 = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
```

### Quick Test Sequence

```bash
# 1. Create agent
curl -X POST "http://localhost:8000/agent/create?wallet_address=0x1234567890123456789012345678901234567890&initial_trust_score=50"

# 2. Get profile
curl "http://localhost:8000/agent/0x1234567890123456789012345678901234567890"

# 3. Simulate loan approval
curl -X POST "http://localhost:8000/agent/update?wallet_address=0x1234567890123456789012345678901234567890&event_type=loan_approval&loan_amount=50000"

# 4. Simulate successful repayment
curl -X POST "http://localhost:8000/agent/update?wallet_address=0x1234567890123456789012345678901234567890&event_type=repayment_success"

# 5. Verify identity (should show improved status)
curl "http://localhost:8000/agent/verify/0x1234567890123456789012345678901234567890"
```

### Run Full Test Suite

```bash
python test_kya_identity.py
```

---

## 📁 Files Created/Modified

### New Files
- ✅ `app/services/reputation_service.py` (200+ lines)
- ✅ `app/routes/agent.py` (300+ lines)
- ✅ `test_kya_identity.py` (test suite)

### Modified Files
- ✅ `app/services/db_service.py` - Added reputation methods
- ✅ `app/routes/wallet_loan.py` - Integrated event handlers
- ✅ `app/routes/__init__.py` - Exported agent router
- ✅ `app/main.py` - Registered agent routes
- ✅ `app/services/__init__.py` - Exported services

---

## 🎯 Implementation Checklist

- ✅ Wallet-based identity system (already existed)
- ✅ Database integration with new fields
- ✅ Reputation scoring service (score = successful_repays / total_loans * 100)
- ✅ Agent status classification (Verified/Risky/Established/New Agent)
- ✅ Activity level calculation (low/medium/high)
- ✅ Trust level indicators (Unknown/Low/Fair/Good/Excellent)
- ✅ Risk assessment with factors
- ✅ POST /agent/create endpoint
- ✅ GET /agent/{wallet} endpoint
- ✅ POST /agent/update endpoint
- ✅ GET /agent/verify/{wallet} endpoint
- ✅ GET /agent/stats/{wallet} endpoint
- ✅ Event handlers (loan_approval, repayment_success, repayment_failure)
- ✅ Integration with loan pipeline
- ✅ Graceful error handling (DB optional)
- ✅ Comprehensive logging
- ✅ Documentation
- ⏳ Database table creation (user action required)

---

## 🚀 Next Steps

### Immediate (To Enable Full Functionality)
1. **Create Supabase Table** (5 minutes)
   - Copy SQL from "Database Setup" section above
   - Run in Supabase SQL Editor
   - Verify with SELECT * FROM agents

2. **Run Test Suite** (2 minutes)
   ```bash
   python test_kya_identity.py
   ```
   - Should show all tests passing
   - Agents persisting to database

### Optional (Enhanced Features)
1. **Add API Key Authentication** - Protect endpoints with JWT
2. **Implement Activity Decay** - Lower activity if no recent transactions
3. **Add Batch Operations** - Get multiple agents in one call
4. **Analytics Dashboard** - Track system metrics over time
5. **Webhook Integrations** - Notify external systems on status changes
6. **Time-based Reputation** - Factor in loan duration and consistency

---

## 📈 Reputation Formula Reference

### Primary Formula
```
reputation_score = (successful_repays / total_loans) * 100
```

### Example Scenarios

| Successful | Total | Score | Status |
|-----------|-------|-------|--------|
| 0 | 0 | 50.0 | New Agent |
| 1 | 1 | 100.0 | Verified |
| 5 | 10 | 50.0 | Established |
| 7 | 10 | 70.0 | Verified |
| 3 | 10 | 30.0 | Risky |
| 9 | 10 | 90.0 | Verified |

---

## 🔐 Security Notes

- Wallet addresses are normalized to lowercase
- Format validation: 0x + 40 hex characters
- All endpoints validate input before processing
- Database errors don't crash the system (graceful fallback)
- Sensitive data (full wallet) included in response for debugging
- Consider adding rate limiting for production
- Add authentication layer before production deployment

---

## ✅ Implementation Complete!

The Identity Layer (KYA) system is now **100% implemented**. All 10 requirements from the original spec are covered:

1. ✅ Wallet-Based Identity
2. ✅ Database Integration  
3. ✅ Agent Initialization
4. ✅ History Tracking
5. ✅ Reputation Scoring
6. ✅ Behavior Metrics
7. ✅ Identity Verification Logic
8. ✅ API Endpoints (5 endpoints)
9. ✅ Output Format
10. ✅ Design Goal (Decentralized Identity)

**To activate**: Create the Supabase `agents` table using the SQL provided above.

