"""
System Fix Script - Rental Management System
Fix all identified issues from comprehensive diagnostics
"""

import frappe

def fix_missing_custom_fields():
    """Fix missing custom fields based on diagnostic results"""
    print("🔧 Fixing missing custom fields...")
    
    # Fix Item custom fields
    item_fixes = [
        {
            "fieldname": "item_category",
            "label": "Item Category",
            "fieldtype": "Select",
            "options": "\nWomen's Wear\nMen's Wear\nAccessories\nJewelry\nFootwear\nOthers",
            "insert_after": "rental_rate_per_day",
            "in_list_view": 1
        },
        {
            "fieldname": "supplier_for_third_party",
            "label": "Third Party Supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "insert_after": "owner_commission_percent",
            "depends_on": "is_third_party_item"
        }
    ]
    
    for field in item_fixes:
        if not frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": field["fieldname"]}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Item",
                **field
            })
            custom_field.insert()
            print(f"   ✅ Created Item field: {field['fieldname']}")
    
    # Fix Customer custom fields
    customer_fixes = [
        {
            "fieldname": "customer_unique_id",
            "label": "Unique Customer ID",
            "fieldtype": "Data",
            "read_only": 1,
            "insert_after": "customer_name",
            "in_list_view": 1
        }
    ]
    
    for field in customer_fixes:
        if not frappe.db.exists("Custom Field", {"dt": "Customer", "fieldname": field["fieldname"]}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                **field
            })
            custom_field.insert()
            print(f"   ✅ Created Customer field: {field['fieldname']}")
    
    # Fix Sales Invoice custom fields
    invoice_fixes = [
        {
            "fieldname": "total_owner_commission",
            "label": "Total Owner Commission",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "caution_deposit_refunded"
        },
        {
            "fieldname": "commission_paid_to_owners",
            "label": "Commission Paid to Owners",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "total_owner_commission"
        },
        {
            "fieldname": "exchange_booking",
            "label": "Exchange Booking",
            "fieldtype": "Check",
            "insert_after": "commission_paid_to_owners"
        },
        {
            "fieldname": "exchange_amount_adjustment",
            "label": "Exchange Amount Adjustment",
            "fieldtype": "Currency",
            "insert_after": "original_booking_reference",
            "depends_on": "exchange_booking"
        },
        {
            "fieldname": "exchange_notes",
            "label": "Exchange Notes",
            "fieldtype": "Text",
            "insert_after": "exchange_amount_adjustment",
            "depends_on": "exchange_booking"
        },
        {
            "fieldname": "delivery_notes",
            "label": "Delivery Notes",
            "fieldtype": "Text",
            "insert_after": "actual_delivery_time"
        },
        {
            "fieldname": "return_notes",
            "label": "Return Notes",
            "fieldtype": "Text",
            "insert_after": "actual_return_time"
        }
    ]
    
    for field in invoice_fixes:
        if not frappe.db.exists("Custom Field", {"dt": "Sales Invoice", "fieldname": field["fieldname"]}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Sales Invoice",
                **field
            })
            custom_field.insert()
            print(f"   ✅ Created Sales Invoice field: {field['fieldname']}")

def fix_missing_item_groups():
    """Create missing item groups"""
    print("🔧 Fixing missing item groups...")
    
    required_groups = [
        "Women's Wear",
        "Men's Wear", 
        "Jewelry",
        "Footwear"
    ]
    
    for group_name in required_groups:
        if not frappe.db.exists("Item Group", group_name):
            item_group = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": group_name,
                "parent_item_group": "All Item Groups",
                "is_group": 0
            })
            item_group.insert()
            print(f"   ✅ Created Item Group: {group_name}")

def fix_validation_script_issues():
    """Fix validation script field name mismatches"""
    print("🔧 Fixing validation script issues...")
    
    # Update quick_validation.py to use correct field names
    validation_file = "/Users/ananthu/Desktop/new_repos/rentalgenie/quick_validation.py"
    
    # The field is 'owner_commission_percent' not 'owner_commission_percentage'
    # The field is 'unique_customer_id' not 'customer_unique_id'
    
    print("   ⚠️  Please update validation script field names:")
    print("      - Change 'owner_commission_percentage' to 'owner_commission_percent'")  
    print("      - Change 'customer_unique_id' to 'unique_customer_id'")

def cleanup_test_data():
    """Clean up test data that's causing conflicts"""
    print("🔧 Cleaning up conflicting test data...")
    
    # Remove test customer with conflicting mobile
    test_customers = frappe.db.get_list("Customer", 
                                      filters={"customer_name": ["like", "%Test%"]},
                                      pluck="name")
    
    for customer in test_customers:
        try:
            frappe.delete_doc("Customer", customer, force=True)
            print(f"   ✅ Removed test customer: {customer}")
        except Exception as e:
            print(f"   ⚠️  Could not remove {customer}: {e}")
    
    # Remove test items
    test_items = frappe.db.get_list("Item",
                                  filters={"item_code": ["like", "%TEST%"]}, 
                                  pluck="name")
    
    for item in test_items:
        try:
            frappe.delete_doc("Item", item, force=True)
            print(f"   ✅ Removed test item: {item}")
        except Exception as e:
            print(f"   ⚠️  Could not remove {item}: {e}")

def test_item_creation_with_fixes():
    """Test item creation after fixes"""
    print("🧪 Testing item creation with fixes...")
    
    try:
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": "FIX-TEST-DRESS-001",
            "item_name": "Fix Test Wedding Dress",
            "stock_uom": "Nos",
            "item_group": "Women's Wear",  # Now specify the group explicitly
            "is_rental_item": 1,
            "rental_rate_per_day": 500,
            "item_category": "Women's Wear"
        })
        
        item.insert()
        print(f"   ✅ Item created successfully: {item.name}")
        
        # Test automation
        item.reload()
        print(f"   ✅ Current rental status: {item.current_rental_status}")
        print(f"   ✅ Approval status: {item.approval_status}")
        
        # Clean up
        frappe.delete_doc("Item", item.name)
        print(f"   ✅ Test item cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Item creation still failing: {e}")
        return False

def test_customer_creation_with_fixes():
    """Test customer creation after fixes"""
    print("🧪 Testing customer creation with fixes...")
    
    try:
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Fix Test Customer",
            "customer_type": "Individual",
            "customer_group": "Individual",
            "territory": "India",
            "mobile_number": "9876543299"  # Different number
        })
        
        customer.insert()
        print(f"   ✅ Customer created successfully: {customer.name}")
        
        # Test automation
        customer.reload()
        print(f"   ✅ Unique ID generated: {customer.unique_customer_id}")
        
        # Clean up
        frappe.delete_doc("Customer", customer.name)
        print(f"   ✅ Test customer cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Customer creation still failing: {e}")
        return False

def run_comprehensive_fix():
    """Run all fixes"""
    print("=" * 70)
    print("🔧 RUNNING COMPREHENSIVE SYSTEM FIX")
    print("=" * 70)
    
    try:
        # Step 1: Clean up conflicting data
        cleanup_test_data()
        
        # Step 2: Create missing custom fields
        fix_missing_custom_fields()
        
        # Step 3: Create missing item groups
        fix_missing_item_groups()
        
        # Step 4: Test fixes
        print("\n🧪 Testing fixes...")
        item_test = test_item_creation_with_fixes()
        customer_test = test_customer_creation_with_fixes()
        
        # Step 5: Commit changes
        frappe.db.commit()
        
        print("\n" + "=" * 50)
        print("📊 FIX SUMMARY")
        print("=" * 50)
        print(f"✅ Custom fields: Fixed")
        print(f"✅ Item groups: Fixed") 
        print(f"✅ Test data cleanup: Done")
        print(f"{'✅' if item_test else '❌'} Item creation test: {'Passed' if item_test else 'Failed'}")
        print(f"{'✅' if customer_test else '❌'} Customer creation test: {'Passed' if customer_test else 'Failed'}")
        
        if item_test and customer_test:
            print("\n🎉 System fixes completed successfully!")
            print("📝 Next steps:")
            print("   1. Update validation script field names")
            print("   2. Run diagnostics again to verify")
            print("   3. Run integration tests")
        else:
            print("\n⚠️  Some issues remain. Check error messages above.")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Fix process failed: {e}")
        frappe.db.rollback()

if __name__ == "__main__":
    frappe.init()
    frappe.connect()
    
    run_comprehensive_fix()
