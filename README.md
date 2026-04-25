# AI Agent Credit System - FastAPI Backend

A modular, multi-agent lending pipeline system built with FastAPI. This backend represents a financial AI system where specialized agents work together to process loan applications through a distributed pipeline architecture.

## 🏗️ Architecture Overview

The system is built around **six independent agents**, each specializing in different aspects of the lending process:

```
Loan Application
       ↓
┌─────────────────────────────────────────────────────┐
│                    PIPELINE STAGES                   │
├─────────────────────────────────────────────────────┤
│ 1. GATEKEEPER    → Identity Verification & KYC      │
│ 2. ANALYST       → Credit Scoring & Financial       │
│ 3. DECISION      → Approval/Rejection & Terms       │
│ 4. TREASURY      → Fund Availability Check          │
│ 5. SETTLER       → Disbursement & Settlement        │
│ 6. AUDITOR       → Logging & Compliance             │
└─────────────────────────────────────────────────────┘
       ↓
   Loan Disbursement
```

## 📁 Project Structure

```
open-loop/
├── app/
│   ├── __init__.py                 # App package init
│   ├── main.py                     # FastAPI application entry point
│   ├── config.py                   # Configuration management
│   │
│   ├── routes/                     # API endpoint definitions
│   │   ├── __init__.py
│   │   └── loan.py                # /loan routes
│   │
│   ├── services/                   # Core business logic (6 agents)
│   │   ├── __init__.py
│   │   ├── gatekeeper.py           # Identity verification
│   │   ├── analyst.py              # Credit scoring
│   │   ├── decision.py             # Loan decisions
│   │   ├── treasury.py             # Fund management
│   │   ├── settler.py              # Transaction settlement
│   │   └── auditor.py              # Audit logging
│   │
│   ├── models/                     # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── schemas.py              # API request/response models
│   │   └── db_models.py            # Database models
│   │
│   ├── database/                   # Database setup & queries
│   │   ├── __init__.py
│   │   └── db.py                  # Database management
│   │
│   └── utils/                      # Helper functions
│       ├── __init__.py
│       └── helpers.py              # Utility functions
│
├── .env.example                    # Environment variables template
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip or poetry

### 1. Clone and Setup

```bash
# Navigate to project directory
cd open-loop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# At minimum, set:
# - ENVIRONMENT=development
# - SECRET_KEY=your-secret-key
# 
# FOR DATABASE PERSISTENCE (Supabase):
# - SUPABASE_URL=https://your-project.supabase.co
# - SUPABASE_ANON_KEY=your-anon-key
#
# See SUPABASE_SETUP_GUIDE.md for complete setup instructions
```

### 2.5 (NEW) Setup Supabase Database

The system now uses **Supabase** for persistent storage of:
- ✅ Agent profiles and history
- ✅ Loan records and decisions
- ✅ Transaction hashes and audit trail

**Quick Setup:**
1. Go to https://supabase.com and create a free project
2. Get `SUPABASE_URL` and `SUPABASE_ANON_KEY` from Settings → API
3. Add to `.env` file
4. Run SQL table creation scripts (see below)

**Full Setup Guide:** See [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md)  
**Schema Documentation:** See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)

**Create Database Tables** (Supabase SQL Editor):

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
CREATE INDEX idx_agents_wallet ON agents(wallet_address);

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
CREATE INDEX idx_loans_wallet ON loans(wallet_address);
CREATE INDEX idx_loans_status ON loans(status);
```

### 3. Run the Application

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the built-in runner
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Health Check
```
GET /health          # Service health status
GET /status          # Detailed status information
GET /                # API information
```

### AI Agent Loan Request Pipeline ⭐ **NEW**
```
POST   /loan/request                  # Core agent loan pipeline
```

**Quick Start:**
```bash
curl -X POST "http://localhost:8000/loan/request?agent_id=AGENT-001&amount=50000"
```

See [LOAN_REQUEST_GUIDE.md](LOAN_REQUEST_GUIDE.md) for comprehensive documentation.

### Loan Operations
```
POST   /loan/apply                    # Submit new loan application
GET    /loan/{loan_id}                # Get loan status
POST   /loan/{loan_id}/verify         # Trigger identity verification
POST   /loan/{loan_id}/score          # Calculate credit score
POST   /loan/{loan_id}/decide         # Make approval decision
GET    /loan/{loan_id}/pipeline       # Get pipeline stage status
GET    /loan/{loan_id}/audit-trail    # Get audit trail
POST   /loan/{loan_id}/disburse       # Disburse approved funds
```

### Pipeline Info
```
GET    /pipeline/info                 # Get pipeline structure
```

## 🤖 Agent Services

### 1. **Gatekeeper Service** (`gatekeeper.py`)
Responsible for initial identity verification and KYC compliance. Also validates AI agents in the loan request pipeline.

**Functions:**
- `verify_identity()` - Verify borrower identity
- `check_sanctions_list()` - Check against sanctions databases
- `validate_agent_identity()` - **NEW** Verify AI agent registration and status

**Current Agents:**
- `AGENT-001` - High success rate (92%), 45+ transactions
- `AGENT-002` - Good success rate (85%), 28+ transactions
- `AGENT-003` - Moderate success rate (78%), 15+ transactions
- `AGENT-TEST` - New agent (50%), 2 transactions

**TODO:**
- Connect to identity verification APIs (Veriff, IDology)
- Validate government ID documents
- Cross-reference with sanctions lists

### 2. **Analyst Service** (`analyst.py`)
Performs credit analysis and scoring. Includes AI agent credit score calculation.

**Functions:**
- `calculate_credit_score()` - Assign credit score (0-850)
- `analyze_financial_health()` - Comprehensive financial analysis
- `calculate_agent_credit_score()` - **NEW** Score 0-100 for AI agents

**Agent Scoring Methodology:**
- Success Rate Component (0-40 pts): Historical agent success rate
- Transaction Component (0-30 pts): Volume of past transactions
- Amount Component (0-50 pts): Loan amount relative to agent history
- Risk Levels: `low` (80+), `medium` (60-79), `high` (40-59), `very_high` (<40)

**TODO:**
- Integrate with credit bureaus (Equifax, Experian, TransUnion)
- Implement FICO score calculation
- ML models for alternative credit scoring

### 3. **Decision Service** (`decision.py`)
Makes final loan approval/rejection decisions. Implements score-based decision logic for agents.

**Functions:**
- `make_decision()` - Approve/reject loan and set terms
- `calculate_loan_terms()` - Generate amortization schedule
- `make_agent_decision()` - **NEW** Score-based approval with dynamic rates

**Agent Decision Rules:**
- Score > 70: APPROVE at 4.5% interest rate, 10% collateral
- Score 50-70: APPROVE at 9.5% interest rate, 25% collateral
- Score < 50: REJECT
- Term: Fixed 12-month amortization

**TODO:**
- ML model for approval prediction
- Dynamic interest rate calculation
- Risk-adjusted pricing

### 4. **Treasury Service** (`treasury.py`)
Manages lending capital and fund availability. Verifies sufficient capital for approved loans.

**Functions:**
- `check_fund_availability()` - Verify sufficient capital
- `check_portfolio_limits()` - Ensure risk constraints
- `reserve_funds()` - Reserve funds for approved loans
- `check_fund_availability_for_agent()` - **NEW** Verify funds for agent loans

**Capital Management:**
- Total Pool: $1,000,000
- Tracks: Reserved funds, Deployed funds, Utilization %

**TODO:**
- Real-time capital pool queries
- Reserve management system
- Liquidity analysis

### 5. **Settler Service** (`settler.py`)
Executes loan disbursement and settlement.

**Functions:**
- `disburse_funds()` - Transfer funds to borrower
- `execute_blockchain_transaction()` - Blockchain settlement
- `get_transaction_status()` - Track disbursement

**TODO:**
- Bank transfer integration (ACH, wire)
- Cryptocurrency disbursement (testnet)
- Escrow handling

### 6. **Auditor Service** (`auditor.py`)
Maintains audit trails and compliance logs. Logs all pipeline events for AI agent loans.

**Functions:**
- `log_event()` - Log pipeline events
- `log_decision()` - Log decision points
- `get_audit_trail()` - Retrieve audit history
- `generate_compliance_report()` - Generate compliance reports

**Agent Pipeline Events Logged:**
- Identity verification (Gatekeeper)
- Credit score calculation (Analyst)
- Loan decisions (Decision)
- Fund availability checks (Treasury)
- Pipeline completion status

**TODO:**
- Persistent database logging
- Log encryption
- Immutable audit trail (blockchain)

## 🔧 Configuration

Configuration is managed via environment variables. See `.env.example` for all available options.

### Core Settings
```env
ENVIRONMENT=development
DEBUG=True
API_TITLE=AI Agent Credit System
API_VERSION=1.0.0
SECRET_KEY=your-secret-key
```

### Database Configuration - Supabase (Persistent Storage) ✅ **NEW**
```env
# Get these from https://supabase.com → Settings → API
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# The system now:
# ✅ Stores agent profiles with trust scores
# ✅ Persists all loan requests and decisions
# ✅ Tracks approval history per agent
# ✅ Records blockchain transaction hashes
# ✅ Maintains audit trail
#
# Complete Setup: See SUPABASE_SETUP_GUIDE.md
# Schema Details: See DATABASE_SCHEMA.md
```

### Legacy Configuration (Optional)
```env
# MongoDB (alternative to Supabase)
# MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/ai_credit_system
```

### Blockchain Configuration
```env
BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR-PROJECT-ID
ETHEREUM_TESTNET=sepolia
WALLET_ADDRESS=0x...
```

## 📊 Data Models

### LoanRequest
```python
{
  "borrower_id": "BORROWER-123",
  "amount": 25000.0,
  "duration_months": 24,
  "purpose": "Home improvement",
  "credit_history": {...}
}
```

### LoanApplicationResponse
```python
{
  "loan_id": "LOAN-abc123def456",
  "borrower_id": "BORROWER-123",
  "status": "pending",
  "amount_requested": 25000.0,
  "gatekeeper_verified": false,
  "credit_score": null,
  "decision": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## 🔄 Loan Processing Flow

### Traditional Borrower Flow
1. **Application Submission**
   - POST `/loan/apply` with loan request

2. **Identity Verification**
   - POST `/loan/{loan_id}/verify` with KYC data
   - Gatekeeper validates identity

3. **Credit Analysis**
   - POST `/loan/{loan_id}/score` with financial data
   - Analyst calculates credit score

4. **Decision Making**
   - POST `/loan/{loan_id}/decide`
   - Decision service approves/rejects and sets terms

5. **Fund Check**
   - Decision stage queries treasury for fund availability
   - Treasury confirms sufficient capital exists

6. **Disbursement**
   - POST `/loan/{loan_id}/disburse`
   - Settler transfers funds (bank transfer or blockchain)

7. **Audit Trail**
   - GET `/loan/{loan_id}/audit-trail`
   - Complete audit log of all pipeline events

### AI Agent Loan Request Flow ⭐ **NEW - WITH PERSISTENCE**
A streamlined single-endpoint pipeline for AI agents with **Supabase database integration**:

```
POST /loan/request?wallet_address=0x742d35Cc...&amount=50000
    ↓
[1] GATEKEEPER → Validates wallet & gets/creates agent in database
    ↓
[2] ANALYST → Calculates 0-100 credit score
    ├─ Success rate component (0-40 pts)
    ├─ Transaction volume component (0-30 pts)
    └─ Loan amount component (0-50 pts)
    ↓
[3] DECISION → Makes approval decision
    ├─ Score > 70 → Approve @ 3.5% rate, 10% collateral
    ├─ Score 50-70 → Approve @ 7.5% rate, 25% collateral
    └─ Score < 50 → Reject
    ↓
[4] TREASURY → Checks fund availability
    └─ Verifies sufficient capital in lending pool
    ↓
[5] PERSISTENCE → Stores loan record in Supabase
    ├─ Saves to loans table
    ├─ Updates agent profile
    ├─ Records decision reason
    └─ Ready for blockchain tx hash update
    ↓
[6] AUDITOR → Logs all pipeline events
    ├─ Identity verification
    ├─ Scoring details
    ├─ Decision rationale
    └─ Database persistence confirmation
    ↓
Returns: Loan decision with db_loan_id for transaction tracking
```

**Data Persisted:**
- Agent profile (wallet, trust_score, total_loans)
- Loan record (amount, terms, credit_score, status)
- Transaction hash (updated after MetaMask execution)
- Audit trail (all events logged)

**Quick Test with Persistence:**
```bash
# First request - creates agent, stores loan
curl -X POST "http://localhost:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=50000"

# Response includes db_loan_id: "123"

# Second request - same wallet, retrieves existing agent
curl -X POST "http://localhost:8000/loan/request?wallet_address=0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0&amount=25000"

# Check Supabase Dashboard → agents table: total_loans incremented
# Check Supabase Dashboard → loans table: Both loans stored
```

For comprehensive testing guide, see [LOAN_REQUEST_GUIDE.md](LOAN_REQUEST_GUIDE.md).

## 🧪 Example API Calls

### Submit Loan Application
```bash
curl -X POST http://localhost:8000/loan/apply \
  -H "Content-Type: application/json" \
  -d '{
    "borrower_id": "BORROWER-001",
    "amount": 50000,
    "duration_months": 36,
    "purpose": "Business expansion",
    "credit_history": {"years": 5, "accounts": 3}
  }'
```

### Verify Identity
```bash
curl -X POST http://localhost:8000/loan/{loan_id}/verify \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-0123",
    "address": "123 Main St, Anytown, USA"
  }'
```

### Calculate Credit Score
```bash
curl -X POST http://localhost:8000/loan/{loan_id}/score \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_gross_income": 5000,
    "total_monthly_debt": 1500,
    "payment_history_clean": true,
    "employment_years": 3
  }'
```

## 🔌 Integration Points

### ✅ Database Integration - COMPLETE
- **Supabase**: Persistent PostgreSQL database
  - Agent profiles with trust scores
  - Loan request history
  - Audit trail with all pipeline events
  - Blockchain transaction hash storage
  - Ready for future analytics

**Setup Files:**
- [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md) - Complete setup with step-by-step instructions
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Full schema documentation with examples
- `app/services/db_service.py` - Database abstraction layer

**Quick Start:**
```bash
# 1. Create Supabase project at https://supabase.com
# 2. Get credentials and add to .env
# 3. Run SQL table creation scripts (see SUPABASE_SETUP_GUIDE.md)
# 4. Restart backend - database initialized automatically
```

### TODO: External Services (Next Phase)
- **Identity Verification**: Veriff, IDology, or similar
- **Credit Bureaus**: Equifax, Experian, TransUnion APIs
- **Payment Processing**: Stripe, ACH, Wire transfer APIs
- **Blockchain**: Web3.py for Ethereum testnet transactions

### TODO: Machine Learning (Future)
- Credit scoring models
- Fraud detection models
- Loan approval prediction models

## 🧩 Modularity

Each agent is completely independent and can:
- Be updated without affecting others
- Be tested in isolation
- Be swapped with alternative implementations
- Be deployed as separate microservices
- Be scaled independently

## 📈 Future Enhancements

- [x] Wallet-based agent identity (instead of agent IDs)
- [x] Real database integration (Supabase PostgreSQL) ✅ NEW
- [x] Deterministic credit scoring (same wallet = same score)
- [x] Persistent loan history tracking ✅ NEW
- [x] Agent approval rate analytics ✅ NEW
- [ ] Async pipeline processing (message queues)
- [ ] Machine learning models for scoring/decisions
- [ ] Blockchain settlement (testnet - MetaMask integration)
- [ ] Additional API endpoints (agent history, statistics)
- [ ] User authentication and authorization
- [ ] Rate limiting and throttling
- [ ] API versioning
- [ ] Comprehensive test suite
- [ ] Docker containerization
- [ ] Kubernetes deployment configs
- [ ] GraphQL API layer
- [ ] Real-time notifications (WebSockets)

## 🛡️ Security Considerations

- [ ] Add authentication (JWT, OAuth2)
- [ ] Implement rate limiting
- [ ] Add request validation
- [ ] Encrypt sensitive data
- [ ] Implement CORS properly
- [ ] Add API versioning
- [ ] Implement proper error handling
- [ ] Add request logging and monitoring
- [ ] Implement data sanitization

## 📝 Logging

The application uses Python's standard logging module. Configure log level in `.env`:

```env
LOG_LEVEL=INFO
```

Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🤝 Contributing

When extending the system:

1. Follow the existing module structure
2. Add comprehensive docstrings
3. Include TODO comments for future implementation
4. Write unit tests for new services
5. Update this README with new features

## 📄 License

[Add your license here]

## 📧 Contact

[Add contact information]

---

## 🎯 Key Concepts

### Modularity
Each agent operates independently with clear input/output contracts. They communicate via standardized response objects (`AgentResponse`).

### Separation of Concerns
- **Routes**: Handle HTTP requests/responses
- **Services**: Contain business logic
- **Models**: Define data structures
- **Database**: Handle persistence
- **Utils**: Provide helper functions

### Extensibility
The system is designed for easy extension:
- Add new agents by creating new service files
- Add new routes by extending the router
- Add new models by extending schemas
- Add new database backends via the abstraction

### TODO-Driven Development
Each module includes TODO comments indicating areas for future implementation, making it easy to identify extension points.

---

**Ready to build the future of AI lending!** 🚀