#!/usr/bin/env python3
"""
Test script for Phase 1 - Advance Payment Allocation Fix

This script tests the new advance payment allocation logic to ensure:
1. Payment Entry is created correctly
2. Accounts Receivable is reduced by advance amount
3. Cash account is increased by advance amount
4. No Customer Advance Payments liability is created
"""

import frappe
from frappe.utils import flt

def test_advance_payment_allocation():
    """Test the new advance payment allocation logic"""
    
    print("=== Testing Phase 1: Advance Payment Allocation ===\n")
    
    # Test configuration
    test_booking_id = "SAL-INV-2024-00001"  # Replace with actual booking ID
    test_advance_amount = 2000
    test_payment_mode = "Cash"
    
    try:
        # Get booking before payment
        booking = frappe.get_doc("Sales Invoice", test_booking_id)
        
        print(f"Testing with booking: {test_booking_id}")
        print(f"Invoice total: ₹{booking.total}")
        print(f"Outstanding amount before advance: ₹{booking.outstanding_amount}")
        print(f"Advance amount to collect: ₹{test_advance_amount}")
        print()
        
        # Get account balances before payment
        company = booking.company
        customer = booking.customer
        
        # Get cash account
        cash_account = frappe.get_value("Company", company, "default_cash_account")
        if not cash_account:
            cash_account = frappe.db.get_value("Account", {
                "account_type": "Cash", 
                "company": company
            }, "name")
        
        # Get AR account
        ar_account = frappe.get_value("Company", company, "default_receivable_account")
        
        print("Account balances BEFORE advance collection:")
        
        # Get cash balance
        cash_balance_before = get_account_balance(cash_account, company)
        print(f"Cash Account ({cash_account}): ₹{cash_balance_before}")
        
        # Get AR balance
        ar_balance_before = get_account_balance(ar_account, company, party_type="Customer", party=customer)
        print(f"AR Account ({ar_account}) for {customer}: ₹{ar_balance_before}")
        
        # Check for advance payments liability account
        advance_account = f"Customer Advance Payments - {frappe.get_value('Company', company, 'abbr')}"
        advance_balance_before = 0
        if frappe.db.exists("Account", advance_account):
            advance_balance_before = get_account_balance(advance_account, company, party_type="Customer", party=customer)
            print(f"Customer Advance Payments ({advance_account}) for {customer}: ₹{advance_balance_before}")
        
        print()
        
        # Call the new confirm_booking_with_advance function
        from rental_management.api.customer_portal import confirm_booking_with_advance
        
        print("Calling confirm_booking_with_advance()...")
        result = confirm_booking_with_advance(test_booking_id, test_advance_amount, test_payment_mode)
        
        if result.get('success'):
            print(f"✅ Success: {result.get('message')}")
            print(f"Payment Entry: {result.get('payment_entry')}")
        else:
            print(f"❌ Failed: {result.get('message')}")
            return
        
        print()
        
        # Refresh booking to get updated values
        booking.reload()
        print(f"Updated outstanding amount: ₹{booking.outstanding_amount}")
        
        print()
        
        # Get account balances after payment
        print("Account balances AFTER advance collection:")
        
        cash_balance_after = get_account_balance(cash_account, company)
        print(f"Cash Account ({cash_account}): ₹{cash_balance_after}")
        
        ar_balance_after = get_account_balance(ar_account, company, party_type="Customer", party=customer)
        print(f"AR Account ({ar_account}) for {customer}: ₹{ar_balance_after}")
        
        if frappe.db.exists("Account", advance_account):
            advance_balance_after = get_account_balance(advance_account, company, party_type="Customer", party=customer)
            print(f"Customer Advance Payments ({advance_account}) for {customer}: ₹{advance_balance_after}")
        
        print()
        
        # Validate results
        print("=== VALIDATION RESULTS ===")
        
        # Check cash increase
        cash_increase = cash_balance_after - cash_balance_before
        if cash_increase == test_advance_amount:
            print(f"✅ Cash increased correctly by ₹{cash_increase}")
        else:
            print(f"❌ Cash increase incorrect: Expected ₹{test_advance_amount}, Got ₹{cash_increase}")
        
        # Check AR decrease
        ar_decrease = ar_balance_before - ar_balance_after
        if ar_decrease == test_advance_amount:
            print(f"✅ AR decreased correctly by ₹{ar_decrease}")
        else:
            print(f"❌ AR decrease incorrect: Expected ₹{test_advance_amount}, Got ₹{ar_decrease}")
        
        # Check outstanding amount
        expected_outstanding = booking.total - test_advance_amount
        if booking.outstanding_amount == expected_outstanding:
            print(f"✅ Outstanding amount correct: ₹{booking.outstanding_amount}")
        else:
            print(f"❌ Outstanding amount incorrect: Expected ₹{expected_outstanding}, Got ₹{booking.outstanding_amount}")
        
        # Check no advance liability created
        if frappe.db.exists("Account", advance_account):
            advance_change = advance_balance_after - advance_balance_before
            if advance_change == 0:
                print(f"✅ No Customer Advance Payments liability created")
            else:
                print(f"❌ Customer Advance Payments liability incorrectly changed by ₹{advance_change}")
        else:
            print(f"✅ No Customer Advance Payments account exists")
        
        print("\n=== TEST COMPLETED ===")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

def get_account_balance(account, company, party_type=None, party=None):
    """Get current balance of an account"""
    try:
        conditions = {
            "account": account,
            "company": company
        }
        
        if party_type and party:
            conditions["party_type"] = party_type
            conditions["party"] = party
        
        balance = frappe.db.sql("""
            SELECT SUM(debit - credit) as balance
            FROM `tabGL Entry`
            WHERE account = %(account)s 
            AND company = %(company)s
            {party_filter}
            AND is_cancelled = 0
        """.format(
            party_filter="AND party_type = %(party_type)s AND party = %(party)s" if party_type and party else ""
        ), conditions)[0][0] or 0
        
        return flt(balance)
        
    except Exception as e:
        print(f"Error getting balance for {account}: {str(e)}")
        return 0

if __name__ == "__main__":
    # Initialize Frappe
    frappe.init(site="your-site-name")  # Replace with your site name
    frappe.connect()
    
    test_advance_payment_allocation()
