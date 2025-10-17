import frappe

def create_item_group_custom_fields():
    """Create custom fields for Item Group doctype for portal functionality"""
    
    custom_fields = [
        {
            "doctype": "Item Group",
            "fieldname": "portal_settings_section",
            "label": "Portal Settings",
            "fieldtype": "Section Break",
            "insert_after": "description",
            "collapsible": 1
        },
        {
            "doctype": "Item Group",
            "fieldname": "portal_image",
            "label": "Portal Category Image",
            "fieldtype": "Attach Image",
            "insert_after": "portal_settings_section",
            "description": "Image to display in customer portal categories section"
        },
        {
            "doctype": "Item Group",
            "fieldname": "portal_icon",
            "label": "Portal Icon Class",
            "fieldtype": "Data",
            "insert_after": "portal_image",
            "description": "Font Awesome icon class (e.g., fa-gem, fa-dress, fa-star)"
        },
        {
            "doctype": "Item Group",
            "fieldname": "column_break_portal",
            "fieldtype": "Column Break",
            "insert_after": "portal_icon"
        },
        {
            "doctype": "Item Group",
            "fieldname": "show_in_portal",
            "label": "Show in Portal",
            "fieldtype": "Check",
            "default": 1,
            "insert_after": "column_break_portal",
            "description": "Display this category in customer portal"
        },
        {
            "doctype": "Item Group",
            "fieldname": "portal_display_order",
            "label": "Portal Display Order",
            "fieldtype": "Int",
            "default": 1,
            "insert_after": "show_in_portal",
            "description": "Order to display in portal (lower numbers first)"
        },
        {
            "doctype": "Item Group",
            "fieldname": "portal_description",
            "label": "Portal Description",
            "fieldtype": "Small Text",
            "insert_after": "portal_display_order",
            "description": "Short description for portal display"
        }
    ]
    
    for field in custom_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["doctype"], "fieldname": field["fieldname"]}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": field["doctype"], 
                "fieldname": field["fieldname"],
                "label": field.get("label"),
                "fieldtype": field["fieldtype"],
                "options": field.get("options"),
                "default": field.get("default"),
                "insert_after": field["insert_after"],
                "depends_on": field.get("depends_on"),
                "mandatory_depends_on": field.get("mandatory_depends_on"),
                "read_only": field.get("read_only", 0),
                "collapsible": field.get("collapsible", 0),
                "description": field.get("description", "")
            })
            custom_field.insert()
            
    frappe.db.commit()
    print("Item Group portal custom fields created successfully!")

def update_existing_item_groups():
    """Update existing Item Groups to show in portal by default"""
    try:
        # Get all non-group item groups (leaf nodes) that have rental items
        item_groups = frappe.db.sql("""
            SELECT DISTINCT ig.name, ig.item_group_name
            FROM `tabItem Group` ig
            JOIN `tabItem` i ON i.item_group = ig.name
            WHERE ig.is_group = 0
              AND i.is_rental_item = 1
              AND i.disabled = 0
        """, as_dict=True)
        
        for ig in item_groups:
            # Update to show in portal with default settings
            frappe.db.set_value("Item Group", ig.name, {
                "show_in_portal": 1,
                "portal_display_order": 1
            })
            print(f"  ✅ Updated {ig.item_group_name} for portal display")
        
        frappe.db.commit()
        print("✅ Existing Item Groups updated for portal!")
    except Exception as e:
        print(f"❌ Error updating Item Groups: {e}")
        frappe.log_error(f"Error updating Item Groups for portal: {str(e)}")

# Call this function during app installation
if __name__ == "__main__":
    create_item_group_custom_fields()
    update_existing_item_groups()