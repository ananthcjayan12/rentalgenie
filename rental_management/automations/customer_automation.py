import frappe
from frappe import _
import re

def before_customer_save(doc, method):
    """Generate unique customer ID and validate mobile number"""
    
    # Validate mobile number format
    if doc.mobile_number:
        validate_mobile_number_format(doc)
        standardize_mobile_number(doc)
    
    # Check for duplicate mobile numbers
    validate_unique_mobile(doc)
    
    # Generate unique customer ID if not set
    if not doc.unique_customer_id:
        generate_unique_customer_id(doc)

def validate_mobile_number_format(doc):
    """Validate Indian mobile number format"""
    mobile = doc.mobile_number.strip()
    
    # Remove country code if present
    if mobile.startswith('+91'):
        mobile = mobile[3:].strip()
    elif mobile.startswith('91') and len(mobile) == 12:
        mobile = mobile[2:].strip()
    elif mobile.startswith('0') and len(mobile) == 11:
        mobile = mobile[1:].strip()
    
    # Check if it's a valid 10-digit number
    if not re.match(r'^[6-9]\d{9}$', mobile):
        frappe.throw(_("Please enter a valid Indian mobile number (10 digits starting with 6, 7, 8, or 9)"))
    
    doc.mobile_number = mobile

def standardize_mobile_number(doc):
    """Standardize mobile number to +91xxxxxxxxxx format"""
    mobile = doc.mobile_number.strip()
    
    # Remove any existing country code
    if mobile.startswith('+91'):
        mobile = mobile[3:].strip()
    elif mobile.startswith('91') and len(mobile) == 12:
        mobile = mobile[2:].strip()
    elif mobile.startswith('0') and len(mobile) == 11:
        mobile = mobile[1:].strip()
    
    # Add standard +91 prefix
    doc.mobile_number = f"+91{mobile}"

def generate_unique_customer_id(doc):
    """Generate unique customer ID based on name and mobile"""
    if not doc.customer_name or not doc.mobile_number:
        return
    
    # Get first 3 characters of customer name (uppercase, only letters)
    name_part = re.sub(r'[^A-Za-z]', '', doc.customer_name)[:3].upper()
    if len(name_part) < 3:
        name_part = name_part.ljust(3, 'X')  # Pad with X if name is too short
    
    # Get last 4 digits of mobile number
    mobile_part = doc.mobile_number[-4:]
    
    # Combine to create unique ID
    base_id = f"{name_part}{mobile_part}"
    
    # Check if this ID already exists, if so append a number
    unique_id = base_id
    counter = 1
    while frappe.db.exists("Customer", {"unique_customer_id": unique_id}):
        unique_id = f"{base_id}{counter}"
        counter += 1
    
    doc.unique_customer_id = unique_id

def validate_unique_mobile(doc):
    """Ensure mobile number is unique"""
    if doc.mobile_number:
        existing_customer = frappe.db.get_value("Customer", 
                                              {"mobile_number": doc.mobile_number, "name": ("!=", doc.name)}, 
                                              "name")
        if existing_customer:
            frappe.throw(_("Mobile number {0} is already registered with customer {1}").format(
                doc.mobile_number, existing_customer))

def update_customer_booking_stats(customer, booking_date=None):
    """Update customer booking statistics"""
    
    # Count total bookings
    total_bookings = frappe.db.count("Sales Invoice", {
        "customer": customer,
        "is_rental_booking": 1,
        "docstatus": 1
    })
    
    # Get last booking date
    last_booking = frappe.db.get_value("Sales Invoice", {
        "customer": customer,
        "is_rental_booking": 1,
        "docstatus": 1
    }, "posting_date", order_by="posting_date desc")
    
    # Calculate total rental amount
    total_amount = frappe.db.sql("""
        SELECT SUM(grand_total)
        FROM `tabSales Invoice`
        WHERE customer = %s 
        AND is_rental_booking = 1 
        AND docstatus = 1
    """, customer)[0][0] or 0
    
    # Update customer record
    frappe.db.set_value("Customer", customer, {
        "total_bookings": total_bookings,
        "last_booking_date": last_booking,
        "total_rental_amount": total_amount
    })
    
    frappe.db.commit()
