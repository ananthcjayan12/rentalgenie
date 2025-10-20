import frappe
from frappe import _

def get_context(context):
    """Context for Add Item page"""
    
    # CRITICAL: Disable page caching only (don't break Frappe internals)
    context.no_cache = 1
    
    context.page_title = "Add New Item"
    context.meta_description = "Add new rental items to inventory"
    
    # Force fresh queries with cache-busting
    import random
    cache_bust = random.randint(1, 1000000)
    
    # Get item groups for dropdown - force fresh query
    context.item_groups = frappe.db.sql(
        f"""
        SELECT /* cache_bust_{cache_bust}_1 */ name, item_group_name
        FROM `tabItem Group`
        WHERE is_group = 0
        ORDER BY item_group_name
        """,
        as_dict=True
    )
    
    # Get existing suppliers for dropdown - force fresh query
    context.suppliers = frappe.db.sql(
        f"""
        SELECT /* cache_bust_{cache_bust}_2 */ name, supplier_name
        FROM `tabSupplier`
        WHERE disabled = 0
        ORDER BY supplier_name
        """,
        as_dict=True
    )
    
    # Add cache-busting timestamp
    import time
    context.cache_bust = int(time.time())
    
    return context