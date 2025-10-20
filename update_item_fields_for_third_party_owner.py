#!/usr/bin/env python3

import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def reinstall_item_fields():
    """Reinstall Item custom fields with updated Third Party Owner configuration"""
    
    try:
        import frappe
        frappe.connect()
        
        from rental_management.custom_fields.item_fields import create_item_custom_fields
        
        print("🔄 Reinstalling Item custom fields with Third Party Owner integration...")
        
        # Fields to remove (old supplier-based fields)
        fields_to_remove = [
            "third_party_supplier"
        ]
        
        print("📭 Removing old custom fields...")
        for field_name in fields_to_remove:
            try:
                if frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": field_name}):
                    frappe.delete_doc("Custom Field", frappe.get_value("Custom Field", 
                        {"dt": "Item", "fieldname": field_name}, "name"))
                    print(f"   ❌ Removed field: {field_name}")
            except Exception as e:
                print(f"   ⚠️  Error removing {field_name}: {str(e)}")
        
        # Create new fields
        print("📦 Creating new custom fields...")
        create_item_custom_fields()
        
        print("✅ Item custom fields reinstalled successfully!")
        print("🎯 Updated fields:")
        print("   - third_party_owner (Link to Third Party Owner)")
        print("   - owner_supplier_source (Link to original Supplier)")
        
    except Exception as e:
        print(f"❌ Error reinstalling custom fields: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reinstall_item_fields()
