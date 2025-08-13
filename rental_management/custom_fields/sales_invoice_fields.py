import frappe


def create_sales_invoice_custom_fields():
    """Create or update custom fields for Sales Invoice doctype for rental bookings"""

    # NOTE: In Frappe, depends_on/mandatory_depends_on must be valid expressions, e.g. "eval:doc.is_rental_booking"
    rental_depends = "eval:doc.is_rental_booking"
    exchange_depends = "eval:doc.is_exchange_booking"

    custom_fields = [
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_booking_section",
            "label": "Rental Booking Details",
            "fieldtype": "Section Break",
            "insert_after": "customer",
            "collapsible": 1,
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "is_rental_booking",
            "label": "Rental Booking",
            "fieldtype": "Check",
            "default": 0,
            "insert_after": "rental_booking_section",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "function_date",
            "label": "Function Date",
            "fieldtype": "Date",
            "depends_on": rental_depends,
            "mandatory_depends_on": rental_depends,
            "insert_after": "is_rental_booking",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_duration_days",
            "label": "Rental Duration (Days)",
            "fieldtype": "Int",
            "depends_on": rental_depends,
            "default": 6,
            "insert_after": "function_date",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "column_break_rental_1",
            "fieldtype": "Column Break",
            "insert_after": "rental_duration_days",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_start_date",
            "label": "Rental Start Date",
            "fieldtype": "Date",
            "depends_on": rental_depends,
            "read_only": 1,
            "insert_after": "column_break_rental_1",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_end_date",
            "label": "Rental End Date",
            "fieldtype": "Date",
            "depends_on": rental_depends,
            "read_only": 1,
            "insert_after": "rental_start_date",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "booking_status",
            "label": "Booking Status",
            "fieldtype": "Select",
            "options": "Draft\nConfirmed\nOut for Rental\nPartially Returned\nReturned\nCompleted\nCancelled\nExchanged",
            "depends_on": rental_depends,
            "default": "Draft",
            "insert_after": "rental_end_date",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_amounts_section",
            "label": "Rental Amounts",
            "fieldtype": "Section Break",
            "insert_after": "booking_status",
            "collapsible": 1,
            "depends_on": rental_depends,
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "caution_deposit_amount",
            "label": "Caution Deposit Amount",
            "fieldtype": "Currency",
            "depends_on": rental_depends,
            "insert_after": "rental_amounts_section",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "advance_amount",
            "label": "Advance Amount",
            "fieldtype": "Currency",
            "depends_on": rental_depends,
            "insert_after": "caution_deposit_amount",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "total_owner_commission",
            "label": "Total Owner Commission",
            "fieldtype": "Currency",
            "depends_on": rental_depends,
            "read_only": 1,
            "insert_after": "advance_amount",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "column_break_rental_2",
            "fieldtype": "Column Break",
            "insert_after": "total_owner_commission",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "balance_due_on_delivery",
            "label": "Balance Due on Delivery",
            "fieldtype": "Currency",
            "depends_on": rental_depends,
            "read_only": 1,
            "insert_after": "column_break_rental_2",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "caution_deposit_refunded",
            "label": "Caution Deposit Refunded",
            "fieldtype": "Currency",
            "depends_on": rental_depends,
            "read_only": 1,
            "default": 0,
            "insert_after": "balance_due_on_delivery",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "exchange_booking_section",
            "label": "Exchange Booking Details",
            "fieldtype": "Section Break",
            "insert_after": "caution_deposit_refunded",
            "collapsible": 1,
            "depends_on": rental_depends,
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "is_exchange_booking",
            "label": "Exchange Booking",
            "fieldtype": "Check",
            "depends_on": rental_depends,
            "default": 0,
            "insert_after": "exchange_booking_section",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "original_booking_reference",
            "label": "Original Booking Reference",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "depends_on": exchange_depends,
            "mandatory_depends_on": exchange_depends,
            "insert_after": "is_exchange_booking",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "exchange_reason",
            "label": "Exchange Reason",
            "fieldtype": "Text",
            "depends_on": exchange_depends,
            "insert_after": "original_booking_reference",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_timestamps_section",
            "label": "Delivery & Return Timing",
            "fieldtype": "Section Break",
            "insert_after": "exchange_reason",
            "collapsible": 1,
            "depends_on": rental_depends,
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "actual_delivery_time",
            "label": "Actual Delivery Time",
            "fieldtype": "Datetime",
            "depends_on": rental_depends,
            "read_only": 1,
            "insert_after": "rental_timestamps_section",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "delivery_notes",
            "label": "Delivery Notes",
            "fieldtype": "Small Text",
            "depends_on": rental_depends,
            "insert_after": "actual_delivery_time",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "actual_return_time",
            "label": "Actual Return Time",
            "fieldtype": "Datetime",
            "depends_on": rental_depends,
            "read_only": 1,
            "insert_after": "delivery_notes",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "return_notes",
            "label": "Return Notes",
            "fieldtype": "Small Text",
            "depends_on": rental_depends,
            "insert_after": "actual_return_time",
        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_notes",
            "label": "Rental Notes",
            "fieldtype": "Text",
            "depends_on": rental_depends,
            "insert_after": "return_notes",
        },
    ]

    for field in custom_fields:
        existing_name = frappe.db.get_value(
            "Custom Field", {"dt": field["doctype"], "fieldname": field["fieldname"]}, "name"
        )

        if not existing_name:
            custom_field = frappe.get_doc(
                {
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
                    "reqd": field.get("reqd", 0),
                }
            )
            custom_field.insert()
        else:
            # Update existing custom field to ensure visibility and correct defaults/options
            cf = frappe.get_doc("Custom Field", existing_name)
            updated = False

            # Properties we want to keep in sync (do not change fieldtype to avoid breaking migrations)
            props = [
                "label",
                "options",
                "default",
                "insert_after",
                "depends_on",
                "mandatory_depends_on",
                "read_only",
                "collapsible",
                "reqd",
            ]

            for prop in props:
                new_val = field.get(prop, 0 if prop in ["read_only", "collapsible", "reqd"] else None)
                if new_val is not None and getattr(cf, prop, None) != new_val:
                    cf.set(prop, new_val)
                    updated = True

            if updated:
                cf.save()

    frappe.db.commit()
    print("Sales Invoice custom fields created/updated successfully!")
