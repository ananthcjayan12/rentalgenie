# Payment Entry Enhancement for Rental Bookings

## Problem Solved
When creating payment entries for rental bookings, the system was showing the full invoice amount instead of the pending amount (after deducting advance payments). This led to incorrect payment processing where users could overpay or not properly account for advance payments.

## Solution Implemented

### 1. Backend Functions Added

#### `calculate_pending_amount(doc)`
- Calculates the pending amount for rental bookings
- Formula: Pending Amount = Total Invoice Amount - Advance Payment
- Note: Caution deposit is not deducted as it's a refundable security deposit
- Updates the `outstanding_amount` field automatically

#### `get_pending_amount(sales_invoice_name)`
- API endpoint to get detailed payment breakdown for a rental booking
- Returns:
  - Total amount
  - Advance amount 
  - Caution deposit
  - Pending amount
  - Current outstanding amount

#### `create_payment_with_advance_allocation()`
- Helper function for creating payment entries with proper advance allocation
- Validates that payment doesn't exceed remaining balance
- Ensures proper accounting treatment

### 2. Frontend Enhancement

#### Client Script for Payment Entry (`payment_entry.js`)
- **Custom Button**: "Get Rental Pending Amount" - allows easy selection of rental bookings
- **Auto-Detection**: Automatically detects when a rental booking is selected
- **Amount Calculation**: Shows only the pending amount instead of full outstanding
- **Visual Feedback**: Displays breakdown of total, advance, caution deposit, and pending amounts
- **Validation**: Prevents overpayment beyond pending amount

### 3. Integration with Validation

#### Enhanced `validate_sales_invoice()`
- Now calls `calculate_pending_amount()` during validation
- Ensures outstanding amount is correctly calculated from the start
- Automatically updates when advance payment changes

## User Experience Improvements

### Before Enhancement:
1. Payment Entry showed full invoice amount (e.g., ₹1,000)
2. Users had to manually calculate pending amount
3. Risk of overpayment or double-counting advance payments
4. No clear visibility of advance payment impact

### After Enhancement:
1. Payment Entry shows only pending amount (e.g., ₹800 if ₹200 advance paid)
2. Clear breakdown displayed: Total ₹1,000, Advance ₹200, Pending ₹800
3. Automatic validation prevents overpayment
4. One-click selection of rental bookings with correct amounts

## How It Works

### For New Payments:
1. User opens Payment Entry for a customer
2. System alerts if rental bookings with outstanding amounts exist
3. User clicks "Get Rental Pending Amount" button
4. Dialog shows rental bookings for the customer
5. User selects a booking
6. System automatically loads only the pending amount
7. User can process payment for the correct amount

### For Direct Reference Selection:
1. User manually adds Sales Invoice reference
2. System detects if it's a rental booking
3. Automatically adjusts outstanding and allocated amounts to pending amount
4. Shows detailed breakdown in a popup

## Technical Details

### Accounting Treatment:
- **Advance Payment**: Already handled via Journal Entry (Customer Advance Payments account)
- **Caution Deposit**: Already handled via Journal Entry (Caution Deposits Received account) 
- **Final Payment**: Standard Payment Entry against Sales Invoice
- **Outstanding Amount**: Automatically reflects only the pending balance

### Error Prevention:
- Validates payment amount doesn't exceed pending balance
- Shows clear error messages
- Prevents accidental overpayment

## Testing Scenarios

1. **Create rental booking with advance payment** → Outstanding should show pending amount
2. **Create payment entry** → Should show pending amount, not full amount
3. **Use custom button** → Should load rental bookings with correct amounts
4. **Try to overpay** → Should show validation error
5. **View payment breakdown** → Should show clear advance/pending split

This enhancement ensures accurate payment processing for rental bookings and prevents accounting errors related to advance payments.
