#!/usr/bin/env python3

import frappe

def test_item_automation():
    """Test the item automation logic"""
    
    try:
        frappe.init(site="rental-app") 
        frappe.connect()
        
        print("🧪 Testing Item Automation Logic...")
        
        # Test 1: Check if custom fields exist
        print("\n1️⃣ Checking Custom Fields:")
        fields_to_check = [
            "is_rental_item",
            "rental_rate_per_day", 
            "rental_item_type",
            "is_third_party_item",
            "third_party_supplier",
            "owner_commission_percent"
        ]
        
        for field in fields_to_check:
            exists = frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": field})
            status = "✅ EXISTS" if exists else "❌ MISSING"
            print(f"  {field}: {status}")
        
        # Test 2: Check existing rental items
        print("\n2️⃣ Checking Existing Rental Items:")
        rental_items = frappe.db.sql("""
            SELECT name, item_name, is_rental_item, rental_item_type, 
                   is_third_party_item, third_party_supplier, owner_commission_percent
            FROM `tabItem` 
            WHERE is_rental_item = 1
            LIMIT 5
        """, as_dict=True)
        
        if rental_items:
            print(f"  Found {len(rental_items)} rental items:")
            for item in rental_items:
                print(f"    📦 {item.name}: {item.item_name}")
                print(f"       Category: {item.rental_item_type or 'Not Set'}")
                print(f"       Third Party: {'Yes' if item.is_third_party_item else 'No'}")
                if item.is_third_party_item:
                    print(f"       Supplier: {item.third_party_supplier or 'Not Set'}")
                    print(f"       Commission: {item.owner_commission_percent or 0}%")
                print()
        else:
            print("  No rental items found")
        
        # Test 3: Check suppliers
        print("\n3️⃣ Checking Auto-created Suppliers:")
        owner_suppliers = frappe.db.sql("""
            SELECT name, supplier_name, supplier_type 
            FROM `tabSupplier` 
            WHERE supplier_name LIKE 'Owner-%'
            LIMIT 5
        """, as_dict=True)
        
        if owner_suppliers:
            print(f"  Found {len(owner_suppliers)} auto-created suppliers:")
            for supplier in owner_suppliers:
                print(f"    👤 {supplier.name}: {supplier.supplier_name}")
        else:
            print("  No auto-created suppliers found")
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        frappe.destroy()

if __name__ == "__main__":
    test_item_automation()
