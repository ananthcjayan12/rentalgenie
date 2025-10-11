#!/usr/bin/env python3
"""
Diagnostic script to check availability function and existing bookings
"""

import frappe
from frappe.utils import getdate, add_days

def check_existing_bookings():
    """Check what bookings exist in the system"""
    print("=== Checking Existing Bookings ===")
    
    # Check all rental bookings
    bookings = frappe.db.sql("""
        SELECT 
            si.name,
            si.customer,
            si.rental_start_date,
            si.rental_end_date,
            si.booking_status,
            si.docstatus,
            sii.item_code,
            sii.item_name
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE si.is_rental_booking = 1
        ORDER BY si.modified DESC
        LIMIT 10
    """, as_dict=True)
    
    if bookings:
        print(f"Found {len(bookings)} recent rental bookings:")
        for booking in bookings:
            print(f"  Booking: {booking.name}")
            print(f"    Customer: {booking.customer}")
            print(f"    Item: {booking.item_code} ({booking.item_name})")
            print(f"    Dates: {booking.rental_start_date} to {booking.rental_end_date}")
            print(f"    Status: {booking.booking_status} (docstatus: {booking.docstatus})")
            print()
    else:
        print("No rental bookings found in the system")
    
    return bookings

def test_availability_with_real_booking(bookings):
    """Test availability check against a real booking"""
    if not bookings:
        print("No bookings to test against")
        return
    
    print("=== Testing Availability Against Real Booking ===")
    
    # Take the first booking
    test_booking = bookings[0]
    print(f"Testing against booking: {test_booking.name}")
    print(f"Item: {test_booking.item_code}")
    print(f"Dates: {test_booking.rental_start_date} to {test_booking.rental_end_date}")
    
    from rental_management.api.customer_portal import check_item_availability
    
    # Test 1: Check availability for exact same dates
    print("\n1. Testing exact same dates (should be unavailable):")
    result = check_item_availability(
        test_booking.item_code,
        test_booking.rental_start_date,
        test_booking.rental_end_date
    )
    print(f"Result: {result}")
    
    # Test 2: Check availability for overlapping dates
    overlap_start = add_days(test_booking.rental_start_date, -1)
    overlap_end = add_days(test_booking.rental_start_date, 1)
    print(f"\n2. Testing overlapping dates {overlap_start} to {overlap_end} (should be unavailable):")
    result = check_item_availability(
        test_booking.item_code,
        overlap_start,
        overlap_end
    )
    print(f"Result: {result}")
    
    # Test 3: Check availability for future dates (should be available)
    future_start = add_days(test_booking.rental_end_date, 5)
    future_end = add_days(future_start, 2)
    print(f"\n3. Testing future dates {future_start} to {future_end} (should be available):")
    result = check_item_availability(
        test_booking.item_code,
        future_start,
        future_end
    )
    print(f"Result: {result}")

def check_item_code_issues():
    """Check for item code mismatches"""
    print("=== Checking Item Code Issues ===")
    
    # Check rental items and their service counterparts
    items = frappe.db.sql("""
        SELECT 
            m.item_code as main_item,
            m.item_name,
            CONCAT(m.item_code, '-RENTAL') as expected_service_item,
            CASE 
                WHEN s.name IS NOT NULL THEN 'EXISTS'
                ELSE 'MISSING'
            END as service_item_status
        FROM `tabItem` m
        LEFT JOIN `tabItem` s ON s.item_code = CONCAT(m.item_code, '-RENTAL')
        WHERE m.is_rental_item = 1
        AND m.disabled = 0
        LIMIT 10
    """, as_dict=True)
    
    print("Rental items and their service items:")
    for item in items:
        print(f"  Main: {item.main_item} -> Service: {item.expected_service_item} ({item.service_item_status})")
        
        if item.service_item_status == 'MISSING':
            print(f"    ❌ Missing service item: {item.expected_service_item}")

def main():
    """Run diagnostic checks"""
    print("=== Availability Check Diagnostic ===\n")
    
    # Initialize Frappe
    frappe.init(site="dev.localhost")
    frappe.connect()
    frappe.set_user("Administrator")
    
    try:
        # Check existing bookings
        bookings = check_existing_bookings()
        
        # Test availability function
        test_availability_with_real_booking(bookings)
        
        # Check item code issues
        check_item_code_issues()
        
        print("\n=== Diagnostic Complete ===")
        print("\nNext steps:")
        print("1. Check the browser console for frontend debug logs")
        print("2. Check the Frappe logs for backend debug output")
        print("3. Try booking an item and then check availability for the same dates")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        frappe.destroy()

if __name__ == "__main__":
    main()
