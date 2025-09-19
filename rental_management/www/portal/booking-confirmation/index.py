import frappe
from frappe.utils import formatdate

def get_context(context):
    """Get context for booking confirmation page"""
    
    # Accept both 'booking' and 'invoice' parameters for compatibility
    booking_id = frappe.form_dict.get('booking') or frappe.form_dict.get('invoice')
    if not booking_id:
        frappe.throw("Booking ID not specified")
    
    try:
        # Get booking details
        booking = frappe.get_doc("Sales Invoice", booking_id)
        
        # Verify access to this booking 
        # For sales staff portal, we allow broader access
        if frappe.form_dict.get('customer_id'):
            # Sales staff accessing for specific customer
            customer_id = frappe.form_dict.get('customer_id')
            if booking.customer != customer_id:
                frappe.throw("Unauthorized access to booking")
        elif frappe.session.user != 'Guest':
            # Check if current user is linked to a customer
            customer_email = frappe.session.user
            customer = frappe.db.get_value("Customer", {"email_id": customer_email}, "name")
            
            print(f"Debug: customer_email={customer_email}, customer={customer}, booking.customer={booking.customer}")
            
            # If user has a customer record, verify they own this booking
            if customer and booking.customer != customer:
                frappe.throw("Unauthorized access to booking")
            # If no customer record, allow access (sales staff or admin user)
        # For Guest users and users without customer records, allow access
            
        context.booking = booking
        context.booking_items = booking.items
        
        # Calculate rental summary - use booking-level dates
        if hasattr(booking, 'rental_end_date') and hasattr(booking, 'rental_start_date') and booking.rental_end_date and booking.rental_start_date:
            context.total_rental_days = (frappe.utils.getdate(booking.rental_end_date) - frappe.utils.getdate(booking.rental_start_date)).days + 1
        elif hasattr(booking, 'rental_duration_days') and booking.rental_duration_days:
            context.total_rental_days = booking.rental_duration_days
        else:
            context.total_rental_days = 1  # Default to 1 day
        
        # Format dates for display - use booking-level dates for all items
        context.formatted_dates = []
        for item in booking.items:
            context.formatted_dates.append({
                'item_name': item.item_name,
                'function_date': formatdate(getattr(booking, 'function_date', None)) if getattr(booking, 'function_date', None) else 'Not set',
                'rental_start': formatdate(getattr(booking, 'rental_start_date', None)) if getattr(booking, 'rental_start_date', None) else 'Not set',
                'rental_end': formatdate(getattr(booking, 'rental_end_date', None)) if getattr(booking, 'rental_end_date', None) else 'Not set'
            })
        
        # Get customer address
        if booking.customer_address:
            context.delivery_address = frappe.get_doc("Address", booking.customer_address)
        else:
            context.delivery_address = None
            
        # Page metadata
        context.page_title = f"Booking Confirmation - {booking.name} | Blush & Glow"
        context.meta_description = f"Your rental booking {booking.name} has been confirmed successfully."
        
        return context
        
    except Exception as e:
        print(f"Error loading booking confirmation for {booking_id}: {str(e)}")
        frappe.throw("Booking not found or access denied")
