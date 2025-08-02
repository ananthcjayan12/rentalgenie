import frappe
from frappe.utils import getdate, add_days

def search_customers_by_mobile(mobile_query):
    """Search customers by mobile number (partial match)"""
    
    # Clean the mobile query
    mobile_query = mobile_query.strip()
    if mobile_query.startswith('+91'):
        mobile_query = mobile_query[3:]
    
    customers = frappe.db.sql("""
        SELECT name, customer_name, mobile_number, unique_customer_id, 
               total_bookings, last_booking_date
        FROM `tabCustomer`
        WHERE mobile_number LIKE %s
        ORDER BY name
        LIMIT 20
    """, f"%{mobile_query}%", as_dict=True)
    
    return customers

def search_customers_by_name(name_query):
    """Search customers by name (partial match)"""
    
    customers = frappe.db.sql("""
        SELECT name, customer_name, mobile_number, unique_customer_id,
               total_bookings, last_booking_date
        FROM `tabCustomer`
        WHERE customer_name LIKE %s
        ORDER BY customer_name
        LIMIT 20
    """, f"%{name_query}%", as_dict=True)
    
    return customers

def get_customer_booking_history(customer_name, limit=10):
    """Get recent booking history for a customer"""
    
    bookings = frappe.db.sql("""
        SELECT si.name as booking_reference, si.posting_date, si.function_date,
               si.rental_start_date, si.rental_end_date, si.booking_status,
               si.grand_total, si.advance_amount, si.caution_deposit_amount,
               COUNT(sii.name) as total_items
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE si.customer = %s 
        AND si.is_rental_booking = 1
        AND si.docstatus = 1
        GROUP BY si.name
        ORDER BY si.posting_date DESC
        LIMIT %s
    """, (customer_name, limit), as_dict=True)
    
    return bookings

def get_customer_statistics(customer_name):
    """Get comprehensive statistics for a customer"""
    
    stats = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_bookings,
            SUM(grand_total) as total_spent,
            AVG(grand_total) as avg_booking_amount,
            MAX(posting_date) as last_booking_date,
            MIN(posting_date) as first_booking_date,
            SUM(CASE WHEN booking_status = 'Completed' THEN 1 ELSE 0 END) as completed_bookings,
            SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_bookings
        FROM `tabSales Invoice`
        WHERE customer = %s 
        AND is_rental_booking = 1
        AND docstatus = 1
    """, customer_name, as_dict=True)
    
    return stats[0] if stats else {}

def get_customer_preferred_items(customer_name, limit=5):
    """Get most rented items by a customer"""
    
    items = frappe.db.sql("""
        SELECT sii.item_code, sii.item_name, 
               COUNT(*) as times_rented,
               SUM(sii.amount) as total_spent_on_item
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE si.customer = %s 
        AND si.is_rental_booking = 1
        AND si.docstatus = 1
        GROUP BY sii.item_code, sii.item_name
        ORDER BY times_rented DESC, total_spent_on_item DESC
        LIMIT %s
    """, (customer_name, limit), as_dict=True)
    
    return items

def check_customer_outstanding_bookings(customer_name):
    """Check if customer has any outstanding/active bookings"""
    
    outstanding = frappe.db.sql("""
        SELECT name, booking_status, rental_start_date, rental_end_date,
               grand_total, outstanding_amount
        FROM `tabSales Invoice`
        WHERE customer = %s 
        AND is_rental_booking = 1
        AND docstatus = 1
        AND booking_status IN ('Confirmed', 'Out for Rental', 'Partially Returned')
        ORDER BY rental_start_date
    """, customer_name, as_dict=True)
    
    return outstanding

def validate_customer_eligibility_for_booking(customer_name):
    """Validate if customer is eligible for new booking"""
    
    # Check for outstanding bookings
    outstanding = check_customer_outstanding_bookings(customer_name)
    
    # Check for any pending payments
    pending_payments = frappe.db.sql("""
        SELECT name, outstanding_amount
        FROM `tabSales Invoice`
        WHERE customer = %s 
        AND is_rental_booking = 1
        AND docstatus = 1
        AND outstanding_amount > 0
    """, customer_name, as_dict=True)
    
    eligibility = {
        "eligible": True,
        "outstanding_bookings": len(outstanding),
        "pending_amount": sum([p.outstanding_amount for p in pending_payments]),
        "issues": []
    }
    
    if outstanding:
        eligibility["issues"].append(f"Customer has {len(outstanding)} active booking(s)")
    
    if eligibility["pending_amount"] > 0:
        eligibility["issues"].append(f"Pending payment: ₹{eligibility['pending_amount']:.2f}")
    
    # Set eligibility based on business rules
    if len(outstanding) > 2:  # Max 2 concurrent bookings
        eligibility["eligible"] = False
        eligibility["issues"].append("Maximum concurrent bookings limit reached")
    
    if eligibility["pending_amount"] > 5000:  # Max ₹5000 pending
        eligibility["eligible"] = False
        eligibility["issues"].append("Pending amount exceeds limit")
    
    return eligibility
