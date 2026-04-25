# Frontend-Backend Integration Guide

## Overview

The Vite + React frontend now has full integration with the FastAPI backend for the AI Agent Credit System. Real-time communication between frontend and backend enables:

- ✅ Actual loan request processing
- ✅ Real credit score calculation from agent data
- ✅ Live risk assessment and approval decisions
- ✅ Dynamic UI updates based on backend responses
- ✅ Complete transaction tracking through pipeline

---

## Architecture

### Frontend Stack
- **Framework:** React 18+ with TypeScript
- **Build Tool:** Vite
- **API Client:** Fetch API
- **Animations:** Motion/Framer Motion
- **Styling:** Tailwind CSS

### Backend Stack
- **Framework:** FastAPI
- **Port:** 8000
- **Endpoint:** `POST /loan/request?agent_id={id}&amount={amount}`
- **Response:** Comprehensive loan decision with agent analysis

### Communication Flow

```
User Input (Console)
    ↓
App.tsx (state management)
    ↓
Engine.tsx (analysis simulation + actual API call)
    ↓
src/services/api.ts (backend request)
    ↓
FastAPI Backend (/loan/request)
    ↓
Response (AnalysisData)
    ↓
Verdict.tsx (display results)
```

---

## Setup Instructions

### 1. Backend Setup

```bash
# Navigate to project root
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

# Start backend server
python -m uvicorn app.main:app --reload
```

Backend will be available at: `http://127.0.0.1:8000`

### 2. Frontend Setup

```bash
# In project root, install Node dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173` (or similar)

---

## API Integration Details

### Configuration

**File:** `.env.local` or `.env`

```env
VITE_API_URL=http://127.0.0.1:8000
```

The frontend automatically reads this environment variable via `import.meta.env.VITE_API_URL`.

### API Service

**File:** `src/services/api.ts`

This module handles all backend communication:

```typescript
// Request a loan from the backend
const response = await requestLoan(agentId, amount);

// Returns BackendLoanResponse with:
// - credit_score (0-100)
// - risk_level (low/medium/high/very_high)
// - confidence (0-1)
// - interest_rate (%)
// - collateral_required (USD)
// - approved (boolean)
// - decision_reason (explanation)
// - agent_profile (metrics)
// - ... and more
```

### Request Format

```
POST /loan/request?agent_id=AGENT-1&amount=50000

Headers:
  Content-Type: application/json
```

### Response Format

```json
{
  "request_id": "req_xyz123",
  "agent_id": "AGENT-1",
  "amount_requested": 50000,
  "score": 78.5,
  "risk_level": "low",
  "confidence": 0.84,
  "approved": true,
  "decision_reason": "Approved due to strong repayment history...",
  "interest_rate": 3.5,
  "collateral_required": 2500,
  "monthly_payment": 4285.71,
  "total_interest": 1428.56,
  "message": "✓ Loan APPROVED at premium rate (3.5%)...",
  "agent_profile": {
    "success_rate": 92.0,
    "transaction_count": 45,
    "repayment_history": 98.0,
    "agent_tier": "strong"
  },
  "timestamp": "2026-04-25T...",
  "pipeline_status": {
    "gatekeeper": "valid",
    "analyst": "score_78.5",
    "decision": "approved",
    "treasury": "available"
  }
}
```

---

## Component Integration

### Console Component (`src/components/Console.tsx`)

**Purpose:** User input for loan request

**Integration Points:**
- Accepts `agentId` (string) and `amount` (number)
- Validates inputs before submission
- Shows loading state while processing
- Calls `onInitiate()` callback to trigger analysis

**Example Usage:**
```typescript
<Console onInitiate={(agentId, amount) => {
  // Trigger Engine component with real data
}} />
```

### Engine Component (`src/components/Engine.tsx`)

**Purpose:** Backend communication and visual progress

**Integration Points:**
```typescript
import { requestLoan, simulateAnalysisProgress } from '../services/api';

// 1. Simulate progress visualization
const cleanup = simulateAnalysisProgress((msg, progress, type) => {
  addLog(msg, type);
  setProgress(progress);
});

// 2. Make actual backend call
const response = await requestLoan(agentId, amount);

// 3. Transform response to AnalysisData
const analysisData: AnalysisData = {
  agentId: response.agent_id,
  creditScore: response.score,
  approved: response.approved,
  // ... map all fields
};

// 4. Pass complete data to Verdict
onComplete(analysisData);
```

### Verdict Component (`src/components/Verdict.tsx`)

**Purpose:** Display backend analysis results

**Integration Points:**
```typescript
// Displays real backend data
<AureumPanel title="credit_score">
  <span>{data.creditScore}</span>  {/* Real score from backend */}
</AureumPanel>

<AureumPanel title="interest_rate">
  <span>{data.interestRate.toFixed(2)}%</span>  {/* Real rate */}
</AureumPanel>

<AureumPanel title="decision_reason">
  <p>{data.decisionReason}</p>  {/* Actual reason from backend */}
</AureumPanel>
```

---

## Data Flow

### Complete Example: Agent-1 Requests $50,000

1. **User Input (Console)**
   ```
   Agent ID: AGENT-1
   Amount: $50,000
   [Click] Initiate Analysis
   ```

2. **App Routes to Engine**
   ```typescript
   handleInitiateAnalysis("AGENT-1", 50000)
   setCurrentScreen("engine")
   ```

3. **Engine Makes API Call**
   ```
   POST /loan/request?agent_id=AGENT-1&amount=50000
   ```

4. **Backend Processes**
   - Gatekeeper: Validates agent identity ✓
   - Analyst: Calculates credit score (78.5) ✓
   - Decision: Determines approval (true) ✓
   - Treasury: Checks funds (available) ✓
   - Auditor: Logs transaction ✓

5. **Response Returns**
   ```json
   {
     "score": 78.5,
     "approved": true,
     "interest_rate": 3.5,
     "collateral_required": 2500,
     ...
   }
   ```

6. **Engine Transforms Data**
   ```typescript
   const analysisData = {
     creditScore: 78.5,
     approved: true,
     interestRate: 3.5,
     ...
   }
   ```

7. **Verdict Displays Results**
   ```
   ✓ LOAN APPROVED
   Score: 78.5
   Rate: 3.5%
   Collateral: $2,500
   Decision Reason: Approved due to...
   ```

---

## Error Handling

### Backend Communication Errors

**File:** `src/services/api.ts`

```typescript
try {
  const response = await fetch(API_ENDPOINT, {...});
  if (!response.ok) {
    throw new Error(`API failed: ${response.status}`);
  }
} catch (error) {
  throw {
    message: `Failed to request loan: ${error.message}`,
    status: error.status
  }
}
```

### UI Error Display

**File:** `src/components/Engine.tsx`

```typescript
{error && (
  <div className="bg-red-500/10 border border-red-500/30">
    <h3>Analysis Failed</h3>
    <p>{error.message}</p>
    <button onClick={() => window.location.reload()}>
      Try Again
    </button>
  </div>
)}
```

### Common Error Scenarios

1. **Backend not running**
   ```
   Failed to request loan: Failed to connect to http://127.0.0.1:8000
   ```
   → Start backend: `python -m uvicorn app.main:app --reload`

2. **Invalid agent_id**
   ```
   Failed to request loan: Invalid agent ID
   ```
   → Use valid format (e.g., AGENT-1, STARTUP-2)

3. **Invalid amount**
   ```
   Failed to request loan: Amount must be > 0
   ```
   → Enter positive number between $1 and $10,000,000

4. **CORS errors**
   ```
   Access to XMLHttpRequest blocked by CORS policy
   ```
   → Add CORS configuration to FastAPI backend

---

## Testing the Integration

### Manual Test with Console + Frontend

```bash
# Terminal 1: Start backend
python -m uvicorn app.main:app --reload

# Terminal 2: Start frontend
npm run dev

# Browser: Navigate to http://localhost:5173
# 1. Enter Agent ID: AGENT-1
# 2. Enter Amount: 50000
# 3. Click "Initiate Analysis"
# 4. Watch progress in Engine component
# 5. View real results in Verdict component
```

### Manual Test with cURL

```bash
curl -X POST "http://127.0.0.1:8000/loan/request?agent_id=AGENT-1&amount=50000" \
  -H "Content-Type: application/json"
```

### Test Different Agent Tiers

**Strong Agent** (expected: HIGH score 75-90)
```bash
curl -X POST "http://127.0.0.1:8000/loan/request?agent_id=AGENT-1&amount=50000"
```

**Average Agent** (expected: MEDIUM score 50-70)
```bash
curl -X POST "http://127.0.0.1:8000/loan/request?agent_id=AGENT-2&amount=50000"
```

**Weak Agent** (expected: LOW score 30-50, rejection)
```bash
curl -X POST "http://127.0.0.1:8000/loan/request?agent_id=UNKNOWN-XYZ&amount=50000"
```

---

## Development Workflow

### Making Changes to API Service

1. **Update API endpoint** (if backend changes)
   ```typescript
   // src/services/api.ts
   const LOAN_REQUEST_ENDPOINT = `${API_BASE_URL}/loan/request`;
   ```

2. **Update response types** (if backend response schema changes)
   ```typescript
   // src/services/api.ts
   export interface BackendLoanResponse {
     // ... update fields
   }
   ```

3. **Update Engine component** (if processing changes)
   ```typescript
   // src/components/Engine.tsx
   const response = await requestLoan(agentId, amount);
   // Transform as needed
   ```

4. **Test in Verdict component** (ensure display works)
   ```typescript
   // src/components/Verdict.tsx
   <span>{data.creditScore}</span>  // Should show new field
   ```

### Adding New Response Fields

1. Add to `BackendLoanResponse` interface
2. Map in `Engine.tsx` to `AnalysisData`
3. Display in `Verdict.tsx` or other components

---

## Performance Considerations

### Loading States

- Console shows spinner while processing
- Engine displays progress bar (0-100%)
- Animated logs show real-time status
- Verdict displays once complete

### Network Optimization

- Single API call per request (no polling)
- Simulated progress is local (no network overhead)
- Response is processed immediately
- No unnecessary data fetching

### Rendering Optimization

- `motion` library for smooth animations
- `AnimatePresence` for component transitions
- Component memoization where needed
- Efficient state updates

---

## CORS Configuration (If Needed)

If you get CORS errors, add this to `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### Backend won't connect
- Check if backend is running: `python -m uvicorn app.main:app --reload`
- Verify API URL in `.env.local`: `VITE_API_URL=http://127.0.0.1:8000`
- Check for port conflicts: `netstat -ano | findstr :8000`

### Frontend won't load
- Clear npm cache: `npm cache clean --force`
- Delete node_modules: `rm -rf node_modules && npm install`
- Start dev server: `npm run dev`

### Blank responses
- Check browser console for errors (F12)
- Verify backend response format in Network tab
- Check that backend endpoint returns valid JSON

### Slow responses
- Monitor backend logs for processing time
- Check system resources (CPU/memory)
- Test with smaller loan amounts if needed

---

## Next Steps

1. **Test the integration** with different agent IDs
2. **Monitor backend logs** for any issues
3. **Customize UI** for your specific needs
4. **Add additional features** like:
   - Transaction history page
   - Portfolio analytics
   - Real-time notifications
   - Webhook for loan status updates

---

## File Reference

| File | Purpose | Integration Point |
|------|---------|-------------------|
| `src/services/api.ts` | Backend communication | All API calls |
| `src/components/Console.tsx` | User input | Collects agent_id & amount |
| `src/components/Engine.tsx` | Analysis processing | Makes API call, shows progress |
| `src/components/Verdict.tsx` | Results display | Shows backend response data |
| `src/types.ts` | Type definitions | Response mapping (BackendLoanResponse → AnalysisData) |
| `.env.local` | Environment config | VITE_API_URL setting |
| `app/main.py` | Backend entry point | FastAPI server |
| `app/routes/loan.py` | Loan endpoint | `POST /loan/request` implementation |

---

## Support & Documentation

- **API Docs:** http://127.0.0.1:8000/docs (Swagger UI)
- **Backend Details:** See `THREE_SCENARIO_GUIDE.md`
- **Requirements:** `requirements.txt` (Python), `package.json` (Node)
- **Status:** See `REQUIREMENT_VALIDATION.md`

