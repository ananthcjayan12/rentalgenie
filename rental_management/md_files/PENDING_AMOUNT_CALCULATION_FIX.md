# Pending Amount Calculation Fix

## Issue Identified
The pending amount calculation was incorrect. It was not deducting the caution deposit from the pending amount, leading to wrong payment calculations.

## Before Fix:
- **Total Invoice:** ₹1,000.00
- **Advance Paid:** ₹300.00  
- **Caution Deposit:** ₹200.00
- **Pending Amount:** ₹700.00 ❌ (Only subtracting advance)

## After Fix:
- **Total Invoice:** ₹1,000.00
- **Advance Paid:** ₹300.00  
- **Caution Deposit:** ₹200.00
- **Pending Amount:** ₹500.00 ✅ (Subtracting both advance and caution deposit)

## Root Cause
The backend functions had incorrect logic that treated caution deposit as "separate" from the pending amount calculation. However, since caution deposit is money already received from the customer (even if refundable), it should be deducted from the pending amount.

## Functions Fixed

### 1. `calculate_pending_amount(doc)`
**Before:**
```python
pending_amount = total_amount - advance_amount
# Note: Caution deposit is not deducted from pending amount 
# as it's a refundable security deposit, not a payment towards the invoice
```

**After:**
```python
pending_amount = total_amount - advance_amount - caution_deposit
# Both advance and caution deposit are money already received from customer
```

### 2. `get_pending_amount(sales_invoice_name)`
**Before:**
```python
# Calculate pending amount (total - advance, caution deposit is separate)
pending_amount = total_amount - advance_amount
```

**After:**
```python
# Calculate pending amount (total - advance - caution deposit)
# Both advance and caution deposit are money already received from customer
pending_amount = total_amount - advance_amount - caution_deposit
```

## Correct Logic
The pending amount represents the **actual remaining cash that needs to be collected** from the customer:

- **Advance Payment**: Money already received towards the invoice
- **Caution Deposit**: Money already received (even though refundable later)
- **Pending Amount**: Only the remaining balance that needs to be collected

This ensures:
1. Payment entries show the correct amount to collect
2. No overpayment occurs
3. Proper accounting of all money received from customer
4. Accurate outstanding amount tracking

## Impact
This fix ensures that when creating payment entries:
- Only the actual remaining balance (₹500) is shown for collection
- The system properly accounts for all money already received
- Payment reconciliation is accurate
- Financial reports reflect correct outstanding amounts
