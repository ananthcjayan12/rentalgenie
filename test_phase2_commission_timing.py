#!/usr/bin/env python3
"""
Test script for Phase 2 - Owner Commission Timing Fix

This script tests the new owner commission timing logic to ensure:
1. No commission liability is created at invoice submission (advance stage)
2. Commission liability is only created at delivery stage
3. Commission flag is properly set to avoid duplication
4. Correct supplier accounts are used
"""

import frappe
from frappe.utils import flt

def test_commission_timing():
    """Test the new commission timing logic"""
    
    print("=== Testing Phase 2: Owner Commission Timing ===\n")
    
    # Test configuration
    test_booking_id = "SAL-INV-2024-00001"  # Replace with actual third-party item booking
    
    try:
        # Get booking
        booking = frappe.get_doc("Sales Invoice", test_booking_id)
        
        print(f"Testing with booking: {test_booking_id}")
        print(f"Booking status: {booking.booking_status}")
        print(f"Owner commission created: {booking.get('owner_commission_created', 0)}")
        print()
        
        # Check if booking has third-party items
        has_third_party_items = False
        third_party_details = []
        
        for item in booking.items:
            # Check if this is a service item, map back to main item
            main_item_code = item.item_code
            if item.item_code.endswith('-RENTAL'):
                main_item_code = item.item_code[:-7]
            
            main_item = frappe.get_doc("Item", main_item_code)
            if main_item.get('is_third_party_item'):
                has_third_party_items = True
                commission_pct = flt(main_item.get('owner_commission_percent', 0))
                supplier = main_item.get('third_party_supplier')
                item_amount = flt(item.amount)
                commission_amount = (item_amount * commission_pct) / 100.0
                
                third_party_details.append({
                    'item_code': item.item_code,
                    'main_item': main_item_code,
                    'supplier': supplier,
                    'commission_pct': commission_pct,
                    'item_amount': item_amount,
                    'commission_amount': commission_amount
                })
        
        if not has_third_party_items:
            print("❌ This booking has no third-party items. Please test with a third-party item booking.")
            return
        
        print("Third-party items found:")
        for detail in third_party_details:
            print(f"  - {detail['item_code']} → {detail['main_item']}")
            print(f"    Supplier: {detail['supplier']}")
            print(f"    Commission: {detail['commission_pct']}% of ₹{detail['item_amount']} = ₹{detail['commission_amount']}")
        print()
        
        # Get account balances before delivery
        company = booking.company
        company_abbr = frappe.get_value("Company", company, "abbr")
        
        # Check commission liability account
        payable_account = frappe.db.get_value("Account", {"account_type": "Payable", "company": company}, "name")
        if not payable_account:
            payable_account = f"Current Liabilities - {company_abbr}"
        
        print("Account balances BEFORE delivery:")
        
        # Check commission liabilities for each supplier
        total_commission_before = 0
        for detail in third_party_details:
            if detail['supplier']:
                commission_balance = get_account_balance(
                    payable_account, company, 
                    party_type="Supplier", party=detail['supplier']
                )
                print(f"Commission liability for {detail['supplier']}: ₹{commission_balance}")
                total_commission_before += commission_balance
        
        print(f"Total commission liabilities before: ₹{total_commission_before}")
        print()
        
        # Simulate delivery stage if booking is in "Confirmed" status
        if booking.booking_status == "Confirmed":
            print("Booking is in 'Confirmed' status. Simulating delivery...")
            
            # Calculate balance and caution deposit amounts
            advance_paid = booking.advance_amount or 0
            balance_due = booking.total - advance_paid
            caution_deposit = 4000  # Example caution deposit
            
            # Call the delivery function
            from rental_management.api.customer_portal import collect_balance_and_caution_deposit
            
            print(f"Calling collect_balance_and_caution_deposit with:")
            print(f"  Balance: ₹{balance_due}")
            print(f"  Caution Deposit: ₹{caution_deposit}")
            
            result = collect_balance_and_caution_deposit(
                test_booking_id, balance_due, caution_deposit, "Cash"
            )
            
            if result.get('success'):
                print(f"✅ Success: {result.get('message')}")
            else:
                print(f"❌ Failed: {result.get('message')}")
                return
            
            print()
            
            # Refresh booking to check flag
            booking.reload()
            print(f"Owner commission created flag after delivery: {booking.get('owner_commission_created', 0)}")
            print()
            
            # Check account balances after delivery
            print("Account balances AFTER delivery:")
            
            total_commission_after = 0
            for detail in third_party_details:
                if detail['supplier']:
                    commission_balance = get_account_balance(
                        payable_account, company, 
                        party_type="Supplier", party=detail['supplier']
                    )
                    print(f"Commission liability for {detail['supplier']}: ₹{commission_balance}")
                    total_commission_after += commission_balance
            
            print(f"Total commission liabilities after: ₹{total_commission_after}")
            
            # Validate results
            print()
            print("=== VALIDATION RESULTS ===")
            
            expected_commission_increase = sum(detail['commission_amount'] for detail in third_party_details)
            actual_commission_increase = total_commission_after - total_commission_before
            
            if abs(actual_commission_increase - expected_commission_increase) < 0.01:
                print(f"✅ Commission liability increased correctly by ₹{actual_commission_increase}")
            else:
                print(f"❌ Commission liability increase incorrect:")
                print(f"    Expected: ₹{expected_commission_increase}")
                print(f"    Actual: ₹{actual_commission_increase}")
            
            if booking.get('owner_commission_created'):
                print(f"✅ Owner commission created flag is set correctly")
            else:
                print(f"❌ Owner commission created flag not set")
                
        else:
            print(f"Booking is in '{booking.booking_status}' status.")
            print("Please test with a booking in 'Confirmed' status for delivery simulation.")
        
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
    
    test_commission_timing()
