import frappe
from frappe.utils import formatdate

def get_context(context):
    """Get context for booking confirmation page"""
    
    booking_id = frappe.form_dict.get('booking')
    if not booking_id:
        frappe.throw("Booking ID not specified")
    
    try:
        # Get booking details
        booking = frappe.get_doc("Sales Invoice", booking_id)
        
        # Verify this booking belongs to current user
        if frappe.session.user == 'Guest':
            frappe.throw("Please login to view booking details")
            
        customer_email = frappe.session.user
        customer = frappe.db.get_value("Customer", {"email_id": customer_email}, "name")
        
        if booking.customer != customer:
            frappe.throw("Unauthorized access to booking")
            
        context.booking = booking
        context.booking_items = booking.items
        
        # Calculate rental summary
        context.total_rental_days = sum(
            (frappe.utils.getdate(item.rental_end_date) - 
             frappe.utils.getdate(item.rental_start_date)).days + 1 
            for item in booking.items
        )
        
        # Format dates for display
        context.formatted_dates = []
        for item in booking.items:
            context.formatted_dates.append({
                'item_name': item.item_name,
                'function_date': formatdate(item.function_date) if item.function_date else 'Not set',
                'rental_start': formatdate(item.rental_start_date) if item.rental_start_date else 'Not set',
                'rental_end': formatdate(item.rental_end_date) if item.rental_end_date else 'Not set'
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
        frappe.log_error(f"Error loading booking confirmation for {booking_id}: {str(e)}")
        frappe.throw("Booking not found or access denied")
