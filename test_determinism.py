"""Test backend determinism — verifies same inputs always produce same outputs."""
import requests

API = "http://127.0.0.1:8000/loan/request"

def test(agent_id, amount):
    r = requests.post(API, params={"agent_id": agent_id, "amount": amount})
    return r.json()

# === Agent 1 (Strong) ===
r1a = test("1", 50000)
r1b = test("1", 50000)
print("=== AGENT '1' (Strong) ===")
print(f"  Score: {r1a['score']}  Risk: {r1a['risk_level']}  Approved: {r1a['approved']}  Rate: {r1a['interest_rate']}%")
print(f"  Repeat identical: {r1a['score'] == r1b['score'] and r1a['approved'] == r1b['approved']}")

# === Agent 2 (Average) ===
r2a = test("2", 50000)
r2b = test("2", 50000)
print("\n=== AGENT '2' (Average) ===")
print(f"  Score: {r2a['score']}  Risk: {r2a['risk_level']}  Approved: {r2a['approved']}  Rate: {r2a['interest_rate']}%")
print(f"  Repeat identical: {r2a['score'] == r2b['score'] and r2a['approved'] == r2b['approved']}")

# === Agent 3 (Weak / Other) ===
r3a = test("3", 50000)
r3b = test("3", 50000)
print("\n=== AGENT '3' (Weak) ===")
print(f"  Score: {r3a['score']}  Risk: {r3a['risk_level']}  Approved: {r3a['approved']}  Rate: {r3a['interest_rate']}%")
print(f"  Repeat identical: {r3a['score'] == r3b['score'] and r3a['approved'] == r3b['approved']}")

# === Amount variation ===
r_low = test("1", 10000)
r_high = test("1", 500000)
print("\n=== AMOUNT VARIATION (Agent 1) ===")
print(f"  $10K  -> Score: {r_low['score']}")
print(f"  $500K -> Score: {r_high['score']}")
print(f"  Both approved: {r_low['approved']} / {r_high['approved']}")

# === All pass? ===
all_ok = all([
    80 <= r1a["score"] <= 90,
    55 <= r2a["score"] <= 70,
    30 <= r3a["score"] <= 50,
    r1a["approved"] == True,
    r2a["approved"] == True,
    r3a["approved"] == False,
    r1a["score"] == r1b["score"],
    r2a["score"] == r2b["score"],
    r3a["score"] == r3b["score"],
])
print(f"\n{'[PASS] ALL TESTS PASSED' if all_ok else '[FAIL] SOME TESTS FAILED'}")
