#!/usr/bin/env python3
"""
Simple test script to validate the delivery accounting fixes
"""

import sys
import os

def test_accounting_fix():
    """Test the delivery accounting fix"""
    
    print("🔧 Testing Delivery Accounting Fix")
    print("=" * 50)
    
    try:
        import frappe
        frappe.connect()
        
        # Check if we have any confirmed bookings to test
        confirmed_bookings = frappe.get_all("Sales Invoice",
            filters={
                "is_rental_booking": 1,
                "booking_status": "Confirmed",
                "docstatus": 1
            },
            fields=["name", "customer", "total", "advance_amount"],
            limit=1
        )
        
        if not confirmed_bookings:
            print("❌ No confirmed bookings found")
            print("   Please create a confirmed booking first")
            return
        
        booking = confirmed_bookings[0]
        print(f"✅ Found test booking: {booking.name}")
        print(f"   Customer: {booking.customer}")
        print(f"   Total: ₹{booking.total}")
        print(f"   Advance: ₹{booking.advance_amount or 0}")
        
        balance_due = booking.total - (booking.advance_amount or 0)
        caution_amount = 4000
        
        print(f"\n🚚 Testing delivery with:")
        print(f"   Balance: ₹{balance_due}")
        print(f"   Caution: ₹{caution_amount}")
        
        # Import and test the function
        from rental_management.api.customer_portal import collect_balance_and_caution_deposit
        
        result = collect_balance_and_caution_deposit(
            booking_id=booking.name,
            balance_amount=balance_due,
            caution_deposit_amount=caution_amount,
            payment_mode="Cash"
        )
        
        if result.get('success'):
            print("✅ Delivery accounting successful!")
            print(f"   Status: {result.get('status')}")
            print(f"   Balance collected: ₹{result.get('balance_collected')}")
            print(f"   Caution collected: ₹{result.get('caution_deposit_collected')}")
        else:
            print(f"❌ Delivery accounting failed: {result.get('message')}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_accounting_fix()
