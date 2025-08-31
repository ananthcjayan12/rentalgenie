import frappe

def get_context(context):
    """Get context for profile page"""
    
    try:
        # Check if user is logged in
        if not frappe.session.user or frappe.session.user == 'Guest':
            frappe.local.flags.redirect_location = '/login?redirect-to=/portal/profile'
            raise frappe.Redirect
            
        # Get customer details
        customer_email = frappe.session.user
        customer = frappe.db.get_value("Customer", {"email_id": customer_email}, 
                                     ["name", "customer_name", "mobile_no", "customer_primary_address"], 
                                     as_dict=True)
        
        context.customer = customer or {}
        context.customer_email = customer_email
        
        # Get customer address if exists
        if customer and customer.get('customer_primary_address'):
            address = frappe.get_doc("Address", customer.customer_primary_address)
            context.address = address
        else:
            context.address = None
            
        # Get booking statistics
        if customer:
            booking_stats = frappe.db.sql("""
                SELECT 
                    COUNT(*) as total_bookings,
                    SUM(total) as total_spent,
                    COUNT(CASE WHEN booking_status = 'Confirmed' THEN 1 END) as active_bookings
                FROM `tabSales Invoice`
                WHERE customer = %s 
                AND is_rental_booking = 1
                AND docstatus = 1
            """, (customer.name,), as_dict=True)
            
            context.stats = booking_stats[0] if booking_stats else {
                'total_bookings': 0,
                'total_spent': 0,
                'active_bookings': 0
            }
        else:
            context.stats = {'total_bookings': 0, 'total_spent': 0, 'active_bookings': 0}
            
        # Page metadata
        context.page_title = "My Profile | Blush & Glow"
        context.meta_description = "Manage your profile and account settings."
        
        return context
        
    except frappe.Redirect:
        raise
    except Exception as e:
        frappe.log_error(f"Error loading profile page: {str(e)}")
        context.error_message = "Unable to load profile. Please try again later."
        return context
