import frappe
from rental_management.api.customer_portal import get_item_details, check_item_availability
import urllib.parse

def get_context(context):
    """Get context for item detail page with customer context"""
    
    # CRITICAL: Disable all caching for real-time updates
    context.no_cache = 1
    frappe.response['type'] = 'page'
    
    # Clear request-level cache
    if hasattr(frappe.local, 'request_cache'):
        frappe.local.request_cache = {}
    
    item_code = frappe.form_dict.get('item')
    customer_id = frappe.form_dict.get('customer', '')  # Sales staff customer selection
    
    # Decode URL parameters
    if item_code:
        item_code = urllib.parse.unquote(item_code)
    if customer_id:
        customer_id = urllib.parse.unquote(customer_id)
    
    if not item_code:
        frappe.throw("Item not specified")
    
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
                
                # Get customer's current cart count from database - force fresh query
                cart_doc_name = frappe.db.sql(
                    """
                    SELECT name FROM `tabRental Cart`
                    WHERE customer = %s AND status = 'Active' AND docstatus = 0
                    LIMIT 1
                    """,
                    (customer_id,),
                    as_dict=True
                )
                
                if cart_doc_name:
                    cart = frappe.get_doc("Rental Cart", cart_doc_name[0].name)
                    context.cart_count = len(cart.items)
                else:
                    context.cart_count = 0
        
        # Get item details
        context.item = get_item_details(item_code)
        
        # Get related items (same category)
        from rental_management.api.customer_portal import get_rental_items
        related_items = get_rental_items(
            category=context.item.get('rental_item_type'),
            limit=4
        )
        # Remove current item from related items
        context.related_items = [
            item for item in related_items.get('items', []) 
            if item['item_code'] != item_code
        ][:3]
        
        # Page metadata
        context.page_title = f"{context.item['item_name']} - Rental | Blush & Glow"
        context.meta_description = f"Rent {context.item['item_name']} at ₹{context.item['rental_rate_per_day']}/day. {context.item['description']}"
        
        # Add cache-busting timestamp
        import time
        context.cache_bust = int(time.time())
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Error loading item detail page for {item_code}: {str(e)}")
        frappe.throw("Item not found or not available for rental")
