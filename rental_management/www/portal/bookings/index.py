import frappe
from frappe.utils import formatdate, get_datetime
from rental_management.api.customer_portal import get_customer_active_bookings, get_booking_payment_summary

def get_context(context):
    """Get context for bookings page - supports both customer portal and sales staff portal"""
    
    # Check if this is sales staff portal (customer parameter)
    customer_id = frappe.form_dict.get('customer', '')
    booking_id = frappe.form_dict.get('booking', '')
    
    if customer_id:
        # Sales staff portal - manage customer bookings
        return get_sales_staff_context(context, customer_id, booking_id)
    else:
        # Customer portal - original functionality
        return get_customer_portal_context(context)

def get_sales_staff_context(context, customer_id, booking_id):
    """Get context for sales staff booking management"""
    
    context.customer_id = customer_id
    context.booking_id = booking_id
    context.customer = None
    context.bookings = []
    context.booking_summary = None
    context.is_sales_staff = True
    
    try:
        if customer_id:
            # Get customer details
            customer_data = frappe.db.get_value(
                "Customer",
                customer_id,
                ["name", "customer_name", "mobile_number"],
                as_dict=True
            )
            if customer_data:
                context.customer = customer_data
                
                # Get customer's active bookings
                bookings_result = get_customer_active_bookings(customer_id)
                if bookings_result.get('success'):
                    context.bookings = bookings_result.get('bookings', [])
                    
        if booking_id:
            # Get detailed booking summary
            summary_result = get_booking_payment_summary(booking_id)
            if summary_result.get('success'):
                context.booking_summary = summary_result.get('summary', {})
                
        # Page metadata
        context.page_title = f"Booking Management - {context.customer.get('customer_name', '')} | Blush & Glow"
        context.meta_description = "Manage rental bookings and payments"
        
    except Exception as e:
        frappe.log_error(f"Error in sales staff booking context: {str(e)}")
        context.error_message = "Error loading booking data"
        
    return context

def get_customer_portal_context(context):
    """Get context for customer portal bookings - original functionality"""
    context.is_sales_staff = False
    
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
