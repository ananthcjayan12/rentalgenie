import frappe
from rental_management.api.customer_portal import get_rental_items, get_rental_categories
import urllib.parse

def get_context(context):
    """Get context for category listing page with customer context"""
    
    # CRITICAL: Disable page caching only (don't break Frappe internals)
    context.no_cache = 1
    
    category = frappe.form_dict.get('category', '')
    search = frappe.form_dict.get('search', '')
    sort_by = frappe.form_dict.get('sort_by', 'name')
    page = int(frappe.form_dict.get('page', 1))
    customer_id = frappe.form_dict.get('customer', '')  # Sales staff customer selection
    per_page = 12
    
    # Decode URL parameters
    if category:
        category = urllib.parse.unquote(category)
    if search:
        search = urllib.parse.unquote(search)
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
            else:
                context.error_message = "Customer not found"
        # Get items for the category
        items_data = get_rental_items(
            category=category,
            search=search,
            sort_by=sort_by,
            page=page,
            limit=per_page
        )
        
        context.items = items_data.get('items', [])
        context.total_items = items_data.get('total_count', 0)
        context.has_more = items_data.get('has_more', False)
        
        # Get all categories for filter (function returns a list)
        categories_data = get_rental_categories()
        context.categories = categories_data or []
        
        # Current filters
        context.current_category = category or ''
        context.current_search = search or ''
        context.current_sort = sort_by or 'name'
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
        
        # Build URL parameters for pagination and customer context
        url_params = []
        if customer_id:
            url_params.append(f"customer={customer_id}")
        if category:
            url_params.append(f"category={category}")
        if search:
            url_params.append(f"search={search}")
        if sort_by != 'name':
            url_params.append(f"sort_by={sort_by}")
        
        context.base_url = "/portal/category"
        context.url_params = "&".join(url_params)
        
        # Add cache-busting timestamp
        import time
        context.cache_bust = int(time.time())
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Error loading category page: {str(e)}")
        context.items = []
        context.categories = []
        context.total_items = 0
        context.has_more = False
        context.current_category = category or ''
        context.current_search = search or ''
        context.current_sort = sort_by or 'name'
        context.current_page = page
        context.per_page = per_page
        context.total_pages = 1
        context.has_prev = False
        context.has_next = False
        context.prev_page = None
        context.next_page = None
        context.page_numbers = [1]
        context.base_url = "/portal/category"
        context.url_params = ""
        context.error_message = "Unable to load items. Please try again later."
        return context
