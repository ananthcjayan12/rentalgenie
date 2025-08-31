import frappe
from rental_management.api.customer_portal import get_item_details, check_item_availability

def get_context(context):
    """Get context for item detail page"""
    
    item_code = frappe.form_dict.get('item')
    if not item_code:
        frappe.throw("Item not specified")
    
    try:
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
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Error loading item detail page for {item_code}: {str(e)}")
        frappe.throw("Item not found or not available for rental")
