import frappe

def get_context(context):
    """Get context for customer profile/management page"""
    
    try:
        # Get customer parameter (selected by shopkeeper)
        customer_id = frappe.form_dict.get('customer')
        
        # TEMPORARY DEBUG - Remove after fixing
        print(f"DEBUG: customer_id = '{customer_id}'")
        
        if customer_id:
            # Check if customer exists
            customer_exists = frappe.db.exists("Customer", customer_id)
            print(f"DEBUG: Customer {customer_id} exists: {customer_exists}")
            
            # Show specific customer details (use db.get_value to avoid permission issues)
            customer = frappe.db.get_value(
                "Customer",
                customer_id,
                ["name", "customer_name", "mobile_number", "email_id"],
                as_dict=True,
            )
            
            print(f"DEBUG: Customer found: {customer is not None}")
            
            if not customer:
                context.mode = 'search'
                context.error_message = "Customer not found"
                return context
            
            context.customer = customer
            context.mode = 'view'
            print(f"DEBUG: Set mode to 'view' for customer {customer['customer_name']}")
            
            # Get customer's addresses using Dynamic Link join
            addresses = frappe.db.sql(
                """
                SELECT a.name, a.address_title, a.address_line1, a.address_line2,
                       a.city, a.state, a.pincode, a.country, a.address_type, a.is_primary_address
                FROM `tabAddress` a
                JOIN `tabDynamic Link` dl
                  ON dl.parent = a.name AND dl.parenttype = 'Address'
                WHERE dl.link_doctype = 'Customer' AND dl.link_name = %s
                ORDER BY a.is_primary_address DESC, a.modified DESC
                """,
                (customer_id,),
                as_dict=True,
            )
            context.customer_addresses = addresses
            
            # Get customer's bookings
            bookings = frappe.db.sql("""
                SELECT 
                    si.name, si.posting_date, si.total, si.booking_status,
                    si.customer_name, si.due_date,
                    COUNT(sii.name) as item_count
                FROM `tabSales Invoice` si
                LEFT JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
                WHERE si.customer = %s 
                AND si.is_rental_booking = 1
                AND si.docstatus = 1
                GROUP BY si.name
                ORDER BY si.posting_date DESC
                LIMIT 10
            """, (customer_id,), as_dict=True)
            
            context.customer_bookings = bookings
            
            # Get customer statistics
            booking_stats = frappe.db.sql(
                """
                SELECT 
                    COUNT(*) as total_bookings,
                    SUM(total) as total_spent,
                    COUNT(CASE WHEN booking_status IN ('Confirmed', 'Delivered') THEN 1 END) as active_bookings,
                    COUNT(CASE WHEN booking_status = 'Completed' THEN 1 END) as completed_bookings,
                    MAX(posting_date) as last_booking_date
                FROM `tabSales Invoice`
                WHERE customer = %s 
                AND is_rental_booking = 1
                AND docstatus = 1
            """,
                (customer_id,),
                as_dict=True,
            )
            
            stats = booking_stats[0] if booking_stats else {
                'total_bookings': 0, 'total_spent': 0, 'active_bookings': 0, 
                'completed_bookings': 0, 'last_booking_date': None
            }
            
            context.total_bookings = stats['total_bookings']
            context.total_spent = stats['total_spent'] or 0
            context.active_bookings = stats['active_bookings']
            context.completed_bookings = stats['completed_bookings']
            
        else:
            # Show customer search/selection interface
            context.mode = 'search'
            context.customer = None
            context.customer_bookings = []
            
            # Get recent customers for quick selection
            recent_customers = frappe.db.sql(
                """
                SELECT DISTINCT c.name, c.customer_name, c.mobile_number, c.email_id,
                       COUNT(si.name) as booking_count,
                       MAX(si.posting_date) as last_booking_date
                FROM `tabCustomer` c
                LEFT JOIN `tabSales Invoice` si ON c.name = si.customer AND si.is_rental_booking = 1
                WHERE c.customer_group = 'Individual' AND c.disabled = 0
                GROUP BY c.name
                ORDER BY CASE WHEN last_booking_date IS NULL THEN 1 ELSE 0 END, last_booking_date DESC, c.creation DESC
                LIMIT 20
            """,
                as_dict=True,
            )
            
            context.recent_customers = recent_customers
        
        # Page metadata
        if customer_id:
            context.page_title = f"Customer Profile - {context.customer['customer_name']} | Blush & Glow"
            context.meta_description = f"Manage bookings and profile for {context.customer['customer_name']}"
        else:
            context.page_title = "Customer Management | Blush & Glow"
            context.meta_description = "Select and manage customer profiles and bookings"
        
        return context
        
    except Exception as e:
        print(f"DEBUG: Error in profile page: {str(e)}")
        context.error_message = "Unable to load customer information. Please try again."
        context.mode = 'search'
        context.customer = None
        return context
