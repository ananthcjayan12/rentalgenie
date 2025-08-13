"""
Rental Management System - Clean Reinstall Script
Remove all existing custom fields and data, then reinstall fresh
"""

import frappe

def remove_all_custom_fields():
    """Remove all rental management custom fields"""
    print("🧹 Removing existing custom fields...")
    
    # Remove Item custom fields
    item_fields = frappe.db.get_list("Custom Field", 
                                   filters={"dt": "Item"},
                                   fields=["name", "fieldname"])
    
    rental_item_fields = [f for f in item_fields if any(keyword in f['fieldname'].lower() 
                         for keyword in ['rental', 'third_party', 'commission', 'category', 'approval', 'unique'])]
    
    for field in rental_item_fields:
        frappe.delete_doc("Custom Field", field['name'])
        print(f"   ✅ Removed Item field: {field['fieldname']}")
    
    # Remove Customer custom fields
    customer_fields = frappe.db.get_list("Custom Field", 
                                        filters={"dt": "Customer"},
                                        fields=["name", "fieldname"])
    
    rental_customer_fields = [f for f in customer_fields if any(keyword in f['fieldname'].lower() 
                             for keyword in ['rental', 'unique', 'booking', 'mobile'])]
    
    for field in rental_customer_fields:
        frappe.delete_doc("Custom Field", field['name'])
        print(f"   ✅ Removed Customer field: {field['fieldname']}")
    
    # Remove Sales Invoice custom fields
    invoice_fields = frappe.db.get_list("Custom Field", 
                                      filters={"dt": "Sales Invoice"},
                                      fields=["name", "fieldname"])
    
    rental_invoice_fields = [f for f in invoice_fields if any(keyword in f['fieldname'].lower() 
                            for keyword in ['rental', 'booking', 'function', 'caution', 'exchange', 'commission'])]
    
    for field in rental_invoice_fields:
        frappe.delete_doc("Custom Field", field['name'])
        print(f"   ✅ Removed Sales Invoice field: {field['fieldname']}")

def cleanup_test_data():
    """Clean up all test data"""
    print("🧹 Cleaning up test data...")
    
    # Remove test customers
    test_customers = frappe.db.get_list("Customer", 
                                      filters=[["customer_name", "like", "%test%"]],
                                      pluck="name")
    
    for customer in test_customers:
        try:
            frappe.delete_doc("Customer", customer, force=True)
            print(f"   ✅ Removed test customer: {customer}")
        except Exception as e:
            print(f"   ⚠️  Could not remove customer {customer}: {e}")
    
    # Remove test items
    test_items = frappe.db.get_list("Item", 
                                  filters=[["item_code", "like", "%test%"]],
                                  pluck="name")
    
    for item in test_items:
        try:
            frappe.delete_doc("Item", item, force=True)
            print(f"   ✅ Removed test item: {item}")
        except Exception as e:
            print(f"   ⚠️  Could not remove item {item}: {e}")
    
    # Remove test invoices
    test_invoices = frappe.db.get_list("Sales Invoice", 
                                     filters={"is_rental_booking": 1},
                                     pluck="name")
    
    for invoice in test_invoices[:5]:  # Limit to first 5 to avoid too many deletions
        try:
            doc = frappe.get_doc("Sales Invoice", invoice)
            if doc.docstatus == 1:
                doc.cancel()
            frappe.delete_doc("Sales Invoice", invoice, force=True)
            print(f"   ✅ Removed test invoice: {invoice}")
        except Exception as e:
            print(f"   ⚠️  Could not remove invoice {invoice}: {e}")

def fresh_install():
    """Run fresh installation"""
    print("🔧 Running fresh installation...")
    
    # Import and run installation
    from rental_management.setup.install import after_install
    after_install()

def run_clean_reinstall():
    """Run complete clean reinstall"""
    print("=" * 70)
    print("🔄 RUNNING CLEAN REINSTALL OF RENTAL MANAGEMENT SYSTEM")
    print("=" * 70)
    
    try:
        # Step 1: Clean up test data first
        cleanup_test_data()
        
        # Step 2: Remove existing custom fields
        remove_all_custom_fields()
        
        # Step 3: Commit deletions
        frappe.db.commit()
        
        # Step 4: Fresh install
        fresh_install()
        
        # Step 5: Final commit
        frappe.db.commit()
        
        print("\n" + "="*50)
        print("🎉 CLEAN REINSTALL COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("📝 Next steps:")
        print("   1. Run diagnostics: bench execute rental_management.comprehensive_diagnostics.run_comprehensive_diagnostics")
        print("   2. Run validation: bench execute rental_management.quick_validation.run_quick_validation")
        print("   3. Run integration tests: bench execute rental_management.tests.test_integration.run_integration_tests")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Clean reinstall failed: {e}")
        frappe.db.rollback()
        raise

if __name__ == "__main__":
    frappe.init()
    frappe.connect()
    
    run_clean_reinstall()
