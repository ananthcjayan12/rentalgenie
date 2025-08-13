import frappe
from frappe.utils import now_datetime, getdate, add_days

def update_booking_status(invoice_name, new_status, update_time=None):
    """Update booking status and related item statuses"""
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    
    if not doc.is_rental_booking:
        frappe.throw("This is not a rental booking")
    
    old_status = doc.booking_status
    doc.booking_status = new_status
    
    # Update timestamps based on status
    if new_status == "Out for Rental" and not doc.actual_delivery_time:
        doc.actual_delivery_time = update_time or now_datetime()
    
    elif new_status == "Returned" and not doc.actual_return_time:
        doc.actual_return_time = update_time or now_datetime()
        # Process caution deposit refund
        handle_caution_deposit_refund(doc)
    
    elif new_status == "Completed":
        if not doc.actual_return_time:
            doc.actual_return_time = update_time or now_datetime()
        # Mark items as available
        update_item_rental_status(doc, "Available")
    
    doc.save()
    
    # Update item statuses
    if new_status in ["Out for Rental", "Returned", "Completed"]:
        item_status = "Out for Rental" if new_status == "Out for Rental" else "Available"
        update_item_rental_status(doc, item_status)
    
    frappe.msgprint(f"Booking status updated from {old_status} to {new_status}")

def handle_caution_deposit_refund(doc):
    """Handle caution deposit refund when booking is returned (before dry cleaning)"""
    if doc.caution_deposit_amount and not doc.caution_deposit_refunded:
        try:
            company_abbr = frappe.get_value("Company", doc.company, "abbr")
            caution_deposit_account = f"Caution Deposits Received - {company_abbr}"
            
            # Get default cash account
            cash_account = frappe.get_value("Company", doc.company, "default_cash_account")
            if not cash_account:
                cash_account = frappe.db.get_value("Account", 
                                                 {"account_type": "Cash", "company": doc.company}, 
                                                 "name")
            
            if not cash_account:
                frappe.msgprint("Cannot process refund: No cash account found", alert=True)
                return
            
            # Create refund journal entry
            je = frappe.get_doc({
                "doctype": "Journal Entry",
                "voucher_type": "Journal Entry",
                "posting_date": getdate(),
                "company": doc.company,
                "user_remark": f"Caution deposit refund for booking {doc.name}",
                "accounts": [
                    {
                        "account": caution_deposit_account,
                        "debit_in_account_currency": doc.caution_deposit_amount,
                        "credit_in_account_currency": 0,
                        "reference_type": "Sales Invoice",
                        "reference_name": doc.name
                    },
                    {
                        "account": cash_account,
                        "debit_in_account_currency": 0,
                        "credit_in_account_currency": doc.caution_deposit_amount,
                        "reference_type": "Sales Invoice",
                        "reference_name": doc.name
                    }
                ]
            })
            je.insert()
            je.submit()
            
            # Update refunded amount
            doc.caution_deposit_refunded = doc.caution_deposit_amount
            frappe.msgprint(f"Caution deposit of ₹{doc.caution_deposit_amount} refunded successfully")
            
        except Exception as e:
            frappe.log_error(f"Error processing caution deposit refund for {doc.name}: {str(e)}")
            frappe.msgprint(f"Error processing refund: {str(e)}", alert=True)

def update_item_rental_status(doc, status):
    """Update rental status of items in the booking"""
    for item in doc.items:
        # Check if item is a rental item
        item_doc = frappe.get_doc("Item", item.item_code)
        if item_doc.is_rental_item:
            frappe.db.set_value("Item", item.item_code, "current_rental_status", status)

def get_item_booking_calendar(item_code, months_ahead=6):
    """Get booking calendar for an item"""
    from frappe.utils import add_months, getdate
    
    end_date = add_months(getdate(), months_ahead)
    
    bookings = frappe.db.sql("""
        SELECT 
            si.name as booking_reference,
            si.customer,
            si.rental_start_date,
            si.rental_end_date,
            si.booking_status,
            si.function_date
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE sii.item_code = %s
        AND si.is_rental_booking = 1
        AND si.docstatus = 1
        AND si.booking_status NOT IN ('Cancelled', 'Completed')
        AND si.rental_start_date <= %s
        ORDER BY si.rental_start_date
    """, (item_code, end_date), as_dict=True)
    
    return bookings

def check_item_availability_for_period(item_code, start_date, end_date, exclude_booking=None):
    """Check if item is available for a specific period"""
    conditions = ["sii.item_code = %s", "si.is_rental_booking = 1", "si.docstatus = 1"]
    values = [item_code]
    
    conditions.append("si.booking_status NOT IN ('Cancelled', 'Completed', 'Exchanged')")
    
    if exclude_booking:
        conditions.append("si.name != %s")
        values.append(exclude_booking)
    
    conditions.append("""(
        (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR
        (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR
        (si.rental_start_date >= %s AND si.rental_end_date <= %s)
    )""")
    values.extend([start_date, start_date, end_date, end_date, start_date, end_date])
    
    conflicting_bookings = frappe.db.sql(f"""
        SELECT si.name, si.customer, si.rental_start_date, si.rental_end_date
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE {' AND '.join(conditions)}
    """, values, as_dict=True)
    
    return len(conflicting_bookings) == 0, conflicting_bookings

def get_rental_dashboard_data():
    """Get dashboard data for rental management"""
    
    # Current bookings summary
    booking_summary = frappe.db.sql("""
        SELECT 
            booking_status,
            COUNT(*) as count,
            SUM(grand_total) as total_amount
        FROM `tabSales Invoice`
        WHERE is_rental_booking = 1
        AND docstatus = 1
        GROUP BY booking_status
    """, as_dict=True)
    
    # Items currently out for rental
    items_out = frappe.db.sql("""
        SELECT COUNT(DISTINCT sii.item_code) as count
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE si.is_rental_booking = 1
        AND si.docstatus = 1
        AND si.booking_status = 'Out for Rental'
    """, as_dict=True)
    
    # Revenue this month
    monthly_revenue = frappe.db.sql("""
        SELECT SUM(grand_total) as revenue
        FROM `tabSales Invoice`
        WHERE is_rental_booking = 1
        AND docstatus = 1
        AND MONTH(posting_date) = MONTH(CURDATE())
        AND YEAR(posting_date) = YEAR(CURDATE())
    """, as_dict=True)
    
    return {
        "booking_summary": booking_summary,
        "items_out_count": items_out[0].count if items_out else 0,
        "monthly_revenue": monthly_revenue[0].revenue if monthly_revenue and monthly_revenue[0].revenue else 0
    }

def process_bulk_status_update(bookings, new_status):
    """Process bulk status updates for multiple bookings"""
    updated_count = 0
    errors = []
    
    for booking_name in bookings:
        try:
            update_booking_status(booking_name, new_status)
            updated_count += 1
        except Exception as e:
            errors.append(f"{booking_name}: {str(e)}")
    
    return {
        "updated_count": updated_count,
        "errors": errors
    }

# Add missing functions for rental_utils
def check_item_availability(item_code, start_date=None, end_date=None):
    """Check if a rental item is available - alias for get_item_availability_status"""
    from rental_management.utils.item_utils import get_item_availability_status
    return get_item_availability_status(item_code, start_date, end_date)

def get_booking_status_summary():
    """Get summary of booking statuses"""
    try:
        summary = frappe.db.sql("""
            SELECT 
                booking_status,
                COUNT(*) as count,
                SUM(grand_total) as total_amount
            FROM `tabSales Invoice`
            WHERE is_rental_booking = 1
            AND docstatus = 1
            GROUP BY booking_status
        """, as_dict=True)
        
        return summary
        
    except Exception as e:
        frappe.log_error(f"Error getting booking status summary: {str(e)}")
        return []

def get_dashboard_data():
    """Get dashboard data for rental management - alias for get_rental_dashboard_data in rental_utils"""
    from rental_management.utils.rental_utils import get_rental_dashboard_data
    return get_rental_dashboard_data()
