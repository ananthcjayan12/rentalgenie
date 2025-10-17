import frappe
from rental_management.api.customer_portal import get_portal_categories, get_portal_banners, get_rental_items

def get_context(context):
    """Get context for portal home page"""
    
    # Get banners for the carousel
    context.banners = get_portal_banners()
    
    # Get categories for the main navigation (using new portal categories)
    context.categories = get_portal_categories()
    
    # Get trending/featured items for home page (sorted by trending)
    trending_items = get_rental_items(filters={'is_trending': True}, sort_by='trending', limit=6)
    context.trending_items = trending_items.get('items', [])
    
    # Get discounted items
    discount_items = get_rental_items(limit=8)
    context.discount_items = discount_items.get('items', [])
    
    # Page metadata
    context.page_title = "Blush & Glow - Premium Rental Collection"
    context.meta_description = "Rent premium designer wear for your special occasions. Lehengas, Gowns, Jewelry and more."
    
    return context
