import frappe
from frappe import _
from frappe.utils import getdate, add_days

def validate_rental_booking_dates(doc):
    """Validate rental booking dates and duration"""
    
    if not doc.function_date:
        frappe.throw(_("Function Date is mandatory for rental bookings"))
    
    if not doc.rental_duration_days or doc.rental_duration_days < 1:
        frappe.throw(_("Rental Duration must be at least 1 day"))
    
    function_date = getdate(doc.function_date)
    today = getdate()
    
    # Function date should not be in the past
    if function_date < today:
        frappe.throw(_("Function Date cannot be in the past"))
    
    # Function date should not be too far in the future (1 year max)
    max_advance_date = add_days(today, 365)
    if function_date > max_advance_date:
        frappe.throw(_("Function Date cannot be more than 1 year in advance"))

def validate_rental_items(doc):
    """Validate that all items in the booking are rental items"""
    
    non_rental_items = []
    
    for item in doc.items:
        item_doc = frappe.get_doc("Item", item.item_code)
        if not item_doc.is_rental_item:
            non_rental_items.append(item.item_code)
    
    if non_rental_items:
        frappe.throw(_("The following items are not enabled for rental: {0}").format(", ".join(non_rental_items)))

def validate_rental_amounts(doc):
    """Validate rental amounts and calculations"""
    
    # Advance amount should not exceed total amount
    if doc.advance_amount and doc.grand_total:
        if doc.advance_amount > doc.grand_total:
            frappe.throw(_("Advance amount cannot exceed total booking amount"))
    
    # Caution deposit should be reasonable (not more than 5x rental amount)
    if doc.caution_deposit_amount and doc.grand_total:
        if doc.caution_deposit_amount > (doc.grand_total * 5):
            frappe.throw(_("Caution deposit seems unusually high. Please verify the amount."))

def validate_customer_eligibility(doc):
    """Validate customer eligibility for booking"""
    
    # Check if customer has outstanding bookings
    outstanding_bookings = frappe.db.count("Sales Invoice", {
        "customer": doc.customer,
        "is_rental_booking": 1,
        "docstatus": 1,
        "booking_status": ["in", ["Confirmed", "Out for Rental", "Partially Returned"]],
        "name": ["!=", doc.name]
    })
    
    # Maximum 3 concurrent bookings per customer
    if outstanding_bookings >= 3:
        frappe.throw(_("Customer {0} already has {1} active bookings. Maximum allowed is 3.").format(
            doc.customer, outstanding_bookings))
    
    # Check pending payments
    pending_amount = frappe.db.sql("""
        SELECT SUM(outstanding_amount) 
        FROM `tabSales Invoice` 
        WHERE customer = %s 
        AND is_rental_booking = 1 
        AND docstatus = 1 
        AND outstanding_amount > 0
    """, doc.customer)[0][0] or 0
    
    # Maximum ₹10,000 pending payment
    if pending_amount > 10000:
        frappe.throw(_("Customer {0} has pending payments of ₹{1}. Please clear dues before new booking.").format(
            doc.customer, pending_amount))

def validate_exchange_booking_rules(doc):
    """Validate exchange booking specific rules"""
    
    if not doc.is_exchange_booking:
        return
    
    # Validate original booking
    original_booking = frappe.get_doc("Sales Invoice", doc.original_booking_reference)
    
    # Original booking should be from same customer
    if original_booking.customer != doc.customer:
        frappe.throw(_("Exchange booking must be for the same customer as original booking"))
    
    # Original booking should not be delivered yet
    if original_booking.booking_status == "Out for Rental":
        frappe.throw(_("Cannot exchange booking after items have been delivered"))
    
    # Exchange should be for same or earlier function date
    if getdate(doc.function_date) > getdate(original_booking.function_date):
        frappe.throw(_("Exchange booking function date cannot be later than original booking"))

def validate_item_availability_comprehensive(doc):
    """Comprehensive item availability validation"""
    
    unavailable_items = []
    
    for item in doc.items:
        item_doc = frappe.get_doc("Item", item.item_code)
        
        if item_doc.is_rental_item:
            # Check item approval status
            if item_doc.approval_status != "Approved":
                unavailable_items.append(f"{item.item_code} (Status: {item_doc.approval_status})")
                continue
            
            # Check item condition
            if hasattr(item_doc, 'current_condition') and item_doc.current_condition < 3:
                unavailable_items.append(f"{item.item_code} (Poor condition)")
                continue
            
            # Check stock availability
            stock_qty = frappe.db.get_value("Stock Ledger Entry", 
                                          {"item_code": item.item_code}, 
                                          "sum(actual_qty)") or 0
            
            if stock_qty < item.qty:
                unavailable_items.append(f"{item.item_code} (Insufficient stock: {stock_qty} available, {item.qty} required)")
    
    if unavailable_items:
        frappe.throw(_("The following items are not available for rental:\n{0}").format("\n".join(unavailable_items)))

def get_booking_conflicts_report(doc):
    """Generate a report of potential booking conflicts"""
    
    conflicts = []
    
    for item in doc.items:
        item_doc = frappe.get_doc("Item", item.item_code)
        
        if item_doc.is_rental_item:
            conflicting_bookings = frappe.db.sql("""
                SELECT si.name, si.customer, si.rental_start_date, si.rental_end_date, 
                       si.booking_status, si.function_date
                FROM `tabSales Invoice` si
                JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
                WHERE sii.item_code = %s
                AND si.is_rental_booking = 1
                AND si.docstatus = 1
                AND si.booking_status NOT IN ('Cancelled', 'Completed', 'Exchanged')
                AND si.name != %s
                AND (
                    (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR
                    (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR
                    (si.rental_start_date >= %s AND si.rental_end_date <= %s)
                )
            """, (
                item.item_code, 
                doc.name or "",
                doc.rental_start_date, doc.rental_start_date,
                doc.rental_end_date, doc.rental_end_date,
                doc.rental_start_date, doc.rental_end_date
            ), as_dict=True)
            
            if conflicting_bookings:
                conflicts.append({
                    "item_code": item.item_code,
                    "conflicts": conflicting_bookings
                })
    
    return conflicts
