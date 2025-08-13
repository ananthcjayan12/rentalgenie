"""
Quick Validation Script for Rental Management System
Test basic functionality without running full test suite
"""

import frappe
from frappe.utils import getdate, add_days, today, flt

def validate_basic_setup():
    """Validate basic system setup"""
    print("🔍 Validating Basic Setup...")
    
    checks = []
    
    # Check if app is installed
    if 'rental_management' in frappe.get_installed_apps():
        checks.append(("✅", "Rental Management app is installed"))
    else:
        checks.append(("❌", "Rental Management app is NOT installed"))
        return checks
    
    # Check custom fields existence
    item_fields = [
        "is_rental_item", "rental_rate_per_day", "item_category", 
        "current_rental_status", "is_third_party_item", "owner_commission_percent"
    ]
    
    for field in item_fields:
        if frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": field}):
            checks.append(("✅", f"Item field '{field}' exists"))
        else:
            checks.append(("❌", f"Item field '{field}' missing"))
    
    # Check customer fields
    customer_fields = ["unique_customer_id", "mobile_number", "total_bookings", "total_rental_amount"]
    
    for field in customer_fields:
        if frappe.db.exists("Custom Field", {"dt": "Customer", "fieldname": field}):
            checks.append(("✅", f"Customer field '{field}' exists"))
        else:
            checks.append(("❌", f"Customer field '{field}' missing"))
    
    # Check sales invoice fields
    invoice_fields = ["is_rental_booking", "function_date", "rental_duration_days", "booking_status"]
    
    for field in invoice_fields:
        if frappe.db.exists("Custom Field", {"dt": "Sales Invoice", "fieldname": field}):
            checks.append(("✅", f"Sales Invoice field '{field}' exists"))
        else:
            checks.append(("❌", f"Sales Invoice field '{field}' missing"))
    
    return checks

def test_item_creation():
    """Test creating a rental item"""
    print("\n🔍 Testing Item Creation...")
    
    try:
        # Create test item
        item_code = "VALIDATE-TEST-DRESS-001"
        
        # Delete if exists
        if frappe.db.exists("Item", item_code):
            try:
                frappe.delete_doc("Item", item_code, force=True)
            except:
                # If deletion fails, try disabling first
                try:
                    existing_item = frappe.get_doc("Item", item_code)
                    existing_item.disabled = 1
                    existing_item.save()
                    frappe.delete_doc("Item", item_code, force=True)
                except:
                    # If still fails, use a different item code
                    import random
                    item_code = f"VALIDATE-TEST-DRESS-{random.randint(100, 999)}"
        
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": "Validation Test Wedding Dress",
            "stock_uom": "Nos",
            "is_rental_item": 1,
            "rental_rate_per_day": 500,
            "item_category": "Women's Wear"
        })
        
        item.insert()
        
        # Check automation worked
        checks = []
        checks.append(("✅", f"Item '{item_code}' created successfully"))
        
        # Verify automation
        item.reload()
        if item.item_group:
            checks.append(("✅", f"Item group auto-set to '{item.item_group}'"))
        else:
            checks.append(("⚠️", "Item group not auto-set"))
        
        if item.current_rental_status:
            checks.append(("✅", f"Rental status set to '{item.current_rental_status}'"))
        else:
            checks.append(("⚠️", "Rental status not set"))
        
        # Check service item creation
        service_item_code = f"{item_code}-RENTAL"
        if frappe.db.exists("Item", service_item_code):
            checks.append(("✅", "Service item auto-created"))
            frappe.delete_doc("Item", service_item_code)
        else:
            checks.append(("⚠️", "Service item not auto-created"))
        
        # Clean up
        try:
            frappe.delete_doc("Item", item_code, force=True)
            checks.append(("✅", "Test item cleaned up"))
        except:
            checks.append(("⚠️", "Could not clean up test item - may need manual cleanup"))
        
        return checks
        
    except Exception as e:
        return [("❌", f"Item creation failed: {str(e)}")]

def test_customer_creation():
    """Test creating a customer"""
    print("\n🔍 Testing Customer Creation...")
    
    try:
        customer_name = "Validation Test Customer"
        
        # Delete if exists
        if frappe.db.exists("Customer", customer_name):
            frappe.delete_doc("Customer", customer_name)
        
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual",
            "customer_group": "Individual",
            "territory": "India",
            "mobile_number": "9876543210"
        })
        
        customer.insert()
        
        checks = []
        checks.append(("✅", f"Customer '{customer_name}' created successfully"))
        
        # Check automation
        customer.reload()
        if customer.unique_customer_id:
            checks.append(("✅", f"Unique ID auto-generated: '{customer.unique_customer_id}'"))
        else:
            checks.append(("⚠️", "Unique ID not auto-generated"))
        
        # Clean up
        frappe.delete_doc("Customer", customer_name)
        checks.append(("✅", "Test customer cleaned up"))
        
        return checks
        
    except Exception as e:
        return [("❌", f"Customer creation failed: {str(e)}")]

def test_booking_creation():
    """Test creating a rental booking"""
    print("\n🔍 Testing Booking Creation...")
    
    try:
        # Create test customer first
        customer_name = "Booking Test Customer"
        if frappe.db.exists("Customer", customer_name):
            try:
                frappe.delete_doc("Customer", customer_name, force=True)
            except:
                import random
                customer_name = f"Booking Test Customer {random.randint(100, 999)}"
        
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual",
            "customer_group": "Individual", 
            "territory": "India",
            "mobile_number": "9876543211"  # Add required mobile number
        })
        customer.insert()
        
        # Create test item
        item_code = "BOOKING-TEST-ITEM-001"
        if frappe.db.exists("Item", item_code):
            try:
                frappe.delete_doc("Item", item_code, force=True)
            except:
                import random
                item_code = f"BOOKING-TEST-ITEM-{random.randint(100, 999)}"
        
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": "Booking Test Item",
            "stock_uom": "Nos",
            "is_rental_item": 1,
            "rental_rate_per_day": 300
        })
        item.insert()
        
        # Create booking
        booking = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": customer_name,
            "company": frappe.defaults.get_user_default("Company") or "Test Company",
            "is_rental_booking": 1,
            "function_date": add_days(today(), 30),
            "rental_duration_days": 5,
            "caution_deposit_amount": 1000,
            "items": [{
                "item_code": item_code,
                "qty": 1,
                "rate": 300
            }]
        })
        
        booking.insert()
        
        checks = []
        checks.append(("✅", f"Booking '{booking.name}' created successfully"))
        
        # Check automation
        booking.reload()
        if booking.booking_status:
            checks.append(("✅", f"Booking status set to '{booking.booking_status}'"))
        else:
            checks.append(("⚠️", "Booking status not set"))
        
        if booking.rental_start_date and booking.rental_end_date:
            checks.append(("✅", "Rental dates calculated"))
        else:
            checks.append(("⚠️", "Rental dates not calculated"))
        
        # Clean up
        try:
            frappe.delete_doc("Sales Invoice", booking.name, force=True)
            frappe.delete_doc("Item", item_code, force=True)
            frappe.delete_doc("Customer", customer_name, force=True)
            checks.append(("✅", "Test data cleaned up"))
        except Exception as cleanup_error:
            checks.append(("⚠️", f"Partial cleanup completed - some test data may remain: {str(cleanup_error)}"))
        
        return checks
        
    except Exception as e:
        return [("❌", f"Booking creation failed: {str(e)}")]

def run_quick_validation():
    """Run all quick validation tests"""
    print("=" * 70)
    print("RENTAL MANAGEMENT SYSTEM - QUICK VALIDATION")
    print("=" * 70)
    
    all_checks = []
    
    try:
        # Test basic setup
        basic_checks = validate_basic_setup()
        all_checks.extend(basic_checks)
        
        # Test item creation if basic setup is OK
        if any("app is installed" in check[1] and check[0] == "✅" for check in basic_checks):
            item_checks = test_item_creation()
            all_checks.extend(item_checks)
            
            customer_checks = test_customer_creation()
            all_checks.extend(customer_checks)
            
            booking_checks = test_booking_creation()
            all_checks.extend(booking_checks)
        
        # Print results
        print("\nVALIDATION RESULTS:")
        print("-" * 50)
        
        success_count = 0
        warning_count = 0
        error_count = 0
        
        for status, message in all_checks:
            print(f"{status} {message}")
            if status == "✅":
                success_count += 1
            elif status == "⚠️":
                warning_count += 1
            elif status == "❌":
                error_count += 1
        
        print("\n" + "=" * 50)
        print(f"SUMMARY: ✅ {success_count} Success | ⚠️ {warning_count} Warnings | ❌ {error_count} Errors")
        
        if error_count == 0:
            print("🎉 System validation passed! Ready for integration testing.")
        elif warning_count > 0 and error_count == 0:
            print("⚠️ System mostly functional with some warnings.")
        else:
            print("❌ System has errors that need to be fixed.")
        
        print("=" * 50)
        
        return error_count == 0
        
    except Exception as e:
        print(f"❌ Validation failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    frappe.init()
    frappe.connect()
    
    success = run_quick_validation()
    if not success:
        exit(1)
