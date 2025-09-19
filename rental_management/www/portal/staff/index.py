import frappe
from frappe.utils import formatdate, get_datetime, flt
from rental_management.api.customer_portal import get_customer_active_bookings, get_booking_payment_summary

def get_context(context):
    """Get context for staff dashboard - booking management"""
    
    # Check if user has permission to access staff portal
    if not frappe.session.user or frappe.session.user == 'Guest':
        frappe.local.flags.redirect_location = '/login?redirect-to=/portal/staff'
        raise frappe.Redirect
    
    # Get parameters
    customer_id = frappe.form_dict.get('customer', '')
    booking_id = frappe.form_dict.get('booking', '')
    view = frappe.form_dict.get('view', 'dashboard')  # dashboard, customer, booking
    
    context.customer_id = customer_id
    context.booking_id = booking_id
    context.view = view
    context.customer = None
    context.bookings = []
    context.booking_summary = None
    context.dashboard_stats = {}
    context.recent_bookings = []
    context.pending_deliveries = []
    context.pending_returns = []
    
    try:
        if view == 'dashboard':
            return get_dashboard_context(context)
        elif view == 'customer' and customer_id:
            return get_customer_context(context, customer_id)
        elif view == 'booking' and booking_id:
            return get_booking_context(context, booking_id)
        else:
            return get_dashboard_context(context)
            
    except Exception as e:
        frappe.log_error(f"Error in staff dashboard context: {str(e)}")
        context.error_message = "Error loading dashboard data"
        return context

def get_dashboard_context(context):
    """Get dashboard overview with stats and recent activity"""
    
    # Get dashboard statistics
    stats = {}
    
    # Bookings awaiting advance collection
    stats['pending_advance'] = frappe.db.count('Sales Invoice', {
        'is_rental_booking': 1,
        'booking_status': 'Draft',
        'docstatus': 1
    })
    
    # Bookings awaiting delivery (advance collected, balance pending)
    stats['pending_delivery'] = frappe.db.count('Sales Invoice', {
        'is_rental_booking': 1,
        'booking_status': 'Advance Collected',
        'docstatus': 1
    })
    
    # Bookings awaiting return (items delivered)
    stats['pending_return'] = frappe.db.count('Sales Invoice', {
        'is_rental_booking': 1,
        'booking_status': 'Items Delivered',
        'docstatus': 1
    })
    
    # Total active bookings
    stats['total_active'] = frappe.db.count('Sales Invoice', {
        'is_rental_booking': 1,
        'booking_status': ['in', ['Draft', 'Advance Collected', 'Items Delivered']],
        'docstatus': 1
    })
    
    context.dashboard_stats = stats
    
    # Get recent bookings (last 10)
    recent_bookings = frappe.db.sql("""
        SELECT 
            si.name, si.posting_date, si.total, si.booking_status,
            si.customer_name, si.customer, si.advance_amount,
            si.balance_amount, si.caution_deposit_amount,
            COUNT(sii.name) as item_count
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE si.is_rental_booking = 1
        AND si.docstatus = 1
        GROUP BY si.name
        ORDER BY si.posting_date DESC
        LIMIT 10
    """, as_dict=True)
    
    context.recent_bookings = recent_bookings
    
    # Get pending deliveries (advance collected, balance pending)
    pending_deliveries = frappe.db.sql("""
        SELECT 
            si.name, si.posting_date, si.total, si.customer_name, 
            si.customer, si.advance_amount, si.balance_amount,
            si.caution_deposit_amount, MIN(sii.rental_start_date) as earliest_start
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE si.is_rental_booking = 1
        AND si.booking_status = 'Advance Collected'
        AND si.docstatus = 1
        GROUP BY si.name
        ORDER BY earliest_start ASC
    """, as_dict=True)
    
    context.pending_deliveries = pending_deliveries
    
    # Get pending returns (items delivered)
    pending_returns = frappe.db.sql("""
        SELECT 
            si.name, si.posting_date, si.total, si.customer_name,
            si.customer, si.caution_deposit_amount, 
            MAX(sii.rental_end_date) as latest_end
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE si.is_rental_booking = 1
        AND si.booking_status = 'Items Delivered'
        AND si.docstatus = 1
        GROUP BY si.name
        ORDER BY latest_end ASC
    """, as_dict=True)
    
    context.pending_returns = pending_returns
    
    # Page metadata
    context.page_title = "Staff Dashboard | Blush & Glow"
    context.meta_description = "Rental booking management dashboard for sales staff"
    
    return context

def get_customer_context(context, customer_id):
    """Get customer-specific booking management"""
    
    # Get customer details
    customer_data = frappe.db.get_value(
        "Customer",
        customer_id,
        ["name", "customer_name", "mobile_number", "email_id"],
        as_dict=True
    )
    if customer_data:
        context.customer = customer_data
        
        # Get customer's active bookings
        bookings_result = get_customer_active_bookings(customer_id)
        if bookings_result.get('success'):
            context.bookings = bookings_result.get('bookings', [])
            
    # Page metadata
    context.page_title = f"Customer Management - {context.customer.get('customer_name', '')} | Blush & Glow"
    context.meta_description = "Manage customer rental bookings"
    
    return context

def get_booking_context(context, booking_id):
    """Get detailed booking management"""
    
    # Get detailed booking summary
    summary_result = get_booking_payment_summary(booking_id)
    if summary_result.get('success'):
        context.booking_summary = summary_result.get('summary', {})
        
        # Get customer info from booking
        if context.booking_summary.get('customer'):
            customer_data = frappe.db.get_value(
                "Customer",
                context.booking_summary['customer'],
                ["name", "customer_name", "mobile_number", "email_id"],
                as_dict=True
            )
            context.customer = customer_data
    
    # Page metadata
    context.page_title = f"Booking Management - {booking_id} | Blush & Glow"
    context.meta_description = "Manage rental booking payments and status"
    
    return context
