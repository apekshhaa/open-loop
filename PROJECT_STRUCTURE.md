# Project Structure Guide

## Complete File Tree

```
open-loop/
│
├── README.md                       # Main documentation
├── QUICKSTART.md                   # Quick start guide
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
│
└── app/                            # Main application directory
    │
    ├── __init__.py                 # Package initialization
    ├── main.py                     # FastAPI app entry point
    ├── config.py                   # Configuration management
    │
    ├── routes/                     # API Endpoints
    │   ├── __init__.py
    │   └── loan.py                 # /loan route handlers (8 endpoints)
    │
    ├── services/                   # Business Logic (6 Agent Services)
    │   ├── __init__.py
    │   ├── gatekeeper.py           # Stage 1: Identity Verification
    │   ├── analyst.py              # Stage 2: Credit Scoring
    │   ├── decision.py             # Stage 3: Loan Decisions
    │   ├── treasury.py             # Stage 4: Fund Management
    │   ├── settler.py              # Stage 5: Disbursement
    │   └── auditor.py              # Stage 6: Audit Logging
    │
    ├── models/                     # Data Models & Schemas
    │   ├── __init__.py
    │   ├── schemas.py              # Pydantic API models
    │   └── db_models.py            # Database models
    │
    ├── database/                   # Database Layer
    │   ├── __init__.py
    │   └── db.py                   # DB connection & repositories
    │
    └── utils/                      # Utility Functions
        ├── __init__.py
        └── helpers.py              # Helper functions & validators
```

## File Descriptions

### Root Level Files

| File | Purpose |
|------|---------|
| `README.md` | Comprehensive project documentation |
| `QUICKSTART.md` | Quick setup and testing guide |
| `requirements.txt` | Python package dependencies |
| `.env.example` | Environment variables template |
| `.gitignore` | Git repository ignore rules |

### Core Application Files

#### `app/main.py` (275 lines)
**Purpose:** FastAPI application initialization and configuration

**Key Components:**
- FastAPI app instantiation with metadata
- CORS middleware configuration
- Startup/shutdown event handlers
- Health check endpoints (`/health`, `/status`)
- Root endpoint (`/`)
- Error handlers
- Pipeline information endpoint (`/pipeline/info`)
- Route registration

**Exports:**
- `app`: FastAPI application instance

#### `app/config.py` (50 lines)
**Purpose:** Configuration management and environment variables

**Key Components:**
- `Settings` class (Pydantic BaseSettings)
- Environment variable loading
- Configuration categories:
  - Application settings
  - Server settings
  - Database configuration
  - Blockchain configuration
  - Security settings

**Exports:**
- `settings`: Global settings instance

### Routes Module (`app/routes/`)

#### `app/routes/loan.py` (450 lines)
**Purpose:** Loan operation API endpoints

**Endpoints:**
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/loan/apply` | Submit new loan application |
| GET | `/loan/{loan_id}` | Get loan status |
| POST | `/loan/{loan_id}/verify` | Trigger identity verification |
| POST | `/loan/{loan_id}/score` | Calculate credit score |
| POST | `/loan/{loan_id}/decide` | Make approval decision |
| GET | `/loan/{loan_id}/pipeline` | Get pipeline status |
| GET | `/loan/{loan_id}/audit-trail` | Get audit trail |
| POST | `/loan/{loan_id}/disburse` | Disburse funds |

**Features:**
- Request validation
- In-memory loan storage
- Pipeline stage tracking
- Event logging via auditor

### Services Module (`app/services/`) - 6 Agent Services

Each service implements a specific stage in the lending pipeline.

#### `app/services/gatekeeper.py` (120 lines)
**Stage:** 1 - Identity Verification

**Functions:**
- `verify_identity()` - Verify borrower with KYC data
- `check_sanctions_list()` - Check sanctions databases

**Features:**
- Fraud score calculation
- Verification method tracking
- Sanctions checking

**TODO:**
- Connect to identity verification APIs
- Validate government ID documents
- Cross-reference sanctions lists

#### `app/services/analyst.py` (200 lines)
**Stage:** 2 - Credit Analysis & Scoring

**Functions:**
- `calculate_credit_score()` - Assign credit score (0-850)
- `analyze_financial_health()` - Financial analysis

**Features:**
- Weighted credit score model
- Risk level determination
- Financial factor analysis
- Amortization calculations

**TODO:**
- Integrate credit bureau APIs
- Implement FICO scoring
- ML models for scoring

#### `app/services/decision.py` (240 lines)
**Stage:** 3 - Loan Decision Making

**Functions:**
- `make_decision()` - Approve/reject with terms
- `calculate_loan_terms()` - Generate loan terms

**Features:**
- Criteria evaluation
- Interest rate calculation
- Loan condition generation
- Amortization scheduling

**TODO:**
- ML approval prediction
- Dynamic interest rates
- Risk-adjusted pricing

#### `app/services/treasury.py` (210 lines)
**Stage:** 4 - Fund & Capital Management

**Functions:**
- `check_fund_availability()` - Check capital pool
- `check_portfolio_limits()` - Verify risk constraints
- `reserve_funds()` - Reserve approved loan amounts
- `get_capital_status()` - Current capital status

**Features:**
- Capital pool tracking
- Portfolio limit checking
- Fund reservation system
- Diversification requirements

**TODO:**
- Real-time capital queries
- Reserve management
- Liquidity analysis

#### `app/services/settler.py` (200 lines)
**Stage:** 5 - Fund Disbursement & Settlement

**Functions:**
- `disburse_funds()` - Transfer funds to borrower
- `execute_blockchain_transaction()` - Blockchain settlement
- `get_transaction_status()` - Track disbursement

**Features:**
- Multiple disbursement methods
- Blockchain transaction execution (testnet)
- Transaction tracking
- Confirmation generation

**TODO:**
- Bank transfer integration
- Crypto disbursement
- Escrow handling

#### `app/services/auditor.py` (230 lines)
**Stage:** 6 - Audit Logging & Compliance

**Functions:**
- `log_event()` - Log pipeline events
- `log_decision()` - Log decision points
- `get_audit_trail()` - Retrieve audit history
- `generate_compliance_report()` - Compliance reports

**Features:**
- Event logging with timestamps
- Decision tracking with reasoning
- Audit trail retrieval
- Compliance reporting

**TODO:**
- Persistent database logging
- Log encryption
- Immutable audit trail

### Models Module (`app/models/`)

#### `app/models/schemas.py` (200 lines)
**Purpose:** Pydantic request/response models

**Key Models:**
- `LoanStatus` - Enum of loan statuses
- `AgentStatus` - Enum of agent processing statuses
- `LoanRequest` - Loan application request
- `LoanApplicationResponse` - Loan application response
- `AgentResponse` - Generic agent response
- `CreditScoreResponse` - Analyst response
- `LoanApprovalResponse` - Decision response
- `PipelineStatusResponse` - Pipeline status
- `HealthCheckResponse` - Health check response

#### `app/models/db_models.py` (80 lines)
**Purpose:** Database model placeholders

**Key Models:**
- `LoanApplicationDB` - Loan persistence model
- `AuditLogDB` - Audit log persistence model

### Database Module (`app/database/`)

#### `app/database/db.py` (120 lines)
**Purpose:** Database connection and repositories

**Key Components:**
- `DatabaseManager` - Database connection management
- `LoanRepository` - Loan data operations
- `AuditRepository` - Audit log operations

**Features:**
- MongoDB/Supabase configuration
- Connection lifecycle management
- Health checking
- CRUD operations (placeholders)

### Utils Module (`app/utils/`)

#### `app/utils/helpers.py` (350 lines)
**Purpose:** Utility and helper functions

**ID Generation:**
- `generate_loan_id()` - Generate unique loan ID
- `generate_log_id()` - Generate unique log ID
- `generate_transaction_id()` - Generate unique transaction ID

**Validation:**
- `validate_email()` - Validate email format
- `validate_loan_amount()` - Validate loan amount
- `validate_duration()` - Validate loan duration
- `RequestValidator` - Request validation class

**Calculations:**
- `calculate_monthly_payment()` - Amortization calculation
- `calculate_total_interest()` - Total interest calculation

**Formatting:**
- `format_currency()` - Format as currency
- `format_percentage()` - Format as percentage
- `get_timestamp_string()` - ISO timestamp

**Responses:**
- `create_error_response()` - Standardized error format
- `create_success_response()` - Standardized success format

## Code Statistics

| Category | Count | Details |
|----------|-------|---------|
| **Files** | 24 | Python modules + config files |
| **Services** | 6 | Agent implementations |
| **Routes** | 1 | Route module with 8 endpoints |
| **Models** | 12+ | Pydantic models |
| **Databases** | 2 | DB model classes |
| **Utils** | 15+ | Helper functions |
| **Lines of Code** | ~2500 | Excluding tests |

## Module Dependencies

```
main.py
├── config.py
├── models/
├── routes/
│   └── loan.py
│       ├── models/
│       ├── services/
│       │   ├── gatekeeper.py
│       │   ├── analyst.py
│       │   ├── decision.py
│       │   ├── treasury.py
│       │   ├── settler.py
│       │   └── auditor.py
│       └── utils/
└── database/
```

## Data Flow

```
API Request
    ↓
routes/loan.py (endpoint handler)
    ↓
services/* (business logic)
    ↓
models/ (data validation & response)
    ↓
database/ (persistence layer - optional)
    ↓
utils/ (helpers)
    ↓
API Response
```

## Extension Points

### Adding a New Agent
1. Create `app/services/new_agent.py`
2. Implement agent class with `AGENT_NAME` constant
3. Add route in `app/routes/loan.py`
4. Add model in `app/models/schemas.py`
5. Update `app/services/__init__.py`

### Adding Database Support
1. Uncomment database packages in `requirements.txt`
2. Implement connection in `app/database/db.py`
3. Update repository methods
4. Modify services to use repositories

### Adding Authentication
1. Create `app/auth/` module
2. Implement JWT or OAuth2
3. Add security dependency to routes
4. Update `app/main.py` with middleware

### Adding New Endpoints
1. Add route handler in `app/routes/loan.py`
2. Create request/response models in `app/models/schemas.py`
3. Call appropriate service methods
4. Add error handling

## Configuration Hierarchy

```
.env (runtime overrides)
    ↓
app/config.py (Settings class)
    ↓
Default values (in Settings class)
```

## Import Organization

**Circular Import Prevention:**
- Services don't import each other
- Routes import services, not vice versa
- Models imported by both routes and services
- Utils imported by all modules

## Testing Strategy (TODO)

Suggested test structure:
```
tests/
├── unit/
│   ├── test_services/
│   ├── test_models/
│   └── test_utils/
├── integration/
│   └── test_routes/
└── fixtures/
    └── sample_data.py
```

---

This structure provides a scalable, maintainable foundation for the AI Agent Credit System. Each module is independent yet integrated, making it easy to extend and test.
