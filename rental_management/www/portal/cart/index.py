import frappe
from rental_management.api.customer_portal import get_cart_items

def get_context(context):
    """Get context for shopping cart page"""
    
    try:
        # Get cart items
        cart_data = get_cart_items()
        context.cart_items = cart_data.get('items', [])
        context.cart_total = cart_data.get('total_amount', 0)
        context.item_count = cart_data.get('item_count', 0)
        
        # Calculate summary
        context.subtotal = sum(item.get('total_amount', 0) for item in context.cart_items)
        context.delivery_charge = 0  # Free delivery for now
        context.grand_total = context.subtotal + context.delivery_charge
        
        # Page metadata
        context.page_title = f"Shopping Cart ({context.item_count}) | Blush & Glow"
        context.meta_description = "Review your rental cart and proceed to checkout."
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Error loading cart page: {str(e)}")
        context.cart_items = []
        context.cart_total = 0
        context.item_count = 0
        context.error_message = "Unable to load cart. Please try again later."
        return context
