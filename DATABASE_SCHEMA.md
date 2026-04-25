# Database Schema - AI Agent Credit System

## Overview

Complete PostgreSQL schema for the AI Agent Credit System with Supabase. Enables persistent storage of agent profiles, loan records, and audit trail.

---

## Table: `agents`

Stores AI agent profiles identified by Ethereum wallet address.

### Schema

```sql
CREATE TABLE agents (
  id BIGSERIAL PRIMARY KEY,
  wallet_address TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  trust_score FLOAT DEFAULT 50.0,
  total_loans INTEGER DEFAULT 0,
  last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agents_wallet ON agents(wallet_address);
```

### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Unique row identifier (auto-increment) |
| `wallet_address` | TEXT | UNIQUE NOT NULL | Ethereum wallet (0x + 40 hex chars) |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When agent first appeared |
| `trust_score` | FLOAT | DEFAULT 50.0 | Trust metric (0-100) |
| `total_loans` | INTEGER | DEFAULT 0 | Cumulative loan requests |
| `last_updated` | TIMESTAMP | DEFAULT NOW() | Last activity time |

### Indexes

- `idx_agents_wallet` on `wallet_address` - Fast lookup by wallet

### Example Rows

```
id │ wallet_address                           │ created_at          │ trust_score │ total_loans │ last_updated
───┼──────────────────────────────────────────┼─────────────────────┼─────────────┼─────────────┼─────────────
 1 │ 0x742d35cc6634c0532925a3b844bc0f5a3d0e │ 2026-04-25 10:30:45 │ 50.0        │ 1           │ 2026-04-25 11:15:22
 2 │ 0xabcdef1234567890abcdef1234567890abcdef │ 2026-04-25 11:00:00 │ 75.5        │ 3           │ 2026-04-25 11:30:00
```

### Operations

**Create/Get Agent**:
```python
db_service.get_or_create_agent(wallet_address, trust_score)
```

**Update Trust Score**:
```python
db_service.update_agent_trust_score(wallet_address, new_score)
```

**Get Statistics**:
```python
db_service.get_agent_statistics(wallet_address)
# Returns: {
#   "total_loans": 5,
#   "approved_loans": 3,
#   "approval_rate": 0.6,
#   "total_borrowed": 150000.0,
#   "avg_interest_rate": 3.5
# }
```

---

## Table: `loans`

Records of all loan requests with decisions and blockchain transaction references.

### Schema

```sql
CREATE TABLE loans (
  id BIGSERIAL PRIMARY KEY,
  wallet_address TEXT NOT NULL REFERENCES agents(wallet_address),
  amount FLOAT NOT NULL,
  interest_rate FLOAT NOT NULL,
  collateral_required FLOAT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('approved', 'rejected')),
  credit_score FLOAT NOT NULL,
  risk_level TEXT NOT NULL,
  tx_hash TEXT,
  decision_reason TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_loans_wallet ON loans(wallet_address);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_loans_created ON loans(created_at);
```

### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Unique loan ID |
| `wallet_address` | TEXT | NOT NULL, FK agents | Agent's wallet |
| `amount` | FLOAT | NOT NULL | Loan amount requested |
| `interest_rate` | FLOAT | NOT NULL | Annual interest rate % |
| `collateral_required` | FLOAT | NOT NULL | Required collateral $ |
| `status` | TEXT | NOT NULL, CHECK | 'approved' or 'rejected' |
| `credit_score` | FLOAT | NOT NULL | Score at time of request |
| `risk_level` | TEXT | NOT NULL | Risk classification |
| `tx_hash` | TEXT | NULLABLE | Blockchain transaction hash |
| `decision_reason` | TEXT | NULLABLE | Explanation of decision |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Request timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

### Indexes

- `idx_loans_wallet` on `wallet_address` - Fast lookup by agent
- `idx_loans_status` on `status` - Find approved/rejected loans
- `idx_loans_created` on `created_at` - Recent loans queries

### Example Rows

```
id │ wallet_address │ amount  │ interest_rate │ status   │ credit_score │ risk_level │ tx_hash │ created_at
───┼────────────────┼─────────┼───────────────┼──────────┼──────────────┼────────────┼─────────┼─────────────
 1 │ 0x742d35cc...  │ 50000.0 │ 3.5           │ approved │ 78.5         │ low        │ NULL    │ 2026-04-25 10:30:46
 2 │ 0x742d35cc...  │ 100000  │ 0.0           │ rejected │ 42.0         │ very_high  │ NULL    │ 2026-04-25 11:15:22
 3 │ 0xabcdef12...  │ 25000   │ 4.2           │ approved │ 65.0         │ medium     │ 0x1a2b... │ 2026-04-25 11:30:00
```

### Operations

**Create Loan Record**:
```python
await db_service.create_loan_record(
    wallet_address="0x742d35cc...",
    amount=50000.0,
    interest_rate=3.5,
    collateral_required=2500.0,
    status="approved",
    credit_score=78.5,
    risk_level="low",
    tx_hash=None,
    decision_reason="Approved due to strong repayment history"
)
```

**Get Loan by ID**:
```python
await db_service.get_loan(loan_id)
```

**Update Transaction Hash**:
```python
await db_service.update_loan_tx_hash(loan_id, tx_hash)
```

**Get Loan History**:
```python
await db_service.get_agent_loan_history(wallet_address, limit=50)
# Returns: [
#   {
#     "id": 1,
#     "amount": 50000.0,
#     "status": "approved",
#     "created_at": "2026-04-25T10:30:46"
#   },
#   ...
# ]
```

---

## Relationships

```
agents (1) ──── (many) loans
  ↓
  Linked via wallet_address
  Foreign Key: loans.wallet_address → agents.wallet_address
```

When an agent is created:
1. Row added to `agents` table with initial trust_score=50.0
2. Each loan request creates row in `loans` table
3. `total_loans` counter in `agents` increments

When agent is queried:
1. Look up by wallet_address in `agents` table
2. Retrieve trust_score and profile info
3. Query `loans` table to get history

---

## Queries

### Get All Loans for Agent

```sql
SELECT 
  id,
  amount,
  interest_rate,
  status,
  credit_score,
  created_at
FROM loans
WHERE wallet_address = '0x742d35cc6634c0532925a3b844bc0f5a3d0e0e0'
ORDER BY created_at DESC;
```

### Get Approval Statistics

```sql
SELECT 
  COUNT(*) as total_requests,
  SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
  ROUND(100.0 * SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) / COUNT(*), 1) as approval_rate_pct
FROM loans
WHERE wallet_address = '0x742d35cc6634c0532925a3b844bc0f5a3d0e0e0';
```

### Get Average Loan Terms

```sql
SELECT 
  AVG(amount) as avg_amount,
  AVG(interest_rate) as avg_rate,
  AVG(collateral_required) as avg_collateral,
  MAX(created_at) as last_request
FROM loans
WHERE wallet_address = '0x742d35cc6634c0532925a3b844bc0f5a3d0e0e0'
  AND status = 'approved';
```

### Recent Loans (Last 7 Days)

```sql
SELECT 
  id,
  wallet_address,
  amount,
  status,
  credit_score,
  created_at
FROM loans
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

### Approve Rate by Risk Level

```sql
SELECT 
  risk_level,
  COUNT(*) as total,
  SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
  ROUND(100.0 * SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) / COUNT(*), 1) as approval_rate_pct
FROM loans
GROUP BY risk_level
ORDER BY total DESC;
```

### Update Transaction Hash (After Blockchain TX)

```sql
UPDATE loans
SET 
  tx_hash = '0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t',
  updated_at = NOW()
WHERE id = 1;
```

### Bulk Update Status

```sql
UPDATE loans
SET status = 'approved'
WHERE status = 'pending'
  AND created_at < NOW() - INTERVAL '24 hours';
```

---

## Data Flow

### Loan Request Flow

```
1. POST /loan/request (wallet_address, amount)
   ↓
2. Gatekeeper validates wallet
   ↓
3. Analyst calculates credit score
   ↓
4. Decision approves/rejects
   ↓
5. Treasury checks funds
   ↓
6. CREATE loan record in 'loans' table
   ↓
7. Increment total_loans in 'agents' table
   ↓
8. Return response with db_loan_id
```

### Agent Creation Flow

```
1. First time wallet appears
   ↓
2. INSERT into 'agents' table
   - wallet_address (unique)
   - trust_score = 50.0 (default)
   - total_loans = 0
   ↓
3. Agent ID generated (auto-increment)
   ↓
4. Subsequent requests use same agent row
```

---

## Constraints & Validation

### Foreign Key Constraint
```sql
ALTER TABLE loans
ADD CONSTRAINT fk_loans_agent
FOREIGN KEY (wallet_address)
REFERENCES agents(wallet_address)
ON DELETE RESTRICT;
```

Effect: Cannot delete agent if loans exist.

### Check Constraint on `status`
```sql
ALTER TABLE loans
ADD CONSTRAINT check_status
CHECK (status IN ('approved', 'rejected'));
```

Effect: Only valid statuses allowed.

### Unique Constraint on `wallet_address`
```sql
ALTER TABLE agents
ADD CONSTRAINT unique_wallet
UNIQUE (wallet_address);
```

Effect: One agent row per wallet.

---

## Performance Considerations

### Indexes Improve These Queries

**By Wallet (common)**:
```sql
SELECT * FROM agents WHERE wallet_address = '0x...'  -- indexed
SELECT * FROM loans WHERE wallet_address = '0x...'   -- indexed
```

**By Status (common)**:
```sql
SELECT * FROM loans WHERE status = 'approved'  -- indexed
```

**By Date (analytics)**:
```sql
SELECT * FROM loans WHERE created_at > '2026-04-25'  -- indexed
```

### Query Performance

| Query | Without Index | With Index |
|-------|---------------|-----------|
| Find agent by wallet | ~100ms | ~1ms |
| Get 100 loan records | ~50ms | ~5ms |
| Filter by status | ~500ms | ~10ms |

---

## Backup & Recovery

### Enable Automated Backups

Supabase Dashboard → Settings → Database → Backups

- Daily automatic backups (7 day retention)
- Manual backup points on request
- Point-in-time recovery available

### Export Data

```sql
-- Export as CSV
COPY agents TO '/tmp/agents.csv' WITH CSV HEADER;
COPY loans TO '/tmp/loans.csv' WITH CSV HEADER;
```

### Restore

```sql
COPY agents FROM '/tmp/agents.csv' WITH CSV HEADER;
COPY loans FROM '/tmp/loans.csv' WITH CSV HEADER;
```

---

## Row-Level Security (RLS)

For production, add security policies:

```sql
-- Enable RLS
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE loans ENABLE ROW LEVEL SECURITY;

-- Policy: Agents can only view their own records
CREATE POLICY agent_select_own ON agents
  FOR SELECT USING (wallet_address = current_user_wallet());

CREATE POLICY agent_select_own_loans ON loans
  FOR SELECT USING (wallet_address = current_user_wallet());
```

---

## Development vs Production

### Development Setup (This Guide)

- ✅ Public anon key (safe for development)
- ✅ Local backend testing
- ✅ No RLS policies needed
- ✅ Easy data inspection

### Production Setup

- 🔒 Use admin key (secured)
- 🔒 Enable RLS policies
- 🔒 Restrict public key access
- 🔒 Audit logs enabled
- 🔒 Backups configured
- 🔒 Rate limiting configured

---

## API Layer

All database operations abstracted through `SupabaseService`:

**File**: `app/services/db_service.py`

**Methods**:
- `get_or_create_agent()` - Create/retrieve agent
- `create_loan_record()` - Store loan request
- `update_loan_tx_hash()` - Update with blockchain hash
- `get_agent_loan_history()` - Retrieve agent history
- `get_agent_statistics()` - Get approval rate, totals
- `health_check()` - Verify database connection

**Benefits**:
- Single source of truth for database logic
- Easy to test and mock
- Separation of concerns
- Consistent error handling

---

## Troubleshooting

### "Relation does not exist"

**Cause**: Table not created yet

**Fix**:
1. Go to Supabase SQL Editor
2. Run creation scripts from this guide
3. Refresh table list

### "Unique constraint violation"

**Cause**: Trying to create duplicate wallet_address

**Fix**:
1. This is expected behavior (prevents duplicates)
2. Use `get_or_create_agent()` instead of raw INSERT
3. Handles this automatically

### "Foreign key constraint violation"

**Cause**: Referencing non-existent agent

**Fix**:
1. Create agent first (in agents table)
2. Then create loan records
3. `get_or_create_agent()` does this automatically

---

## See Also

- [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md) - Complete setup instructions
- [app/services/db_service.py](app/services/db_service.py) - Database abstraction layer
- [Supabase Docs](https://supabase.com/docs)

