import frappe
from rental_management.api.customer_portal import get_rental_items, get_rental_categories

def get_context(context):
    """Get context for category listing page"""
    
    category = frappe.form_dict.get('category', '')
    search = frappe.form_dict.get('search', '')
    sort_by = frappe.form_dict.get('sort_by', 'name')
    page = int(frappe.form_dict.get('page', 1))
    per_page = 12
    
    try:
        # Get items for the category
        items_data = get_rental_items(
            category=category,
            search=search,
            sort_by=sort_by,
            page=page,
            limit=per_page
        )
        
        context.items = items_data.get('items', [])
        context.total_items = items_data.get('total', 0)
        context.has_more = items_data.get('has_more', False)
        
        # Get all categories for filter
        categories_data = get_rental_categories()
        context.categories = categories_data.get('categories', [])
        
        # Current filters
        context.current_category = category
        context.current_search = search
        context.current_sort = sort_by
        context.current_page = page
        context.per_page = per_page
        
        # Calculate pagination
        total_pages = (context.total_items + per_page - 1) // per_page
        context.total_pages = total_pages
        context.has_prev = page > 1
        context.has_next = page < total_pages
        context.prev_page = page - 1 if context.has_prev else None
        context.next_page = page + 1 if context.has_next else None
        
        # Generate page numbers for pagination
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)
        context.page_numbers = list(range(start_page, end_page + 1))
        
        # Page metadata
        if category:
            category_name = category.replace('_', ' ').title()
            context.page_title = f"{category_name} Rentals | Blush & Glow"
            context.meta_description = f"Browse our {category_name.lower()} collection for rent. Premium quality items at affordable rates."
        elif search:
            context.page_title = f"Search: {search} | Blush & Glow"
            context.meta_description = f"Search results for '{search}' in our rental collection."
        else:
            context.page_title = "All Rentals | Blush & Glow"
            context.meta_description = "Browse our complete collection of rental items. Premium quality at affordable rates."
        
        # Build URL parameters for pagination
        url_params = []
        if category:
            url_params.append(f"category={category}")
        if search:
            url_params.append(f"search={search}")
        if sort_by != 'name':
            url_params.append(f"sort_by={sort_by}")
        
        context.base_url = "/portal/category"
        context.url_params = "&".join(url_params)
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Error loading category page: {str(e)}")
        context.items = []
        context.categories = []
        context.error_message = "Unable to load items. Please try again later."
        return context
