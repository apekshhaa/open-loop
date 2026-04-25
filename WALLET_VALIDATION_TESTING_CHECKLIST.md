# Wallet Validation Fix - Testing Checklist

## ✅ Pre-Testing Setup

- [ ] Install MetaMask browser extension (if not already installed)
- [ ] Have test Ethereum account ready (any testnet address works)
- [ ] Open browser DevTools (F12)
- [ ] Clear browser cache and refresh

---

## 🧪 Test Suite 1: MetaMask Connection

### Test 1.1: MetaMask Detection
**Steps:**
1. Open app to Console screen
2. DevTools Console → Look for logs starting with `[WalletService]`

**Expected:**
- [ ] See: `[WalletService] MetaMask detected`
- [ ] Connect Wallet button is NOT red/disabled
- [ ] UI shows "Not Connected" status

**If Failed:**
- [ ] Check if MetaMask is installed
- [ ] Check if MetaMask is enabled in browser
- [ ] Check logs for error messages

---

### Test 1.2: Manual Wallet Connection
**Steps:**
1. Click "Connect Wallet" button
2. Approve in MetaMask popup
3. Check DevTools Console for logs
4. Observe UI changes

**Expected:**
- [ ] MetaMask popup appears automatically
- [ ] After approval, UI shows connected status
- [ ] Wallet address displayed in left panel
- [ ] Console shows multiple `[WalletService]` logs
- [ ] Console shows `[Console] Wallet connected successfully`
- [ ] "Request Loan" button becomes enabled (gold color)

**Sample Logs:**
```
[WalletService] Requesting MetaMask accounts...
[WalletService] MetaMask connection successful: { address: "0x...", accountCount: 1 }
[WalletService] Validating address: { original: "0x...", trimmed: "0x...", length: 42 }
[WalletService] Address validated successfully: { original: "0x...", normalized: "0x..." }
[Console] Wallet connected successfully: 0x...
```

---

### Test 1.3: Disconnect Wallet
**Steps:**
1. After connecting wallet, click "Disconnect Wallet" button
2. Observe UI changes

**Expected:**
- [ ] UI shows "Not Connected" status
- [ ] Wallet address no longer displayed
- [ ] "Request Loan" button becomes disabled
- [ ] Console clear of connection logs

---

## 🧪 Test Suite 2: Address Validation

### Test 2.1: Valid Address Accepted
**Steps:**
1. Connect wallet (any valid MetaMask address)
2. Enter amount: 50000
3. Click "Request Loan"
4. Check console logs

**Expected:**
- [ ] No error messages show
- [ ] Console shows `[API] Wallet validated successfully`
- [ ] API call is made to backend
- [ ] Results appear on Verdict screen

---

### Test 2.2: Address with Whitespace Handling
**Purpose:** Verify that addresses are trimmed before validation

**Manual Test (DevTools):**
```javascript
// In DevTools Console:
import { validateWalletAddress } from './src/services/walletService.ts';

const addressWithSpace = "  0x742d35Cc6634C0532925a3b844Bc0f5a3d0E0E0  ";
const result = validateWalletAddress(addressWithSpace);
console.log(result);
```

**Expected:**
- [ ] `isValid: true`
- [ ] Address trimmed and returned
- [ ] No whitespace in normalized address

---

### Test 2.3: Invalid Address Handling
**Manual Test (DevTools):**
```javascript
import { validateWalletAddress } from './src/services/walletService.ts';

// Test invalid addresses:
console.log(validateWalletAddress("0x123"));  // Too short
console.log(validateWalletAddress("invalid"));  // Not hex
console.log(validateWalletAddress(""));  // Empty
```

**Expected:**
- [ ] All return `{ isValid: false, error: "...", address: null }`
- [ ] Clear error messages
- [ ] No false positives

---

### Test 2.4: Checksum Address Handling
**Purpose:** Verify mixed-case (checksum) addresses are accepted

**Steps:**
1. In MetaMask, note the connected address (e.g., starts with lowercase)
2. Manually test with mixed case in DevTools:

```javascript
import { validateWalletAddress } from './src/services/walletService.ts';

// Use the address but with random uppercase letters:
validateWalletAddress("0x742D35Cc6634C0532925A3b844Bc0f5A3D0E0E0");
```

**Expected:**
- [ ] `isValid: true`
- [ ] Address normalized to proper checksum or lowercase
- [ ] No error for mixed-case

---

## 🧪 Test Suite 3: Error Messages

### Test 3.1: Error When Wallet Not Connected
**Steps:**
1. Start fresh (no wallet connected)
2. Enter loan amount
3. Click "Request Loan"

**Expected:**
- [ ] Error appears: "Please connect your wallet first"
- [ ] No API call made
- [ ] Red error box visible

---

### Test 3.2: Error Message for Missing MetaMask
**Steps:**
1. Disable MetaMask extension (or test in non-MetaMask browser)
2. Try to click "Connect Wallet"

**Expected:**
- [ ] Button shows as disabled (red)
- [ ] Error: "MetaMask is not installed..."
- [ ] No popup appears

---

### Test 3.3: Error for Invalid Loan Amount
**Steps:**
1. Connect wallet
2. Try to enter invalid amounts:
   - "0"
   - "-100"
   - "abc"
3. Click "Request Loan"

**Expected:**
- [ ] Error: "Please enter a valid loan amount"
- [ ] No API call made

---

## 🧪 Test Suite 4: UI Behavior

### Test 4.1: Button State Management
**Scenarios:**

**Scenario A: Not Connected**
- [ ] "Request Loan" button is disabled (gray color)
- [ ] Text shows "Connect Wallet First"
- [ ] Click does nothing

**Scenario B: Connecting (Loading)**
- [ ] Button shows loading spinner
- [ ] Text shows "Connecting..."
- [ ] Button disabled during connection

**Scenario C: Connected**
- [ ] Button is enabled (gold color)
- [ ] Text shows "Request Loan"
- [ ] Click initiates request

**Scenario D: Request Loading**
- [ ] Button shows loading state
- [ ] Text shows "Analyzing..."
- [ ] Cannot click again

---

### Test 4.2: Connection Restoration
**Steps:**
1. Connect wallet
2. Refresh page (Ctrl+R or F5)
3. Observe if wallet reconnects

**Expected:**
- [ ] After refresh, wallet still shows as connected
- [ ] No need to click "Connect Wallet" again
- [ ] Console shows connection restoration log

---

### Test 4.3: Account Switching
**Steps:**
1. Connect wallet with Account A
2. In MetaMask, switch to Account B
3. Observe UI

**Expected:**
- [ ] UI updates automatically
- [ ] New wallet address displayed
- [ ] No error messages
- [ ] Console shows `accountsChanged` event log

---

## 🧪 Test Suite 5: End-to-End Loan Request

### Test 5.1: Complete Happy Path
**Steps:**
1. Connect wallet (MetaMask)
2. Enter amount: 50000
3. Click "Request Loan"
4. Wait for result
5. Check DevTools console throughout

**Expected Flow:**
- [ ] Step 1: Connect button works
- [ ] Step 2: Amount input accepts value
- [ ] Step 3: Request button becomes active and clickable
- [ ] Step 4: Processing spinner shows
- [ ] Step 5: Console shows validation logs
- [ ] Step 6: API call made with wallet_address parameter
- [ ] Step 7: Results displayed on Verdict screen
- [ ] Step 8: Credit score, status, and details shown

**Console Should Show:**
```
[Console] Loan request initiated { walletConnected: true, ... }
[Console] All validations passed, initiating analysis
[API] Validating wallet address: 0x...
[API] Wallet validated successfully
[API] Loan request: { wallet: "0x...", amount: 50000 }
[API] Loan request successful: { requestId: "REQ-...", approved: true }
```

---

## 🧪 Test Suite 6: Logging Verification

### Test 6.1: Enable Console Logging
**Steps:**
1. Open DevTools Console
2. Filter by: `[WalletService]`, `[Console]`, `[API]`

**Expected:**
- [ ] Clear, prefixed logs visible
- [ ] Logs show timestamps and contexts
- [ ] No console errors
- [ ] No console warnings (except expected MetaMask warnings)

### Test 6.2: Debug Information Visible
**For Each Operation, Verify:**
- [ ] User action logged (what user did)
- [ ] Validation details logged (what was validated)
- [ ] Decision logged (pass/fail)
- [ ] Result logged (final outcome)

---

## 📋 Summary Checklist

### Critical Tests (Must Pass)
- [ ] MetaMask connects successfully
- [ ] Valid addresses accepted without error
- [ ] Invalid addresses rejected with clear error
- [ ] Whitespace is handled correctly
- [ ] Button states work correctly
- [ ] End-to-end loan request works

### Important Tests (Should Pass)
- [ ] Wallet disconnects properly
- [ ] Connection restores on page refresh
- [ ] Account switching detected
- [ ] All error messages are clear
- [ ] Logging is comprehensive

### Nice-to-Have Tests (Could Pass)
- [ ] Checksum addresses handled
- [ ] MetaMask not installed shows proper error
- [ ] UI animations smooth
- [ ] Performance acceptable

---

## 🚨 Troubleshooting

### Issue: "MetaMask not detected" but it's installed
**Solution:**
1. Check if MetaMask extension is enabled
2. Refresh page
3. Check browser console for errors
4. Try in a different browser
5. Check `window.ethereum` in DevTools: `console.log(window.ethereum)`

### Issue: "Invalid wallet address" error with MetaMask wallet
**Solution:**
1. Check DevTools console for full error message
2. Copy the exact address from error log
3. Test address directly: `validateWalletAddress("0x...")`
4. Check if address has extra whitespace in logs
5. Verify MetaMask is on same network as backend expects

### Issue: Connection doesn't persist after refresh
**Solution:**
1. Check if localStorage has wallet data (if persisted)
2. Check if MetaMask is still connected
3. Look for auth errors in console
4. Try MetaMask connection again
5. Check network tab for failed requests

### Issue: API call fails after valid wallet connection
**Solution:**
1. Check backend is running: `http://127.0.0.1:8000`
2. Check VITE_API_URL in .env.local
3. Check DevTools Network tab for request details
4. Look for CORS errors
5. Check backend logs for validation failures

---

## ✅ Completion Criteria

All tests are complete when:
- ✅ All Critical Tests pass
- ✅ No console errors (only expected warnings)
- ✅ MetaMask integration works end-to-end
- ✅ No false "invalid address" errors
- ✅ Logging clearly shows what's happening
- ✅ User can request loan with valid wallet

---

## 📈 Performance Considerations

- Validation should complete in < 1ms
- MetaMask connection popup appears within 1 second
- UI updates responsive (< 100ms)
- No console spam (logs are organized)

---

## 🎯 Next Steps After Testing

If all tests pass:
1. ✅ Deploy to staging
2. ✅ Test with real MetaMask accounts on testnet
3. ✅ Load test with multiple concurrent connections
4. ✅ Test on different browsers (Chrome, Firefox, Safari)
5. ✅ Deploy to production

