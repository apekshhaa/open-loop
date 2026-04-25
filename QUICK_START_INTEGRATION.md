# Quick Start: Running Frontend + Backend

## What You'll Build

A fully integrated AI Agent Credit System where:
- Frontend collects loan requests (agent_id + amount)
- Backend processes loans through 5-stage pipeline
- Real-time results display on frontend
- System demonstrates three agent tiers (strong/average/weak)

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

## Setup (5 Minutes)

### Step 1: Backend Setup

```bash
# Open Terminal 1 - From project root
cd open-loop

# Create Python virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Frontend Setup

```bash
# Open Terminal 2 - From project root
cd open-loop

# Install Node dependencies (one time only)
npm install
```

### Step 3: Start Backend

```bash
# In Terminal 1 (with venv activated)
python -m uvicorn app.main:app --reload
```

**Output should show:**
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 4: Start Frontend

```bash
# In Terminal 2
npm run dev
```

**Output should show:**
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Press q to quit
```

### Step 5: Open in Browser

Navigate to: **http://localhost:5173/**

---

## Using the System

### Flow 1: Strong Agent (Expected: APPROVED)

1. **Agent ID:** `AGENT-1`
2. **Loan Amount:** `50000`
3. **Expected Result:**
   - Score: 75-90
   - Risk: LOW
   - Rate: 3.5-4.5%
   - Status: ✓ APPROVED

### Flow 2: Average Agent (Expected: CONDITIONAL APPROVAL)

1. **Agent ID:** `AGENT-2`
2. **Loan Amount:** `50000`
3. **Expected Result:**
   - Score: 50-70
   - Risk: MEDIUM/HIGH
   - Rate: 7.5-9.5%
   - Status: ✓ APPROVED (with caution)

### Flow 3: Weak Agent (Expected: REJECTION)

1. **Agent ID:** `UNKNOWN-XYZ`
2. **Loan Amount:** `50000`
3. **Expected Result:**
   - Score: 30-50
   - Risk: HIGH/VERY_HIGH
   - Rate: N/A
   - Status: ✗ REJECTED

---

## Understanding the UI Flow

```
Portal (Landing)
    ↓
Console (Enter Data)
    → Agent ID: AGENT-1
    → Amount: 50000
    → [Initiate Analysis]
    ↓
Engine (Processing)
    → Shows progress 0→100%
    → Live log of analysis stages
    → Animated score counter
    → Making actual API call...
    ↓
Verdict (Results)
    → Credit Score: 78.5
    → Risk Level: LOW
    → Interest Rate: 3.5%
    → Collateral: $2,500
    → Decision: APPROVED
    → [Execute Disbursement] → Execution/Ledger
```

---

## Key Features

✅ **Real Backend Integration**
- Every response comes from FastAPI backend
- No mock/dummy data
- Actual credit scoring algorithm

✅ **Three Distinct Scenarios**
- AGENT-1 → Strong tier (high approval rate, low rates)
- AGENT-2 → Average tier (moderate approval, moderate rates)
- Others → Weak tier (low approval rate, high rates)

✅ **Live Processing**
- Progress bar shows analysis stages
- Console logs all pipeline steps
- Real-time score calculation

✅ **Beautiful UI**
- Luxury tech aesthetic
- Smooth animations
- Clear visual hierarchy
- Responsive design

---

## Testing Different Scenarios

### Validate API Works

```bash
# Test with curl (if backend is running)
curl -X POST "http://127.0.0.1:8000/loan/request?agent_id=AGENT-1&amount=50000"
```

Expected response includes: score, risk_level, approved, interest_rate, etc.

### Test Frontend Inputs

| Agent ID | Amount | Expected Tier | Expected Score |
|----------|--------|---------------|-----------------|
| AGENT-1 | 50000 | STRONG | 75-90 |
| STARTUP-1 | 100000 | STRONG | 75-90 |
| AGENT-2 | 50000 | AVERAGE | 50-70 |
| FINTECH-2 | 75000 | AVERAGE | 50-70 |
| NEWCO-ABC | 50000 | WEAK | 30-50 |
| UNKNOWN-XYZ | 50000 | WEAK | 30-50 |

### Test Error Handling

Try these to see error messages:
- Empty Agent ID → "Please enter an Agent ID"
- Amount = 0 → "Enter a valid loan amount"
- Backend offline → "Failed to connect to API"

---

## Troubleshooting

### Backend won't start
```bash
# Make sure you're in the venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Try a different port
python -m uvicorn app.main:app --port 8001 --reload
```

### Frontend shows errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### API calls failing
```bash
# Check if backend is running
curl http://127.0.0.1:8000/docs

# Check .env.local has correct URL
cat .env.local
# Should show: VITE_API_URL=http://127.0.0.1:8000
```

### Port already in use
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Or use different port
python -m uvicorn app.main:app --port 8001 --reload
```

---

## What's Happening Behind the Scenes

### When You Submit a Loan Request:

1. **Frontend** captures Agent ID and Loan Amount
2. **Frontend** sends POST to backend: `/loan/request?agent_id=X&amount=Y`
3. **Backend Pipeline** processes:
   - Gatekeeper: Validates agent identity
   - Analyst: Calculates credit score (0-100) based on:
     - Agent success rate
     - Transaction history
     - Repayment history
     - Loan amount
     - Agent tier (1→strong, 2→average, others→weak)
   - Decision: Determines approval and rates
   - Treasury: Checks fund availability
   - Auditor: Logs all events
4. **Backend** returns complete response with:
   - Score, risk level, confidence
   - Approval decision
   - Interest rate, collateral requirement
   - Monthly payment calculation
   - Decision reasoning
   - Agent profile metrics
5. **Frontend** displays results in Verdict component

---

## Production Deployment

When ready to deploy:

1. **Backend (FastAPI)**
   ```bash
   # Use Gunicorn + Uvicorn
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Frontend (React)**
   ```bash
   # Build for production
   npm run build
   
   # Output in dist/ directory
   # Deploy to: Vercel, Netlify, AWS S3, etc.
   ```

3. **Update .env for production**
   ```env
   VITE_API_URL=https://api.yourdomain.com
   ```

---

## Next Steps

### ✅ Immediate
1. Run both servers locally
2. Test with different agent IDs
3. Check backend logs for processing details
4. View browser console for frontend logs

### 🔜 Enhancements
1. Add transaction history page
2. Add real-time notifications
3. Add portfolio analytics dashboard
4. Add webhook support for status updates
5. Add admin approval interface

### 📚 Documentation
- Swagger UI: http://127.0.0.1:8000/docs
- Integration Guide: `FRONTEND_BACKEND_INTEGRATION.md`
- Three Scenarios: `THREE_SCENARIO_GUIDE.md`
- API Details: `README.md`

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                    BROWSER (User)                       │
├─────────────────────────────────────────────────────────┤
│                   Vite + React                          │
│  Portal → Console → Engine → Verdict → Execution       │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP POST
                       │ /loan/request
                       ↓
┌──────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│  Port 8000                                              │
├──────────────────────────────────────────────────────────┤
│  Gatekeeper → Analyst → Decision → Treasury → Auditor  │
│                                                         │
│  Credit Scoring:                                        │
│  - Agent tier detection (1/2/other)                    │
│  - Score calculation (0-100)                           │
│  - Confidence scoring (0-1)                            │
│  - Risk assessment                                      │
│  - Approval decision & pricing                         │
└──────────────────────────────────────────────────────────┘
```

---

## Key Files

| Location | Purpose |
|----------|---------|
| `src/services/api.ts` | Frontend→Backend communication |
| `src/components/Engine.tsx` | Makes API call, shows progress |
| `src/components/Verdict.tsx` | Displays results |
| `app/main.py` | Backend entry point |
| `app/routes/loan.py` | Loan request endpoint |
| `app/services/analyst.py` | Credit scoring logic |
| `app/services/decision.py` | Approval decision logic |

---

## Support

For issues or questions, check:
1. Browser console (F12) for frontend errors
2. Backend terminal for processing logs
3. `.env.local` for correct API URL
4. Swagger UI (http://127.0.0.1:8000/docs) for API details

---

**Happy testing! 🚀**

