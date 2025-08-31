import frappe
from frappe.utils import formatdate, get_datetime

def get_context(context):
    """Get context for bookings page"""
    
    try:
        # Check if user is logged in
        if not frappe.session.user or frappe.session.user == 'Guest':
            frappe.local.flags.redirect_location = '/login?redirect-to=/portal/bookings'
            raise frappe.Redirect
            
        # Get customer bookings
        customer_email = frappe.session.user
        customer = frappe.db.get_value("Customer", {"email_id": customer_email}, "name")
        
        if not customer:
            context.bookings = []
            context.error_message = "No customer profile found. Please contact support."
            return context
            
        # Get all bookings for this customer
        bookings = frappe.db.sql("""
            SELECT 
                si.name, si.posting_date, si.total, si.booking_status,
                si.customer_name, si.due_date,
                COUNT(sii.name) as item_count,
                MIN(sii.rental_start_date) as earliest_rental_date,
                MAX(sii.rental_end_date) as latest_rental_date
            FROM `tabSales Invoice` si
            LEFT JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
            WHERE si.customer = %s 
            AND si.is_rental_booking = 1
            AND si.docstatus = 1
            GROUP BY si.name
            ORDER BY si.posting_date DESC
        """, (customer,), as_dict=True)
        
        # Format booking data
        formatted_bookings = []
        for booking in bookings:
            # Get first item image for display
            first_item = frappe.db.sql("""
                SELECT sii.item_code, sii.item_name, i.image
                FROM `tabSales Invoice Item` sii
                LEFT JOIN `tabItem` i ON sii.item_code = i.item_code
                WHERE sii.parent = %s
                LIMIT 1
            """, (booking.name,), as_dict=True)
            
            formatted_bookings.append({
                'name': booking.name,
                'posting_date': formatdate(booking.posting_date),
                'total': booking.total,
                'status': booking.booking_status or 'Confirmed',
                'item_count': booking.item_count,
                'earliest_rental_date': formatdate(booking.earliest_rental_date) if booking.earliest_rental_date else None,
                'latest_rental_date': formatdate(booking.latest_rental_date) if booking.latest_rental_date else None,
                'first_item_image': first_item[0].image if first_item and first_item[0].image else None,
                'first_item_name': first_item[0].item_name if first_item else 'No items'
            })
        
        context.bookings = formatted_bookings
        context.customer_name = frappe.db.get_value("Customer", customer, "customer_name")
        
        # Page metadata
        context.page_title = "My Bookings | Blush & Glow"
        context.meta_description = "View and manage your rental bookings."
        
        return context
        
    except frappe.Redirect:
        raise
    except Exception as e:
        frappe.log_error(f"Error loading bookings page: {str(e)}")
        context.bookings = []
        context.error_message = "Unable to load bookings. Please try again later."
        return context
