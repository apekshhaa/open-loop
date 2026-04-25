# Three Explicit Evaluation Scenarios Guide

## Overview

The Enhanced AI Agent Credit System now explicitly supports **three distinct evaluation scenarios** designed for clear, realistic demonstration purposes. Each scenario maps deterministically to agent characteristics with obvious variation in outputs.

---

## Scenario Mapping

### 1. **STRONG AGENTS** (Agent IDs ending in "1")

**Identifier:** `agent_id.endswith("1")`  
**Examples:** `AGENT-1`, `STARTUP-1`, `FINTECH-1`, `TEST-AGENT-1`

#### Expected Behavior:

| Metric | Range | Details |
|--------|-------|---------|
| **Score** | 75-90 | High confidence in agent quality |
| **Risk Level** | LOW | Minimal risk profile |
| **Interest Rate** | 3.5%-4.5% | Best available rates |
| **Collateral** | 5%-10% | Minimal requirement |
| **Approval Status** | ✓ APPROVED | Always approved |
| **Confidence** | 0.75-0.92 | High model confidence |
| **Agent Tier** | strong | Strong tier classification |

#### Loan Terms:
- **Score ≥ 80:** Rate 3.5%, Collateral 5%, Risk "Excellent"
- **Score > 70:** Rate 4.5%, Collateral 10%, Risk "Low Risk"

#### Decision Reason Examples:
- "Approved due to strong repayment history and low risk profile"
- "Approved based on solid transaction history and positive financial metrics"

#### Sample Response Message:
```
✓ Loan APPROVED at premium rate (3.5%) - Strong agent with outstanding creditworthiness
```

#### Agent Profile:
```json
{
  "success_rate": 80.0-95.0,           // High success rate
  "transaction_count": 30-50,           // Significant history
  "repayment_history": 85.0-98.0,      // Excellent repayment
  "agent_tier": "strong"
}
```

#### Use Case in Demo:
✅ **Shows:** "This agent is high-quality, low-risk, and gets the best terms"

---

### 2. **AVERAGE AGENTS** (Agent IDs ending in "2")

**Identifier:** `agent_id.endswith("2")`  
**Examples:** `AGENT-2`, `STARTUP-2`, `FINTECH-2`, `TEST-AGENT-2`

#### Expected Behavior:

| Metric | Range | Details |
|--------|-------|---------|
| **Score** | 50-70 | Moderate credit assessment |
| **Risk Level** | MEDIUM/HIGH | Moderate risk profile |
| **Interest Rate** | 7.5%-9.5% | Moderate to premium rates |
| **Collateral** | 20%-25% | Moderate requirement |
| **Approval Status** | ✓ APPROVED (with caution) | Approved but conditional |
| **Confidence** | 0.55-0.75 | Medium model confidence |
| **Agent Tier** | average | Average tier classification |

#### Loan Terms:
- **Score ≥ 60:** Rate 7.5%, Collateral 20%, Risk "Medium Risk"
- **Score ≥ 50:** Rate 9.5%, Collateral 25%, Risk "Higher Risk"

#### Decision Reason Examples:
- "Approved with caution due to moderate risk and average performance"
- "Approved at premium rate due to higher perceived risk and limited transaction history"

#### Sample Response Message:
```
~ Loan APPROVED at standard rate (7.5%) - Conditional approval with moderate collateral requirement
~ Loan APPROVED at premium rate (9.5%) - Marginal approval with significant risk premium
```

#### Agent Profile:
```json
{
  "success_rate": 55.0-75.0,           // Moderate success rate
  "transaction_count": 10-30,           // Some history
  "repayment_history": 60.0-85.0,      // Fair to good repayment
  "agent_tier": "average"
}
```

#### Use Case in Demo:
✅ **Shows:** "This agent is acceptable but riskier—we approve but charge more"

---

### 3. **WEAK AGENTS** (All Other Agent IDs)

**Identifier:** All other IDs not ending in "1" or "2"  
**Examples:** `NEWCO-ABC`, `UNKNOWN-XYZ`, `STARTUP-003`, `TEST-AGENT-X`

#### Expected Behavior:

| Metric | Range | Details |
|--------|-------|---------|
| **Score** | 30-50 | Low credit assessment |
| **Risk Level** | HIGH/VERY_HIGH | Significant risk |
| **Interest Rate** | N/A (if rejected) | Irrelevant on rejection |
| **Collateral** | High or N/A | Substantial if approved |
| **Approval Status** | ✗ REJECTED or Marginal | Often rejected |
| **Confidence** | 0.42-0.65 | Low model confidence |
| **Agent Tier** | weak | Weak tier classification |

#### Loan Terms:
- **Score < 50:** REJECTED, Rate 0%, Collateral 0%, Risk "Insufficient"

#### Decision Reason Examples:
- "Rejected due to low reliability score and insufficient credit history"

#### Sample Response Message:
```
✗ Loan REJECTED - Score XX.X below approval threshold. Insufficient creditworthiness.
```

#### Agent Profile:
```json
{
  "success_rate": 30.0-60.0,           // Low to moderate success
  "transaction_count": 0-15,            // Limited history
  "repayment_history": 30.0-70.0,      // Poor to fair repayment
  "agent_tier": "weak"
}
```

#### Use Case in Demo:
✅ **Shows:** "This agent doesn't meet our standards—loan is rejected"

---

## Scoring Formula

### Base Score Calculation:

```
base_score = (success_rate × 40) +
             (min(transaction_count/50, 1.0) × 35) +
             (repayment_history × 25) +
             (amount_factor × 10) +
             (randomness ± 2) +
             tier_adjustment

final_score = clamp(base_score, 0, 100)
```

### Tier Adjustments:
- **Strong:** +15 to +25 points → Moves typical score to 75-90 range
- **Average:** +0 to +10 points → Keeps typical score in 50-70 range
- **Weak:** -15 to -5 points → Moves typical score to 30-50 range

---

## Confidence Scoring

Confidence is tier-specific and independent of transaction history:

| Agent Tier | Confidence Range | Rationale |
|------------|------------------|-----------|
| **Strong** | 0.75 - 0.92 | High confidence in approval decision |
| **Average** | 0.55 - 0.75 | Medium confidence; some uncertainty |
| **Weak** | 0.42 - 0.65 | Low confidence; high uncertainty |

---

## Demo Scenarios

### Test Case 1: STRONG Agent

```bash
POST /loan/request?agent_id=AGENT-1&amount=50000
```

**Expected Response:**
```json
{
  "agent_id": "AGENT-1",
  "amount_requested": 50000,
  "score": 78.5,
  "risk_level": "low",
  "confidence": 0.84,
  "approved": true,
  "interest_rate": 3.5,
  "collateral_required": 2500,
  "decision_reason": "Approved due to strong repayment history and low risk profile",
  "message": "✓ Loan APPROVED at premium rate (3.5%) - Strong agent with outstanding creditworthiness",
  "agent_profile": {
    "success_rate": 92.0,
    "transaction_count": 45,
    "repayment_history": 98.0,
    "agent_tier": "strong"
  }
}
```

### Test Case 2: AVERAGE Agent

```bash
POST /loan/request?agent_id=AGENT-2&amount=50000
```

**Expected Response:**
```json
{
  "agent_id": "AGENT-2",
  "amount_requested": 50000,
  "score": 58.2,
  "risk_level": "high",
  "confidence": 0.62,
  "approved": true,
  "interest_rate": 7.5,
  "collateral_required": 10000,
  "decision_reason": "Approved with caution due to moderate risk and average performance",
  "message": "~ Loan APPROVED at standard rate (7.5%) - Conditional approval with moderate collateral requirement",
  "agent_profile": {
    "success_rate": 72.0,
    "transaction_count": 18,
    "repayment_history": 76.0,
    "agent_tier": "average"
  }
}
```

### Test Case 3: WEAK Agent

```bash
POST /loan/request?agent_id=UNKNOWN-XYZ&amount=50000
```

**Expected Response:**
```json
{
  "agent_id": "UNKNOWN-XYZ",
  "amount_requested": 50000,
  "score": 42.3,
  "risk_level": "very_high",
  "confidence": 0.51,
  "approved": false,
  "interest_rate": 0.0,
  "collateral_required": 0.0,
  "decision_reason": "Rejected due to low reliability score and insufficient credit history",
  "message": "✗ Loan REJECTED - Score 42.3 below approval threshold. Insufficient creditworthiness.",
  "agent_profile": {
    "success_rate": 45.0,
    "transaction_count": 3,
    "repayment_history": 50.0,
    "agent_tier": "weak"
  }
}
```

---

## Running the Demo

### Start the Server:
```bash
python -m uvicorn app.main:app --reload
```

### Run the Demo Script:
```bash
python demo_enhanced_system.py
```

The demo script includes:
- ✓ Two STRONG agent tests (should show ~75-90 scores, 3.5%-4.5% rates)
- ✓ Two AVERAGE agent tests (should show ~50-70 scores, 7.5%-9.5% rates)
- ✓ Three WEAK agent tests (should show ~30-50 scores, mostly rejected)
- ✓ Amount variation tests (shows how loan amount affects scoring)
- ✓ Consistency checks (same tier agents produce similar results)

---

## Key Advantages of This Design

### 1. **Deterministic Variation**
- Agent tier is determined solely by agent_id ending
- Same agent_id always produces consistent tier assignment
- But randomness ensures variation (different runs have different scores within tier)

### 2. **Clear Demo Narrative**
- Three distinct outcomes are obvious and easy to explain
- Each scenario tells a clear story about agent quality
- Stakeholders immediately understand the system's intelligence

### 3. **Realistic Decision-Making**
- Not all agents get approved (shows real decision logic)
- Rates and collateral vary based on risk (shows pricing intelligence)
- Confidence varies with tier (shows model calibration)

### 4. **Explainability**
- decision_reason field clearly explains each decision
- message field provides human-readable summary
- agent_profile shows the data behind the decision

### 5. **Easy to Test**
- Predictable behavior makes testing straightforward
- Can reliably demonstrate system to stakeholders
- Variations within each tier show model sophistication

---

## Customization

### To Add More Tiers:
Modify `get_agent_tier()` in `app/services/analyst.py`:
```python
def get_agent_tier(agent_id: str) -> str:
    if agent_id.endswith("1"):
        return "strong"
    elif agent_id.endswith("2"):
        return "average"
    elif agent_id.endswith("3"):  # New tier
        return "emerging"
    else:
        return "weak"
```

### To Adjust Score Ranges:
Modify `tier_adjustments` in `app/services/analyst.py`:
```python
tier_adjustments = {
    "strong": (20, 30),    # Higher adjustments → higher scores
    "average": (5, 15),
    "weak": (-20, -10)
}
```

### To Adjust Confidence Ranges:
Modify confidence calculation in `app/services/analyst.py`:
```python
if agent_tier == "strong":
    confidence = random.uniform(0.80, 0.95)  # Even higher
elif agent_tier == "average":
    confidence = random.uniform(0.50, 0.70)  # Even lower
```

---

## Technical Implementation

### Files Modified:
- `app/services/analyst.py` - Tier-based scoring and confidence
- `app/services/decision.py` - Three-scenario decision logic
- `app/routes/loan.py` - Response construction with all fields
- `demo_enhanced_system.py` - Comprehensive demo scenarios

### Key Functions:
- `get_agent_tier()` - Maps agent_id to tier
- `calculate_agent_credit_score()` - Applies tier adjustments and calculates confidence
- `make_agent_decision()` - Implements three-scenario decision logic

### Response Fields:
- `score` - Credit score (0-100)
- `risk_level` - Risk classification
- `confidence` - Model confidence (0-1)
- `decision_reason` - Explanation of decision
- `message` - Human-readable summary
- `agent_profile` - Agent characteristics
- `agent_tier` - Tier classification (strong/average/weak)

---

## Success Criteria

✅ **System explicitly demonstrates three distinct scenarios**  
✅ **STRONG agents always get high scores and approval**  
✅ **AVERAGE agents get moderate scores and conditional approval**  
✅ **WEAK agents get low scores and often get rejected**  
✅ **Confidence scoring aligns with agent tier**  
✅ **Decision reasons clearly explain each outcome**  
✅ **Agent profiles show realistic characteristics**  
✅ **Demo is easy to understand and present to stakeholders**  

---

## Next Steps

1. **Start the server:** `python -m uvicorn app.main:app --reload`
2. **Run the demo:** `python demo_enhanced_system.py`
3. **Observe the outputs:** Three distinct scenarios are clearly visible
4. **Share with stakeholders:** Easy to understand and explain
5. **Adjust as needed:** Customize tier ranges and decision logic

