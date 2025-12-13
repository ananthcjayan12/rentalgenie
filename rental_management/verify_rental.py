
import frappe
from frappe.utils import add_days, nowdate, flt
from rental_management.automations.booking_automation import calculate_rental_amounts, create_owner_commission_liabilities

def verify():
    # 1. Setup Test Item with Fixed Commission
    item_code = "TEST-GOWN-FIXED"
    if not frappe.db.exists("Item", item_code):
        item = frappe.new_doc("Item")
        item.item_code = item_code
        item.item_name = "Test Gown Fixed Comm"
        item.item_group = "All Item Groups"
        item.is_rental_item = 1
        item.rental_rate_per_day = 10000
        
        # Third Party Details
        item.is_third_party_item = 1
        item.owner_commission_fixed = 4000
        
        # Create a dummy owner
        owner_name = "Test Owner A"
        if not frappe.db.exists("Third Party Owner", {"owner_name": owner_name}):
            owner = frappe.new_doc("Third Party Owner")
            owner.owner_name = owner_name
            owner.email = "owner@example.com"
            owner.insert(ignore_permissions=True)
            owner_name = owner.name
        else:
            owner_name = frappe.db.get_value("Third Party Owner", {"owner_name": owner_name}, "name")
            
        item.third_party_owner = owner_name
        item.purchase_cost = 5000
        item.insert(ignore_permissions=True)
    else:
        item = frappe.get_doc("Item", item_code)
        item.owner_commission_fixed = 4000
        item.save()

    print(f"Item {item_code} set up with Fixed Commission: {item.owner_commission_fixed}")

    # 2. Create Sales Invoice (Booking)
    si = frappe.new_doc("Sales Invoice")
    si.customer = frappe.db.get_value("Customer", {}, "name") or frappe.get_doc({"doctype": "Customer", "customer_name": "Test Cust"}).insert().name
    si.is_rental_booking = 1
    si.rental_duration_days = 3
    si.function_date = add_days(nowdate(), 5)
    
    # Add Item
    row = si.append("items", {})
    row.item_code = item_code
    row.qty = 1
    row.rate = 10000 * 3 # Total amount for line? No, usually rate is unit rate.
    # In Rental App, user input implies rate / day. But Sales Invoice usually expects Rate = Price.
    # Let's assume standard behavior: Rate = 30000 (Total price for 3 days).
    row.rate = 30000
    row.amount = 30000
    
    si.insert(ignore_permissions=True)
    
    # 3. Test Commission Calculation
    print("Running calculate_rental_amounts...")
    calculate_rental_amounts(si)
    
    # Expected: 4000 * 3 * 1 = 12000
    expected_commission = 12000.0
    actual = flt(si.total_owner_commission)
    
    print(f"Total Owner Commission: {actual}")
    if actual == expected_commission:
        print("PASS: Commission calculation matches expected fixed amount logic.")
    else:
        print(f"FAIL: Expected {expected_commission}, got {actual}")

    # 4. Test Print Format Generation
    print("Testing Rental Invoice Print Format...")
    try:
        html = frappe.get_print("Sales Invoice", si.name, "Rental Invoice")
        if "RENTAL INVOICE" in html and item_code in html:
             print("PASS: Print Format generated successfully with key content.")
        else:
             print("FAIL: Print Format generation missing content.")
    except Exception as e:
        print(f"FAIL: Print Format error: {e}")

    # Cleanup
    # frappe.delete_doc("Sales Invoice", si.name) # Keep it for inspection if needed

if __name__ == "__main__":
    verify()
