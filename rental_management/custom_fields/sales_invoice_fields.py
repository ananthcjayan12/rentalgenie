import frappe

def create_sales_invoice_custom_fields():
    """Create custom fields for Sales Invoice doctype for rental bookings"""
    #dsd
    custom_fields = [
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_booking_section",
            "label": "Rental Booking Details",
            "fieldtype": "Section Break",
            "insert_after": "customer",
            "collapsible": 1
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "is_rental_booking",
            "label": "Rental Booking",
            "fieldtype": "Check",
            "default": 0,
            "insert_after": "rental_booking_section"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "function_date",
            "label": "Function Date",
            "fieldtype": "Date",
            "depends_on": "is_rental_booking",
            "mandatory_depends_on": "is_rental_booking",
            "insert_after": "is_rental_booking"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_duration_days",
            "label": "Rental Duration (Days)",
            "fieldtype": "Int",
            "depends_on": "is_rental_booking",
            "default": 6,
            "insert_after": "function_date"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "column_break_rental_1",
            "fieldtype": "Column Break",
            "insert_after": "rental_duration_days"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_start_date",
            "label": "Rental Start Date",
            "fieldtype": "Date",
            "depends_on": "is_rental_booking",
            "read_only": 1,
            "insert_after": "column_break_rental_1"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_end_date",
            "label": "Rental End Date",
            "fieldtype": "Date",
            "depends_on": "is_rental_booking",
            "read_only": 1,
            "insert_after": "rental_start_date"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "booking_status",
            "label": "Booking Status",
            "fieldtype": "Select",
            "options": "\nDraft\nConfirmed\nOut for Rental\nPartially Returned\nReturned\nCompleted\nCancelled\nExchanged",
            "depends_on": "is_rental_booking",
            "default": "Draft",
            "insert_after": "rental_end_date"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_amounts_section",
            "label": "Rental Amounts",
            "fieldtype": "Section Break",
            "insert_after": "booking_status",
            "collapsible": 1,
            "depends_on": "is_rental_booking"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "caution_deposit_amount",
            "label": "Caution Deposit Amount",
            "fieldtype": "Currency",
            "depends_on": "is_rental_booking",
            "insert_after": "rental_amounts_section"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "advance_amount",
            "label": "Advance Amount",
            "fieldtype": "Currency",
            "depends_on": "is_rental_booking",
            "insert_after": "caution_deposit_amount"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "pending_payment_amount",
            "label": "Pending Payment Amount",
            "fieldtype": "Currency",
            "depends_on": "is_rental_booking",
            "read_only": 1,
            "insert_after": "advance_amount"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "column_break_rental_2",
            "fieldtype": "Column Break",
            "insert_after": "pending_payment_amount"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "balance_amount_collected",
            "label": "Balance Amount Collected",
            "fieldtype": "Currency",
            "depends_on": "is_rental_booking",
            "default": 0,
            "insert_after": "column_break_rental_2"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "caution_deposit_collected",
            "label": "Caution Deposit Collected",
            "fieldtype": "Currency",
            "depends_on": "is_rental_booking",
            "default": 0,
            "insert_after": "balance_amount_collected"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "balance_due_on_delivery",
            "label": "Balance Due on Delivery",
            "fieldtype": "Currency",
            "depends_on": "is_rental_booking",
            "read_only": 1,
            "insert_after": "caution_deposit_collected"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "caution_deposit_refunded",
            "label": "Caution Deposit Refunded",
            "fieldtype": "Currency",
            "depends_on": "is_rental_booking",
            "read_only": 1,
            "default": 0,
            "insert_after": "balance_due_on_delivery"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "caution_deposit_deduction",
            "label": "Caution Deposit Deduction",
            "fieldtype": "Currency",
            "depends_on": "is_rental_booking",
            "default": 0,
            "insert_after": "caution_deposit_refunded"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "deduction_reason",
            "label": "Deduction Reason",
            "fieldtype": "Text",
            "depends_on": "is_rental_booking",
            "insert_after": "caution_deposit_deduction"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "exchange_booking_section",
            "label": "Exchange Booking Details",
            "fieldtype": "Section Break",
            "insert_after": "deduction_reason",
            "collapsible": 1,
            "depends_on": "is_rental_booking"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "is_exchange_booking",
            "label": "Exchange Booking",
            "fieldtype": "Check",
            "depends_on": "is_rental_booking",
            "default": 0,
            "insert_after": "exchange_booking_section"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "original_booking_reference",
            "label": "Original Booking Reference",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "depends_on": "is_exchange_booking",
            "mandatory_depends_on": "is_exchange_booking",
            "insert_after": "is_exchange_booking"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "exchange_reason",
            "label": "Exchange Reason",
            "fieldtype": "Text",
            "depends_on": "is_exchange_booking",
            "insert_after": "original_booking_reference"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_timestamps_section",
            "label": "Rental Timestamps",
            "fieldtype": "Section Break",
            "insert_after": "exchange_reason",
            "collapsible": 1,
            "depends_on": "is_rental_booking"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "actual_delivery_time",
            "label": "Actual Delivery Time",
            "fieldtype": "Datetime",
            "depends_on": "is_rental_booking",
            "read_only": 1,
            "insert_after": "rental_timestamps_section"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "actual_return_time",
            "label": "Actual Return Time",
            "fieldtype": "Datetime",
            "depends_on": "is_rental_booking",
            "read_only": 1,
            "insert_after": "actual_delivery_time"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_notes",
            "label": "Rental Notes",
            "fieldtype": "Text",
            "depends_on": "is_rental_booking",
            "insert_after": "actual_return_time"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "delivery_notes",
            "label": "Delivery Notes",
            "fieldtype": "Text",
            "depends_on": "is_rental_booking",
            "insert_after": "rental_notes"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "return_notes",
            "label": "Return Notes",
            "fieldtype": "Text",
            "depends_on": "is_rental_booking",
            "insert_after": "delivery_notes"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "special_instructions",
            "label": "Special Instructions",
            "fieldtype": "Text",
            "depends_on": "is_rental_booking",
            "insert_after": "return_notes"
        },
        # Accounting Integration Fields
        {
            "doctype": "Sales Invoice",
            "fieldname": "accounting_entries_section",
            "label": "Accounting Entries",
            "fieldtype": "Section Break",
            "insert_after": "return_notes",
            "collapsible": 1,
            "depends_on": "is_rental_booking"
        },
        {
            "doctype": "Sales Invoice", 
            "fieldname": "total_rental_amount",
            "label": "Total Rental Amount",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "accounting_entries_section",
            "description": "Full rental amount (including advance)"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "advance_journal_entry",
            "label": "Advance Journal Entry",
            "fieldtype": "Link",
            "options": "Journal Entry",
            "read_only": 1,
            "insert_after": "total_rental_amount"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "balance_payment_entry",
            "label": "Balance Payment Entry", 
            "fieldtype": "Link",
            "options": "Payment Entry",
            "read_only": 1,
            "insert_after": "advance_journal_entry"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "column_break_accounting_1",
            "fieldtype": "Column Break",
            "insert_after": "balance_payment_entry"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "caution_deposit_journal_entry",
            "label": "Caution Deposit Journal Entry",
            "fieldtype": "Link",
            "options": "Journal Entry", 
            "read_only": 1,
            "insert_after": "column_break_accounting_1"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "commission_journal_entry",
            "label": "Commission Journal Entry",
            "fieldtype": "Link",
            "options": "Journal Entry",
            "read_only": 1,
            "insert_after": "caution_deposit_journal_entry"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "refund_journal_entry", 
            "label": "Refund Journal Entry",
            "fieldtype": "Link",
            "options": "Journal Entry",
            "read_only": 1,
            "insert_after": "commission_journal_entry"
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "owner_commission_amount",
            "label": "Owner Commission Amount",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "refund_journal_entry"
        },
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
    
    # Add custom field to Sales Invoice Item
    sales_invoice_item_fields = [
        {
            "doctype": "Sales Invoice Item",
            "fieldname": "full_rental_amount",
            "label": "Full Rental Amount",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "amount",
            "description": "Complete rental amount (before advance adjustment)"
        }
    ]
    
    for field in sales_invoice_item_fields:
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
                "read_only": field.get("read_only", 0),
                "description": field.get("description", "")
            })
            custom_field.insert()
    
    frappe.db.commit()
    print("Sales Invoice custom fields created successfully!")
