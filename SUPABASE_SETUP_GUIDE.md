# 🗄️ Supabase Integration - Complete Setup Guide

## Overview

Your FastAPI AI Agent Credit System now integrates with **Supabase** for persistent data storage. This enables:

✅ Agent profile persistence across requests  
✅ Complete loan history tracking  
✅ Audit trail of all transactions  
✅ Approval rate analytics  
✅ Real fintech-like state management  

---

## Step 1: Create Supabase Project

### 1.1 Sign Up / Log In
1. Visit [supabase.com](https://supabase.com)
2. Click "Start your project" or log in
3. Create a new organization (if needed)

### 1.2 Create New Project
1. Click "New Project"
2. Fill in:
   - **Project Name**: `ai-credit-system` (or your choice)
   - **Database Password**: Strong password (save this!)
   - **Region**: Choose closest to your location
3. Click "Create new project"
4. Wait for initialization (~2 minutes)

### 1.3 Get Your Credentials
After project creation:
1. Go to **Settings** → **API**
2. Copy these values:
   ```
   SUPABASE_URL = https://[project-id].supabase.co
   SUPABASE_ANON_KEY = (eyJ0eXAi...) [long string]
   ```
3. Save these in `.env` file (see Step 2)

---

## Step 2: Configure Environment Variables

### 2.1 Update .env File

Create or update `d:\hackathon\open-loop\.env`:

```env
# Database Configuration - Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Other existing variables...
ENVIRONMENT=development
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

**Where to find these values:**
- SUPABASE_URL: Supabase Dashboard → Settings → API → Project URL
- SUPABASE_ANON_KEY: Supabase Dashboard → Settings → API → anon/public

### 2.2 Verify Configuration
```bash
# Test that .env is loaded correctly
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('SUPABASE_URL'))"
```

Should output your Supabase URL.

---

## Step 3: Create Database Tables

### 3.1 Access Supabase SQL Editor

1. Go to Supabase Dashboard
2. Click **SQL Editor** (left sidebar)
3. Click **New Query**

### 3.2 Create `agents` Table

Copy and paste this SQL:

```sql
-- Create agents table
CREATE TABLE agents (
  id BIGSERIAL PRIMARY KEY,
  wallet_address TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  trust_score FLOAT DEFAULT 50.0,
  total_loans INTEGER DEFAULT 0,
  last_updated TIMESTAMP DEFAULT NOW()
);

-- Create index for fast lookups
CREATE INDEX idx_agents_wallet ON agents(wallet_address);

-- Add comment
COMMENT ON TABLE agents IS 'Agent profiles with wallet-based identity';
```

Click **Run** to execute.

### 3.3 Create `loans` Table

```sql
-- Create loans table
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

-- Create indexes
CREATE INDEX idx_loans_wallet ON loans(wallet_address);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_loans_created ON loans(created_at);

-- Add comment
COMMENT ON TABLE loans IS 'Loan request records with decisions and blockchain hashes';
```

Click **Run** to execute.

### 3.4 Verify Tables

1. Go to **Table Editor** (left sidebar)
2. You should see:
   - `agents` table
   - `loans` table
3. Click each to see columns

---

## Step 4: Install Python Dependencies

### 4.1 Update Dependencies

```bash
cd d:\hackathon\open-loop

# Activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install/update dependencies
pip install -r requirements.txt
```

This installs `supabase` package (version 2.3.4).

### 4.2 Verify Installation

```bash
python -c "import supabase; print(f'Supabase version: {supabase.__version__}')"
```

Should output: `Supabase version: 2.3.4` (or similar)

---

## Step 5: Test Database Connection

### 5.1 Run Backend

```bash
cd d:\hackathon\open-loop

# Activate venv if not already
venv\Scripts\activate

# Start FastAPI server
python -m uvicorn app.main:app --reload
```

Should output:
```
INFO:     Application startup complete
```

Check logs for database connection status:
```
[DB] Health check passed
[DB] Database service initialized successfully
```

### 5.2 Test Health Endpoint

```bash
curl http://127.0.0.1:8000/health
```

If database is connected, you'll see a 200 response.

---

## Step 6: Test Loan Request with Persistence

### 6.1 Make Loan Request

```bash
curl -X POST "http://127.0.0.1:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=50000"
```

### 6.2 Check Response

Response should include:
```json
{
  "wallet_address": "0x742d35cc...",
  "db_loan_id": "123",  // Database record ID
  "approved": true,
  "score": 78,
  "pipeline_status": {
    "persistence": "saved"
  }
}
```

### 6.3 Verify in Supabase

1. Go to Supabase Dashboard
2. Click **Table Editor**
3. Click `agents` table → See new agent record
4. Click `loans` table → See new loan record

---

## Step 7: Monitor Data

### 7.1 View Agent Records

Supabase Dashboard → Table Editor → `agents`:

| wallet_address | created_at | trust_score | total_loans |
|---|---|---|---|
| 0x742d35cc... | 2026-04-25 10:30:45 | 50.0 | 1 |

### 7.2 View Loan Records

Supabase Dashboard → Table Editor → `loans`:

| id | wallet_address | amount | status | interest_rate | created_at |
|---|---|---|---|---|---|
| 1 | 0x742d35cc... | 50000 | approved | 3.5 | 2026-04-25 10:30:46 |

---

## API Endpoints with Database

### Loan Request (Now with Persistence)

**Endpoint**: `POST /loan/request`

**Query Parameters**:
- `wallet_address`: Ethereum address (required, 0x...)
- `amount`: Loan amount (required, 1-10,000,000)

**Request Example**:
```bash
curl -X POST "http://127.0.0.1:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=50000"
```

**Response**:
```json
{
  "request_id": "REQ-XXXX-XXXX-XXXX",
  "wallet_address": "0x742d35cc6634c0532925a3b844bc0f5a3d0e0e0",
  "db_loan_id": "123",
  "approved": true,
  "score": 78.5,
  "interest_rate": 3.5,
  "collateral_required": 2500,
  "status": "approved",
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

**What Happens**:
1. Validates wallet format
2. Creates/retrieves agent in `agents` table
3. Calculates credit score
4. Makes approval decision
5. **Stores loan record in `loans` table** ✅ NEW
6. Returns response with `db_loan_id`

---

## Database Schema Reference

### `agents` Table

```sql
CREATE TABLE agents (
  id              BIGSERIAL PRIMARY KEY,
  wallet_address  TEXT UNIQUE NOT NULL,    -- Ethereum wallet
  created_at      TIMESTAMP DEFAULT NOW(), -- Account creation
  trust_score     FLOAT DEFAULT 50.0,      -- Trust score (0-100)
  total_loans     INTEGER DEFAULT 0,       -- Total loans requested
  last_updated    TIMESTAMP DEFAULT NOW()  -- Last update time
);
```

**Example Row**:
```
id: 1
wallet_address: 0x742d35cc6634c0532925a3b844bc0f5a3d0e0e0
created_at: 2026-04-25 10:30:45
trust_score: 50.0
total_loans: 1
```

### `loans` Table

```sql
CREATE TABLE loans (
  id                  BIGSERIAL PRIMARY KEY,
  wallet_address      TEXT NOT NULL,             -- Agent's wallet
  amount              FLOAT NOT NULL,            -- Loan amount
  interest_rate       FLOAT NOT NULL,            -- Interest rate %
  collateral_required FLOAT NOT NULL,            -- Collateral $
  status              TEXT NOT NULL,             -- 'approved' or 'rejected'
  credit_score        FLOAT NOT NULL,            -- Credit score
  risk_level          TEXT NOT NULL,             -- Risk level
  tx_hash             TEXT,                      -- Blockchain TX hash (nullable)
  decision_reason     TEXT,                      -- Why approved/rejected
  created_at          TIMESTAMP DEFAULT NOW(),  -- Request time
  updated_at          TIMESTAMP DEFAULT NOW()   -- Update time
);
```

**Example Row**:
```
id: 1
wallet_address: 0x742d35cc6634c0532925a3b844bc0f5a3d0e0e0
amount: 50000.0
interest_rate: 3.5
collateral_required: 2500.0
status: approved
credit_score: 78.5
risk_level: low
tx_hash: NULL (will update after blockchain TX)
decision_reason: Approved due to strong repayment history
created_at: 2026-04-25 10:30:46
```

---

## Error Handling

### Database Connection Errors

If you see:
```
[DB] Health check failed: Connection error
```

**Solutions**:
1. Check SUPABASE_URL and SUPABASE_ANON_KEY in `.env`
2. Verify project exists in Supabase Dashboard
3. Check internet connection
4. Restart backend server

### Loan Request Still Works Without DB

If database fails, the system:
- ✅ Still processes loan request
- ✅ Returns valid response
- ✅ Logs error to console
- ⚠️ But loan not persisted (lost on server restart)

Check logs:
```
[DB] Error in create_loan_record: ...
[Loan Route] Database error storing loan: ...
```

---

## Common Tasks

### Get Agent Statistics

From Supabase SQL Editor:

```sql
-- Get total loans by wallet
SELECT 
  wallet_address,
  COUNT(*) as total_requests,
  SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
  AVG(credit_score) as avg_score
FROM loans
GROUP BY wallet_address
ORDER BY total_requests DESC;
```

### Get Loan History for Wallet

```sql
-- Get all loans for a wallet
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

### Update Transaction Hash After Blockchain TX

```sql
-- Update tx_hash after MetaMask transaction completes
UPDATE loans
SET tx_hash = '0xabcdef123...'
WHERE id = 1;
```

---

## Troubleshooting

### Issue: "SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set"

**Solution**:
1. Check `.env` file exists
2. Verify format: `SUPABASE_URL=...` (no quotes needed)
3. Restart server after updating `.env`

### Issue: "Invalid login credentials"

**Solution**:
1. Get fresh API keys from Supabase Dashboard
2. Update `.env` with correct keys
3. Keys are from Settings → API (not project password)

### Issue: "Relation 'agents' does not exist"

**Solution**:
1. Go to Supabase Table Editor
2. Verify `agents` and `loans` tables exist
3. If not, run the SQL creation scripts from Step 3
4. Click **Run** to execute

### Issue: "Column 'wallet_address' not found"

**Solution**:
1. Check table schema in Supabase UI
2. Recreate tables using SQL from Step 3
3. Verify column names match exactly

---

## Production Deployment

### For Production Use:

1. **Use Admin Key (Secure)**
   - Store in secure environment variables
   - Don't commit to git
   - Rotate regularly

2. **Enable Row-Level Security (RLS)**
   ```sql
   ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
   ALTER TABLE loans ENABLE ROW LEVEL SECURITY;
   ```

3. **Add Backup**
   - Supabase → Database → Backups
   - Enable daily automated backups

4. **Monitor Quotas**
   - Supabase Dashboard → Settings → Usage
   - Track API calls and database storage

5. **Add Indexes**
   - Already done in setup scripts
   - Speeds up queries for large datasets

---

## Next Steps

1. ✅ [Step 1-7 above]
2. Test with your frontend
3. Monitor data in Supabase Dashboard
4. Consider adding:
   - Loan history API endpoint
   - Agent statistics endpoint
   - Export to CSV functionality
   - Advanced analytics

---

## Support

- **Supabase Docs**: https://supabase.com/docs
- **Supabase Status**: https://status.supabase.com
- **Python SDK**: https://github.com/supabase/supabase-py

