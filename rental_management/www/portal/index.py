import frappe
from rental_management.api.customer_portal import get_portal_categories, get_portal_banners, get_rental_items

def get_context(context):
    """Get context for portal home page"""
    
    # Get banners for the carousel
    context.banners = get_portal_banners()
    
    # Get categories for the main navigation (using new portal categories)
    context.categories = get_portal_categories()
    
    # Get random items for trending section (2-4 items)
    random_items = get_rental_items(sort_by='random', limit=4)
    context.trending_items = random_items.get('items', [])
    
    # Page metadata
    context.page_title = "Blush & Glow - Premium Rental Collection"
    context.meta_description = "Rent premium designer wear for your special occasions. Lehengas, Gowns, Jewelry and more."
    
    return context
