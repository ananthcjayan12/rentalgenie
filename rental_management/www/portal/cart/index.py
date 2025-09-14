import frappe
from rental_management.api.customer_portal import get_cart_items, get_customer_cart_items

def get_context(context):
    """Get context for shopping cart page with customer context"""
    
    customer_id = frappe.form_dict.get('customer', '')  # Sales staff customer selection
    
    try:
        # Handle customer context for sales staff portal
        context.customer_id = customer_id
        context.customer = None
        
        if customer_id:
            # Get customer details for header display
            customer_data = frappe.db.get_value(
                "Customer",
                customer_id,
                ["name", "customer_name", "mobile_number"],
                as_dict=True
            )
            if customer_data:
                context.customer = customer_data
                
                # Get customer-specific cart items
                cart_data = get_customer_cart_items(customer_id)
            else:
                context.error_message = "Customer not found"
                cart_data = {'items': [], 'total': 0, 'item_count': 0}
        else:
            # Get session-based cart items (fallback)
            cart_data = get_cart_items()
            
        context.cart_items = cart_data.get('items', [])
        context.cart_total = cart_data.get('total', 0)
        context.item_count = cart_data.get('item_count', 0)
        
        # Calculate summary
        context.subtotal = sum(item.get('total_amount', 0) for item in context.cart_items)
        context.delivery_charge = 0  # Free delivery for now
        context.grand_total = context.subtotal + context.delivery_charge
        
        # Page metadata
        if customer_id and context.customer:
            context.page_title = f"{context.customer['customer_name']} - Cart ({context.item_count}) | Blush & Glow"
            context.meta_description = f"Review {context.customer['customer_name']}'s rental cart and proceed to checkout."
        else:
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
