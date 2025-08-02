import frappe

def create_item_custom_fields():
    """Create custom fields for Item doctype"""
    
    custom_fields = [
        {
            "doctype": "Item",
            "fieldname": "rental_section",
            "label": "Rental Configuration",
            "fieldtype": "Section Break",
            "insert_after": "image",
            "collapsible": 1
        },
        {
            "doctype": "Item", 
            "fieldname": "is_rental_item",
            "label": "Enable for Rental",
            "fieldtype": "Check",
            "default": 0,
            "insert_after": "rental_section"
        },
        {
            "doctype": "Item",
            "fieldname": "rental_rate_per_day",
            "label": "Rental Rate (₹/day)",
            "fieldtype": "Currency", 
            "depends_on": "is_rental_item",
            "mandatory_depends_on": "is_rental_item",
            "insert_after": "is_rental_item"
        },
        # Note: Caution deposit removed from item level - will be manually added at invoice level
        {
            "doctype": "Item", 
            "fieldname": "rental_item_type",
            "label": "Item Category",
            "fieldtype": "Select",
            "options": "\nDress\nOrnament\nAccessory\nOther",
            "depends_on": "is_rental_item",
            "insert_after": "rental_rate_per_day"
        },
        {
            "doctype": "Item",
            "fieldname": "column_break_rental_1", 
            "fieldtype": "Column Break",
            "insert_after": "rental_item_type"
        },
        {
            "doctype": "Item",
            "fieldname": "current_rental_status",
            "label": "Current Status",
            "fieldtype": "Select",
            "options": "Available\nBooked\nOut for Rental\nUnder Dry Wash\nMaintenance",
            "default": "Available",
            "depends_on": "is_rental_item",
            "insert_after": "column_break_rental_1"
        },
        {
            "doctype": "Item",
            "fieldname": "approval_status", 
            "label": "Approval Status",
            "fieldtype": "Select", 
            "options": "Pending Approval\nApproved\nRejected",
            "default": "Pending Approval",
            "read_only": 1,
            "insert_after": "current_rental_status"
        },
        # Third Party Section
        {
            "doctype": "Item",
            "fieldname": "third_party_section",
            "label": "Third Party Owner Details", 
            "fieldtype": "Section Break",
            "depends_on": "is_rental_item",
            "collapsible": 1,
            "insert_after": "approval_status"
        },
        {
            "doctype": "Item",
            "fieldname": "is_third_party_item",
            "label": "Third Party Owned",
            "fieldtype": "Check",
            "depends_on": "is_rental_item",
            "insert_after": "third_party_section"
        },
        {
            "doctype": "Item", 
            "fieldname": "owner_commission_percent",
            "label": "Owner Commission %",
            "fieldtype": "Percent",
            "depends_on": "is_third_party_item",
            "default": 30,
            "insert_after": "is_third_party_item"
        },
        {
            "doctype": "Item",
            "fieldname": "third_party_supplier",
            "label": "Owner (Supplier)",
            "fieldtype": "Link", 
            "options": "Supplier",
            "depends_on": "is_third_party_item",
            "insert_after": "owner_commission_percent"
        }
    ]
    
    for field in custom_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["doctype"], "fieldname": field["fieldname"]}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": field["doctype"], 
                "fieldname": field["fieldname"],
                "label": field["label"],
                "fieldtype": field["fieldtype"],
                "options": field.get("options"),
                "default": field.get("default"),
                "insert_after": field["insert_after"],
                "depends_on": field.get("depends_on"),
                "mandatory_depends_on": field.get("mandatory_depends_on"),
                "read_only": field.get("read_only", 0),
                "collapsible": field.get("collapsible", 0)
            })
            custom_field.insert()
            
    frappe.db.commit()
    print("Item custom fields created successfully!")

# Call this function during app installation
if __name__ == "__main__":
    create_item_custom_fields()
