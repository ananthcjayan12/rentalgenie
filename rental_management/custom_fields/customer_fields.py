import frappe

def create_customer_custom_fields():
    """Create custom fields for Customer doctype"""
    
    custom_fields = [
        {
            "doctype": "Customer",
            "fieldname": "customer_management_section",
            "label": "Customer Management",
            "fieldtype": "Section Break",
            "insert_after": "mobile_no",
            "collapsible": 1
        },
        {
            "doctype": "Customer",
            "fieldname": "unique_customer_id",
            "label": "Unique Customer ID",
            "fieldtype": "Data",
            "read_only": 1,
            "insert_after": "customer_management_section"
        },
        {
            "doctype": "Customer",
            "fieldname": "mobile_number",
            "label": "Mobile Number",
            "fieldtype": "Data",
            "reqd": 1,
            "insert_after": "unique_customer_id"
        },
        {
            "doctype": "Customer",
            "fieldname": "column_break_customer_1",
            "fieldtype": "Column Break",
            "insert_after": "mobile_number"
        },
        {
            "doctype": "Customer",
            "fieldname": "total_bookings",
            "label": "Total Bookings",
            "fieldtype": "Int",
            "read_only": 1,
            "default": 0,
            "insert_after": "column_break_customer_1"
        },
        {
            "doctype": "Customer",
            "fieldname": "last_booking_date",
            "label": "Last Booking Date",
            "fieldtype": "Date",
            "read_only": 1,
            "insert_after": "total_bookings"
        },
        {
            "doctype": "Customer",
            "fieldname": "total_rental_amount",
            "label": "Total Rental Amount",
            "fieldtype": "Currency",
            "read_only": 1,
            "default": 0,
            "insert_after": "last_booking_date"
        },
        {
            "doctype": "Customer",
            "fieldname": "customer_notes_section",
            "label": "Customer Notes",
            "fieldtype": "Section Break",
            "insert_after": "total_rental_amount",
            "collapsible": 1
        },
        {
            "doctype": "Customer",
            "fieldname": "customer_preferences",
            "label": "Customer Preferences",
            "fieldtype": "Text",
            "insert_after": "customer_notes_section"
        },
        {
            "doctype": "Customer",
            "fieldname": "special_instructions",
            "label": "Special Instructions",
            "fieldtype": "Text",
            "insert_after": "customer_preferences"
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
                "reqd": field.get("reqd", 0)
            })
            custom_field.insert()
    
    frappe.db.commit()
    print("Customer custom fields created successfully!")

# Call this function during app installation
if __name__ == "__main__":
    create_customer_custom_fields()
