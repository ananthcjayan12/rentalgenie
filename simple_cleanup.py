"""
Simple cleanup script to remove conflicting test data
"""

import frappe

def cleanup_conflicting_data():
    """Remove conflicting test data"""
    print("🧹 Cleaning up conflicting test data...")
    
    # Remove the specific customer causing mobile number conflict
    conflicting_customer = "Validation Test Customer"
    if frappe.db.exists("Customer", conflicting_customer):
        try:
            frappe.delete_doc("Customer", conflicting_customer, force=True)
            print(f"✅ Removed conflicting customer: {conflicting_customer}")
        except Exception as e:
            print(f"⚠️  Could not remove {conflicting_customer}: {e}")
    
    # Remove any other test customers
    test_customers = frappe.db.get_list("Customer", 
                                      filters=[["customer_name", "like", "%test%"]],
                                      pluck="name")
    
    for customer in test_customers:
        try:
            frappe.delete_doc("Customer", customer, force=True)
            print(f"✅ Removed test customer: {customer}")
        except Exception as e:
            print(f"⚠️  Could not remove {customer}: {e}")
    
    # Remove test items
    test_items = frappe.db.get_list("Item", 
                                  filters=[["item_code", "like", "%TEST%"]],
                                  pluck="name")
    
    for item in test_items[:5]:  # Limit to first 5
        try:
            frappe.delete_doc("Item", item, force=True)
            print(f"✅ Removed test item: {item}")
        except Exception as e:
            print(f"⚠️  Could not remove {item}: {e}")
    
    frappe.db.commit()
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    frappe.init()
    frappe.connect()
    
    cleanup_conflicting_data()
