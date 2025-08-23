#!/usr/bin/env python3

import frappe
from rental_management.setup.install import install_app

def reinstall_item_fields():
    """Reinstall custom fields to fix any duplicate/label issues"""
    
    print("🔄 Reinstalling custom fields...")
    
    try:
        # Connect to Frappe
        frappe.init(site="rental-app")
        frappe.connect()
        
        # Remove existing custom fields for Item (if any issues)
        existing_fields = [
            "rental_section",
            "is_rental_item", 
            "rental_rate_per_day",
            "rental_item_type",
            "column_break_rental_1",
            "current_rental_status",
            "approval_status",
            "third_party_section",
            "is_third_party_item",
            "owner_commission_percent",
            "third_party_supplier"
        ]
        
        for fieldname in existing_fields:
            if frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": fieldname}):
                try:
                    custom_field = frappe.get_doc("Custom Field", {"dt": "Item", "fieldname": fieldname})
                    custom_field.delete()
                    print(f"  ✅ Removed existing field: {fieldname}")
                except:
                    print(f"  ⚠️ Could not remove field: {fieldname}")
        
        frappe.db.commit()
        
        # Reinstall with updated fields
        install_app()
        
        print("✅ Custom fields reinstalled successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        frappe.destroy()

if __name__ == "__main__":
    reinstall_item_fields()
