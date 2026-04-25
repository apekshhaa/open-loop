# AI Agent Credit System - Quick Start Guide

## Getting Started (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy the example configuration
cp .env.example .env

# No changes needed for basic testing, but you can customize:
# ENVIRONMENT=development
# DEBUG=True
# PORT=8000
```

### Step 3: Start the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test the API

Open in your browser or use curl:

**Health Check:**
```bash
curl http://localhost:8000/health
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick API Test

### 1. Submit a Loan Application
```bash
curl -X POST http://localhost:8000/loan/apply \
  -H "Content-Type: application/json" \
  -d '{
    "borrower_id": "TEST-USER-001",
    "amount": 50000,
    "duration_months": 36,
    "purpose": "Business expansion"
  }'
```

Response (save the `loan_id`):
```json
{
  "loan_id": "LOAN-abc123def456",
  "borrower_id": "TEST-USER-001",
  "status": "pending",
  "amount_requested": 50000,
  "gatekeeper_verified": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. Verify Identity (Gatekeeper Stage)
```bash
LOAN_ID="LOAN-abc123def456"

curl -X POST http://localhost:8000/loan/${LOAN_ID}/verify \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "address": "123 Main St, Anytown, USA"
  }'
```

### 3. Calculate Credit Score (Analyst Stage)
```bash
curl -X POST http://localhost:8000/loan/${LOAN_ID}/score \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_gross_income": 8000,
    "total_monthly_debt": 2000,
    "payment_history_clean": true,
    "employment_years": 5,
    "long_credit_history": true,
    "multiple_accounts": true
  }'
```

### 4. Make Loan Decision (Decision Stage)
```bash
curl -X POST http://localhost:8000/loan/${LOAN_ID}/decide
```

Response will include approval decision and interest rate.

### 5. Check Pipeline Status
```bash
curl http://localhost:8000/loan/${LOAN_ID}/pipeline
```

### 6. Get Audit Trail
```bash
curl http://localhost:8000/loan/${LOAN_ID}/audit-trail
```

### 7. Disburse Funds (Settler Stage)
```bash
curl -X POST http://localhost:8000/loan/${LOAN_ID}/disburse
```

## Project Structure Overview

```
app/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration management
├── routes/              # API endpoints (/loan)
├── services/            # 6 Agent services
│   ├── gatekeeper.py   # Identity verification
│   ├── analyst.py      # Credit scoring
│   ├── decision.py     # Loan decisions
│   ├── treasury.py     # Fund management
│   ├── settler.py      # Disbursement
│   └── auditor.py      # Audit logging
├── models/              # Pydantic schemas
├── database/            # Database setup (placeholder)
└── utils/               # Helper functions
```

## Key Features

✅ **Six Independent Agents** - Each with its own responsibility  
✅ **Clean Architecture** - Modular and extensible design  
✅ **Comprehensive API** - Full loan lifecycle endpoints  
✅ **Audit Trail** - Complete transaction logging  
✅ **Type Safety** - Pydantic models for all data  
✅ **Environment Config** - Flexible configuration system  
✅ **API Documentation** - Swagger and ReDoc available  

## Next Steps

1. **Explore the API** - Use Swagger at http://localhost:8000/docs
2. **Check the Services** - Review each agent in `/app/services/`
3. **Study the Models** - Understand data structures in `/app/models/`
4. **Implement TODOs** - Follow TODO comments for future features
5. **Add Database** - Uncomment MongoDB/Supabase in requirements.txt
6. **Integrate Services** - Connect to real identity verification, credit bureaus, etc.

## Troubleshooting

**Port already in use:**
```bash
uvicorn app.main:app --reload --port 8001
```

**Import errors:**
```bash
pip install -e .
```

**Environment variable issues:**
```bash
# Ensure .env file exists and check for typos
cat .env
```

## Learning Path

1. Start with [README.md](README.md) for architecture overview
2. Review [app/main.py](app/main.py) for app structure
3. Explore [app/routes/loan.py](app/routes/loan.py) for endpoints
4. Study [app/services/](app/services/) for agent implementations
5. Check [app/models/schemas.py](app/models/schemas.py) for data structures

## Environment Variables

Key variables you can customize in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| ENVIRONMENT | development | Environment (development/production) |
| DEBUG | True | Enable debug mode |
| HOST | 0.0.0.0 | Server host |
| PORT | 8000 | Server port |
| LOG_LEVEL | INFO | Logging level |
| MONGODB_URL | None | MongoDB connection string |
| SUPABASE_URL | None | Supabase connection string |

## API Response Format

All responses follow a standard format:

**Success:**
```json
{
  "loan_id": "LOAN-xyz",
  "status": "processing",
  "data": {...}
}
```

**Error:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error",
    "details": {...}
  }
}
```

## Performance Tips

- Use `/health` for load balancer checks
- Implement database caching for credit scores
- Consider async processing for long-running stages
- Use message queues (Celery, RabbitMQ) for pipeline
- Implement rate limiting for production

## Security Checklist

- [ ] Add authentication (JWT/OAuth2)
- [ ] Enable HTTPS in production
- [ ] Set strong SECRET_KEY in .env
- [ ] Implement rate limiting
- [ ] Validate all inputs
- [ ] Encrypt sensitive data
- [ ] Add request logging
- [ ] Implement CORS properly

---

Ready to process loans with AI agents! 🚀
