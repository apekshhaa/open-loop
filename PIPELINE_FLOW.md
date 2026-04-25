# AI Agent Credit System - Pipeline Flow Visualization

## 🔄 Loan Processing Pipeline

### Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LOAN APPLICATION                                 │
│                                                                          │
│  POST /loan/apply                                                        │
│  {                                                                       │
│    "borrower_id": "BORROWER-001",                                       │
│    "amount": 50000,                                                      │
│    "duration_months": 36,                                                │
│    "purpose": "Business expansion"                                       │
│  }                                                                       │
└──────────────────────────┬──────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    STAGE 1: GATEKEEPER                                   │
│                   (Identity Verification)                                │
│                                                                          │
│  POST /loan/{loan_id}/verify                                             │
│                                                                          │
│  Actions:                                                               │
│  ├─ Verify borrower identity with KYC data                             │
│  ├─ Check against sanctions lists                                       │
│  ├─ Calculate fraud risk score                                          │
│  └─ Return verification status                                          │
│                                                                          │
│  Output:                                                                │
│  {                                                                       │
│    "agent_name": "gatekeeper",                                          │
│    "status": "completed",                                               │
│    "result": {                                                          │
│      "verified": true,                                                  │
│      "fraud_score": 0.15                                                │
│    }                                                                    │
│  }                                                                       │
└──────────────────────────┬──────────────────────────────────────────────┘
                           ↓
                    [VERIFIED? ✓]
                           ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    STAGE 2: ANALYST                                      │
│                    (Credit Scoring)                                      │
│                                                                          │
│  POST /loan/{loan_id}/score                                              │
│                                                                          │
│  Actions:                                                               │
│  ├─ Analyze financial data                                              │
│  ├─ Calculate credit score (0-850 FICO scale)                          │
│  ├─ Determine risk level (low/medium/high)                             │
│  ├─ Identify key credit factors                                        │
│  └─ Generate analyst recommendation                                     │
│                                                                          │
│  Output:                                                                │
│  {                                                                       │
│    "agent_name": "analyst",                                             │
│    "status": "completed",                                               │
│    "result": {                                                          │
│      "credit_score": 750,                                               │
│      "risk_level": "low",                                               │
│      "recommendation": "Highly recommended for approval"                │
│    }                                                                    │
│  }                                                                       │
└──────────────────────────┬──────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    STAGE 3: DECISION                                     │
│                  (Loan Decision Making)                                  │
│                                                                          │
│  POST /loan/{loan_id}/decide                                             │
│                                                                          │
│  Evaluates:                                                             │
│  ├─ Credit score (minimum 580)                                          │
│  ├─ Gatekeeper verification status                                      │
│  ├─ Debt-to-income ratio (max 43%)                                      │
│  └─ Prior stage results                                                 │
│                                                                          │
│  Decision Logic:                                                        │
│  IF credit_score >= 750 THEN interest_rate = 4.5%                      │
│  IF credit_score >= 670 THEN interest_rate = 6.5%                      │
│  IF credit_score >= 580 THEN interest_rate = 9.5%                      │
│  ELSE reject                                                            │
│                                                                          │
│  Output:                                                                │
│  {                                                                       │
│    "agent_name": "decision",                                            │
│    "status": "completed",                                               │
│    "result": {                                                          │
│      "decision": "approved",                                            │
│      "approved_amount": 50000,                                          │
│      "interest_rate": 0.045,                                            │
│      "conditions": ["Standard loan agreement terms apply"]              │
│    }                                                                    │
│  }                                                                       │
└──────────────────────────┬──────────────────────────────────────────────┘
                           ↓
                    [APPROVED? ✓]
                           ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    STAGE 4: TREASURY                                     │
│                  (Fund Management & Verification)                        │
│                                                                          │
│  [Internally Called - No Direct Endpoint]                               │
│                                                                          │
│  Actions:                                                               │
│  ├─ Check capital pool availability                                     │
│  ├─ Verify single loan limits (max 5% of capital)                      │
│  ├─ Check portfolio diversification requirements                        │
│  ├─ Reserve funds for approved loan                                     │
│  └─ Return fund status                                                  │
│                                                                          │
│  Capital Pool Example:                                                  │
│  {                                                                       │
│    "total_available": 1000000,                                          │
│    "reserved": 100000,                                                  │
│    "deployed": 150000,                                                  │
│    "available": 750000,                                                 │
│    "utilization": 25%                                                   │
│  }                                                                       │
└──────────────────────────┬──────────────────────────────────────────────┘
                           ↓
                    [FUNDS OK? ✓]
                           ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    STAGE 5: SETTLER                                      │
│                  (Disbursement & Settlement)                             │
│                                                                          │
│  POST /loan/{loan_id}/disburse                                           │
│                                                                          │
│  Actions:                                                               │
│  ├─ Disburse funds to borrower                                          │
│  ├─ Execute blockchain transaction (if applicable)                      │
│  ├─ Generate transaction receipts                                       │
│  ├─ Confirm disbursement                                                │
│  └─ Update loan status to FUNDED                                        │
│                                                                          │
│  Disbursement Methods:                                                  │
│  ├─ Bank transfer (ACH/Wire) - 1-3 business days                       │
│  ├─ Cryptocurrency (testnet) - blockchain confirmation                  │
│  └─ Direct deposit - immediate                                          │
│                                                                          │
│  Output:                                                                │
│  {                                                                       │
│    "agent_name": "settler",                                             │
│    "status": "completed",                                               │
│    "result": {                                                          │
│      "disbursement_successful": true,                                   │
│      "transaction_id": "TXN-abc123def456",                              │
│      "amount": 50000,                                                   │
│      "confirmation_number": "DISBURSE-abc123de",                        │
│      "estimated_arrival": "1-3 business days"                           │
│    }                                                                    │
│  }                                                                       │
└──────────────────────────┬──────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    STAGE 6: AUDITOR                                      │
│                  (Logging & Compliance)                                  │
│                                                                          │
│  [Continuously Running - All Events Logged]                             │
│                                                                          │
│  GET /loan/{loan_id}/audit-trail                                         │
│                                                                          │
│  Actions:                                                               │
│  ├─ Log every pipeline event                                            │
│  ├─ Record decision points with reasoning                               │
│  ├─ Track timestamps and actors                                         │
│  ├─ Generate compliance reports                                         │
│  └─ Maintain complete audit trail                                       │
│                                                                          │
│  Audit Trail Example:                                                   │
│  [                                                                       │
│    {                                                                    │
│      "log_id": "LOG-001",                                               │
│      "agent": "gatekeeper",                                             │
│      "event": "verified",                                               │
│      "timestamp": "2024-01-15T10:30:00Z"                                │
│    },                                                                   │
│    {                                                                    │
│      "log_id": "LOG-002",                                               │
│      "agent": "analyst",                                                │
│      "event": "scored",                                                 │
│      "score": 750,                                                      │
│      "timestamp": "2024-01-15T10:31:00Z"                                │
│    },                                                                   │
│    ...                                                                  │
│  ]                                                                       │
│                                                                          │
│  Compliance Report:                                                     │
│  {                                                                       │
│    "total_events": 15,                                                  │
│    "events_by_agent": {                                                 │
│      "gatekeeper": 2,                                                   │
│      "analyst": 2,                                                      │
│      "decision": 2,                                                     │
│      "settler": 3,                                                      │
│      "auditor": 6                                                       │
│    }                                                                    │
│  }                                                                       │
└──────────────────────────┬──────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       LOAN COMPLETED                                     │
│                                                                          │
│  Final Status:                                                          │
│  {                                                                       │
│    "loan_id": "LOAN-abc123def456",                                      │
│    "status": "funded",                                                  │
│    "borrower_id": "BORROWER-001",                                       │
│    "amount_requested": 50000,                                           │
│    "approved_amount": 50000,                                            │
│    "interest_rate": 0.045,                                              │
│    "monthly_payment": 1445.35,                                          │
│    "total_interest": 2032.60,                                           │
│    "disbursement_date": "2024-01-15T11:00:00Z",                        │
│    "completion_percentage": 100%                                        │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📊 Decision Criteria Matrix

```
┌────────────────────────────────────────────────────────────────────┐
│              LOAN APPROVAL DECISION MATRIX                          │
├──────────────────┬──────────────────┬─────────────┬────────────────┤
│ Credit Score     │ Debt-to-Income   │ Decision    │ Interest Rate  │
├──────────────────┼──────────────────┼─────────────┼────────────────┤
│ 750 - 850        │ ≤ 43%            │ APPROVED    │ 4.5%           │
│ 670 - 749        │ ≤ 43%            │ APPROVED    │ 6.5%           │
│ 620 - 669        │ ≤ 40%            │ APPROVED    │ 9.5% (80% amt) │
│ 580 - 619        │ ≤ 35%            │ APPROVED    │ 12.5% (80% amt)│
│ < 580            │ Any              │ REJECTED    │ N/A            │
│ Any              │ > 43%            │ REJECTED    │ N/A            │
│ Not Verified     │ Any              │ REJECTED    │ N/A            │
└──────────────────┴──────────────────┴─────────────┴────────────────┘
```

## 🔀 Alternative Flow: Rejection

```
Application (PENDING)
       ↓
   Gatekeeper
       ↓
    [Failed?] ──→ REJECTED ──→ Status: REJECTED
       ↓ (Passed)
   Analyst
       ↓
   Score < 580? ──→ REJECTED ──→ Status: REJECTED
       ↓ (Score OK)
   Decision
       ↓
   Approved? ──→ NO ──→ REJECTED ──→ Status: REJECTED
       ↓ (YES)
   Disburse
       ↓
   FUNDED
```

## 🔌 Data Transformations

### At Each Stage

```
STAGE 1: GATEKEEPER
Input:  { borrower_id, kyc_data }
Output: { verified: boolean, fraud_score: float }
        Status: PENDING → VERIFICATION

STAGE 2: ANALYST
Input:  { borrower_id, financial_data }
Output: { credit_score: 0-850, risk_level: str }
        Status: VERIFICATION → SCORING

STAGE 3: DECISION
Input:  { credit_score, verified, dti, amount }
Output: { decision: str, approved_amount: float, rate: float }
        Status: SCORING → DECISION_PENDING/APPROVED/REJECTED

STAGE 4: TREASURY
Input:  { approved_amount }
Output: { funds_available: boolean }
        Status: (checked internally)

STAGE 5: SETTLER
Input:  { loan_id, amount, borrower_id }
Output: { transaction_id, confirmation_number }
        Status: APPROVED → FUNDED

STAGE 6: AUDITOR
Input:  { event_data }
Output: { log_id, timestamp }
        Status: (continuously logged)
```

## 🧮 Payment Calculation Example

```
Loan Details:
├─ Principal: $50,000
├─ Annual Rate: 4.5% (0.045)
├─ Duration: 36 months
└─ Monthly Rate: 0.045 ÷ 12 = 0.00375

Calculation:
M = P × [r(1+r)^n] / [(1+r)^n - 1]
M = 50000 × [0.00375(1.00375)^36] / [(1.00375)^36 - 1]
M = 50000 × [0.00375 × 1.1423] / [0.1423]
M = $1,445.35 per month

Results:
├─ Monthly Payment: $1,445.35
├─ Total Payments: $52,032.60 (36 × $1,445.35)
├─ Total Interest: $2,032.60
└─ Total Cost: $52,032.60
```

## 📈 Pipeline Status Tracking

```
GET /loan/{loan_id}/pipeline

Response:
{
  "loan_id": "LOAN-abc123def456",
  "stages": {
    "gatekeeper": {
      "agent_name": "gatekeeper",
      "status": "completed",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    "analyst": {
      "agent_name": "analyst",
      "status": "completed",
      "timestamp": "2024-01-15T10:31:00Z"
    },
    "decision": {
      "agent_name": "decision",
      "status": "completed",
      "timestamp": "2024-01-15T10:32:00Z"
    },
    "treasury": null,
    "settler": null,
    "auditor": {
      "agent_name": "auditor",
      "status": "completed",
      "timestamp": "2024-01-15T10:33:00Z"
    }
  },
  "overall_status": "pending",
  "completion_percentage": 50.0
}
```

## ⏱️ Typical Processing Timeline

```
Time    Event
────    ─────────────────────────────────
T+0     Loan application submitted
T+5s    Identity verification (Gatekeeper)
T+10s   Credit scoring (Analyst)
T+15s   Decision making (Decision)
T+20s   Fund verification (Treasury)
T+25s   Manual approval by administrator
T+30s   Fund disbursement initiated (Settler)
T+35s   Audit logging complete (Auditor)
T+40s   Loan funding complete

Total: ~40 seconds for complete pipeline
```

---

This visualization shows how the six independent agents work together to process a loan from application through disbursement, with complete audit trail logging throughout the process.
