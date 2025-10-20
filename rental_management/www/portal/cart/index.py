import frappe
from frappe.utils import formatdate, get_datetime
from rental_management.api.customer_portal import get_customer_cart_items
import urllib.parse

def get_context(context):
    """Get context for shopping cart page with customer context"""
    
    # CRITICAL: Disable page caching only (don't break Frappe internals)
    context.no_cache = 1
    
    customer_id = frappe.form_dict.get('customer', '')  # Sales staff customer selection
    
    # Decode URL parameters
    if customer_id:
        customer_id = urllib.parse.unquote(customer_id)
    
    try:
        # Handle customer context for sales staff portal
        context.customer_id = customer_id
        context.customer = None
        
        if customer_id:
            # Get customer details for header display - force fresh query
            customer_data = frappe.db.sql(
                """
                SELECT name, customer_name, mobile_number
                FROM `tabCustomer`
                WHERE name = %s AND disabled = 0
                LIMIT 1
                """,
                (customer_id,),
                as_dict=True
            )
            if customer_data:
                context.customer = customer_data[0]
                
                # Get customer-specific cart items
                cart_data = get_customer_cart_items(customer_id)
            else:
                context.error_message = "Customer not found"
                cart_data = {'items': [], 'total': 0, 'item_count': 0}
        else:
            # No customer selected - show empty cart
            context.error_message = "Please select a customer to view cart"
            cart_data = {'items': [], 'total': 0, 'item_count': 0}
            
        # Process cart items and serialize dates for JSON
        cart_items = cart_data.get('items', [])
        serialized_cart_items = []
        
        for item in cart_items:
            # Create a copy of the item with serialized dates
            serialized_item = {}
            
            # Copy all non-date fields
            for key, value in item.items():
                if key in ['function_date', 'rental_start_date', 'rental_end_date']:
                    # Convert date objects to strings for JSON serialization
                    if value:
                        try:
                            if hasattr(value, 'strftime'):
                                serialized_item[key] = value.strftime('%Y-%m-%d')
                            elif hasattr(value, 'isoformat'):
                                serialized_item[key] = value.isoformat()
                            else:
                                serialized_item[key] = str(value)
                        except Exception as e:
                            # Use print for debugging instead of log_error to avoid character limits
                            print(f"Date serialization error for {key}: {e}")
                            serialized_item[key] = None
                    else:
                        serialized_item[key] = None
                else:
                    # Copy other fields as-is, but ensure they're JSON serializable
                    try:
                        import json
                        json.dumps(value)  # Test if value is JSON serializable
                        serialized_item[key] = value
                    except (TypeError, ValueError):
                        # Convert non-serializable values to strings
                        serialized_item[key] = str(value) if value is not None else None
                        
            serialized_cart_items.append(serialized_item)
            
        context.cart_items = cart_items  # Original items for template display
        context.cart_items_json = serialized_cart_items  # Serialized items for JSON
        context.cart_total = cart_data.get('total', 0)
        context.item_count = cart_data.get('item_count', 0)
        
        # Calculate caution deposit total
        total_caution_deposit = 0
        for item in context.cart_items:
            if item.get('item_code'):
                # Get main item code for caution deposit lookup
                main_item_code = item['item_code'][:-7] if item['item_code'].endswith('-RENTAL') else item['item_code']
                try:
                    caution_deposit = frappe.db.get_value("Item", main_item_code, "caution_deposit") or 0
                    total_caution_deposit += caution_deposit
                except:
                    pass
        
        context.total_caution_deposit = total_caution_deposit
        
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
        
        # Add cache-busting timestamp
        import time
        context.cache_bust = int(time.time())
        
        return context
        
    except Exception as e:
        # Use print for debugging instead of log_error to avoid character limits
        print(f"Error loading cart page: {str(e)}")
        context.cart_items = []
        context.cart_items_json = []
        context.cart_total = 0
        context.item_count = 0
        context.error_message = "Unable to load cart. Please try again later."
        return context
