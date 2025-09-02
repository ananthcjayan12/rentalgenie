import frappe
from rental_management.api.customer_portal import get_cart_items

def get_context(context):
    """Get context for checkout page"""
    
    try:
        # Check if user is logged in
        if not frappe.session.user or frappe.session.user == 'Guest':
            frappe.local.flags.redirect_location = '/login?redirect-to=/portal/checkout'
            raise frappe.Redirect
            
        # Get cart items
        cart_data = get_cart_items()
        context.cart_items = cart_data.get('items', [])
        context.item_count = cart_data.get('item_count', 0)
        
        # Redirect to cart if empty
        if context.item_count == 0:
            frappe.local.flags.redirect_location = '/portal/cart'
            raise frappe.Redirect
            
        # Calculate totals
        context.subtotal = sum(item.get('total_amount', 0) for item in context.cart_items)
        context.delivery_charge = 0  # Free delivery
        context.grand_total = context.subtotal + context.delivery_charge
        
        # Get customer details if available
        customer_email = frappe.session.user
        customer = frappe.db.get_value("Customer", {"email_id": customer_email}, 
                                     ["name", "customer_name", "mobile_number", "customer_primary_address"], 
                                     as_dict=True)
        
        context.customer = customer or {}
        
        # Get customer address if exists
        if customer and customer.get('customer_primary_address'):
            address = frappe.get_doc("Address", customer.customer_primary_address)
            context.address = address
        else:
            context.address = None
            
        # Page metadata
        context.page_title = "Checkout | Blush & Glow"
        context.meta_description = "Complete your rental booking with secure checkout."
        
        return context
        
    except frappe.Redirect:
        raise
    except Exception as e:
        frappe.log_error(f"Error loading checkout page: {str(e)}")
        context.error_message = "Unable to load checkout. Please try again later."
        return context
