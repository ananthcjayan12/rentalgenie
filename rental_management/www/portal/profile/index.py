import frappe
from frappe import _
import urllib.parse

def get_context(context):
    """Get context for customer profile/management page"""
    
    # CRITICAL: Disable page caching only (don't break Frappe internals)
    context.no_cache = 1
    
    try:
        # Get parameters
        customer_id = frappe.form_dict.get('customer')
        return_to = frappe.form_dict.get('return_to')
        return_item = frappe.form_dict.get('item')
        
        # Store return context
        context.return_to = return_to
        context.return_item = return_item
        
        if customer_id:
            # Decode URL-encoded customer name
            customer_id = urllib.parse.unquote(customer_id)
            
            # Check if customer exists using fresh SQL query
            customer_exists = frappe.db.sql(
                """
                SELECT name FROM `tabCustomer`
                WHERE name = %s AND disabled = 0
                LIMIT 1
                """,
                (customer_id,),
                as_dict=True
            )
            
            if not customer_exists:
                context.mode = 'search'
                context.error_message = f"Customer '{customer_id}' not found"
                context.customer = None
                context.customer_bookings = []
                context.customer_addresses = []
                load_recent_customers(context)
                return context
            
            # Get customer details - force fresh query
            customer = frappe.db.sql(
                """
                SELECT name, customer_name, mobile_number, email_id, customer_group
                FROM `tabCustomer`
                WHERE name = %s AND disabled = 0
                LIMIT 1
                """,
                (customer_id,),
                as_dict=True
            )
            
            if not customer:
                context.mode = 'search'
                context.error_message = "Unable to load customer information"
                context.customer = None
                context.customer_bookings = []
                context.customer_addresses = []
                load_recent_customers(context)
                return context
            
            # Set customer view mode
            context.customer = customer[0]
            context.mode = 'view'
            
            # Get customer's addresses - force fresh query
            addresses = frappe.db.sql(
                """
                SELECT a.name, a.address_title, a.address_line1, a.address_line2,
                       a.city, a.state, a.pincode, a.country, a.address_type, 
                       a.is_primary_address
                FROM `tabAddress` a
                INNER JOIN `tabDynamic Link` dl
                  ON dl.parent = a.name 
                  AND dl.parenttype = 'Address'
                  AND dl.parentfield = 'links'
                WHERE dl.link_doctype = 'Customer' 
                  AND dl.link_name = %s
                ORDER BY a.is_primary_address DESC, a.creation DESC
                """,
                (customer_id,),
                as_dict=True,
            )
            context.customer_addresses = addresses or []
            
            # Get customer's bookings - force fresh query
            bookings = frappe.db.sql("""
                SELECT 
                    si.name, 
                    si.posting_date, 
                    si.total, 
                    si.booking_status,
                    si.customer_name, 
                    si.due_date,
                    COUNT(sii.name) as item_count
                FROM `tabSales Invoice` si
                LEFT JOIN `tabSales Invoice Item` sii 
                  ON si.name = sii.parent
                WHERE si.customer = %s 
                  AND si.is_rental_booking = 1
                  AND si.docstatus = 1
                GROUP BY si.name
                ORDER BY si.posting_date DESC
                LIMIT 10
            """, (customer_id,), as_dict=True)
            
            context.customer_bookings = bookings or []
            
            # Get customer statistics - force fresh query
            booking_stats = frappe.db.sql(
                """
                SELECT 
                    COUNT(*) as total_bookings,
                    SUM(total) as total_spent,
                    COUNT(CASE WHEN booking_status IN ('Confirmed', 'Delivered') 
                          THEN 1 END) as active_bookings,
                    COUNT(CASE WHEN booking_status = 'Completed' 
                          THEN 1 END) as completed_bookings,
                    MAX(posting_date) as last_booking_date
                FROM `tabSales Invoice`
                WHERE customer = %s 
                  AND is_rental_booking = 1
                  AND docstatus = 1
                """,
                (customer_id,),
                as_dict=True,
            )
            
            stats = booking_stats[0] if booking_stats else {}
            
            context.total_bookings = stats.get('total_bookings', 0)
            context.total_spent = stats.get('total_spent', 0) or 0
            context.active_bookings = stats.get('active_bookings', 0)
            context.completed_bookings = stats.get('completed_bookings', 0)
            context.last_booking_date = stats.get('last_booking_date')
            
            # Page metadata for customer view
            context.page_title = f"Customer Profile - {context.customer['customer_name']} | Blush & Glow"
            context.meta_description = f"Manage bookings and profile for {context.customer['customer_name']}"
            
        else:
            # Show customer search/selection interface
            context.mode = 'search'
            context.customer = None
            context.customer_bookings = []
            context.customer_addresses = []
            
            load_recent_customers(context)
            
            # Page metadata for search view
            context.page_title = "Customer Management | Blush & Glow"
            context.meta_description = "Select and manage customer profiles and bookings"
        
        # Add cache-busting timestamp
        import time
        context.cache_bust = int(time.time())
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Profile page error: {str(e)}", "Profile Page Error")
        
        context.error_message = "Unable to load customer information. Please try again."
        context.mode = 'search'
        context.customer = None
        context.customer_bookings = []
        context.customer_addresses = []
        load_recent_customers(context)
        
        return context


def load_recent_customers(context):
    """Load recent customers list with no caching"""
    try:
        # Force fresh query - add random comment to prevent query cache
        import random
        cache_bust = random.randint(1, 1000000)
        
        # Get recent customers - force fresh data
        recent_customers = frappe.db.sql(
            f"""
            SELECT /* cache_bust_{cache_bust} */
                c.name, 
                c.customer_name, 
                c.mobile_number, 
                c.email_id,
                COUNT(DISTINCT si.name) as booking_count,
                MAX(si.posting_date) as last_booking_date,
                c.creation
            FROM `tabCustomer` c
            LEFT JOIN `tabSales Invoice` si 
              ON c.name = si.customer 
              AND si.is_rental_booking = 1
              AND si.docstatus = 1
            WHERE c.disabled = 0
            GROUP BY c.name
            ORDER BY 
                CASE WHEN MAX(si.posting_date) IS NULL THEN 1 ELSE 0 END,
                MAX(si.posting_date) DESC, 
                c.creation DESC
            LIMIT 50
            """,
            as_dict=True,
        )
        
        context.recent_customers = recent_customers
        
    except Exception as e:
        frappe.log_error(f"Error loading recent customers: {str(e)}")
        context.recent_customers = []
