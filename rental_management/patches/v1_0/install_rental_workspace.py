"""
Install Rental Management Workspace
"""

import frappe
from frappe.model.sync import sync_for

def execute():
    """Force install the Rental Management workspace"""
    try:
        # Force sync workspace
        sync_for("rental_management", force=True)
        
        # Ensure workspace is enabled
        if frappe.db.exists("Workspace", "Rental Management"):
            frappe.db.set_value("Workspace", "Rental Management", "is_hidden", 0)
            frappe.db.set_value("Workspace", "Rental Management", "public", 1)
            print("✅ Rental Management workspace updated")
        else:
            print("❌ Rental Management workspace not found after sync")
            
        frappe.db.commit()
        
    except Exception as e:
        print(f"❌ Error installing workspace: {e}")
        frappe.log_error(f"Workspace installation error: {str(e)}")