import frappe
from frappe import _
from frappe.utils import now_datetime, getdate

def approve_rental_item(item_code, approved_by=None):
    """Approve a rental item for public availability"""
    try:
        item_doc = frappe.get_doc("Item", item_code)
        
        if not item_doc.is_rental_item:
            frappe.throw(_("Only rental items can be approved"))
        
        if item_doc.approval_status == "Approved":
            frappe.msgprint(_("Item is already approved"))
            return
        
        # Update approval status
        item_doc.approval_status = "Approved"
        item_doc.current_rental_status = "Available"
        
        # Add approval comment
        approved_by = approved_by or frappe.session.user
        item_doc.add_comment("Comment", f"Item approved for rental by {approved_by} on {now_datetime()}")
        
        item_doc.save()
        frappe.msgprint(_("Item {0} has been approved for rental").format(item_code))
        
    except Exception as e:
        frappe.log_error(f"Error approving item {item_code}: {str(e)}")
        frappe.throw(_("Error approving item: {0}").format(str(e)))

def reject_rental_item(item_code, reason=None, rejected_by=None):
    """Reject a rental item"""
    try:
        item_doc = frappe.get_doc("Item", item_code)
        
        if not item_doc.is_rental_item:
            frappe.throw(_("Only rental items can be rejected"))
        
        # Update approval status
        item_doc.approval_status = "Rejected"
        item_doc.current_rental_status = ""
        
        # Add rejection comment
        rejected_by = rejected_by or frappe.session.user
        rejection_comment = f"Item rejected by {rejected_by} on {now_datetime()}"
        if reason:
            rejection_comment += f"\nReason: {reason}"
        
        item_doc.add_comment("Comment", rejection_comment)
        item_doc.save()
        
        frappe.msgprint(_("Item {0} has been rejected").format(item_code))
        
    except Exception as e:
        frappe.log_error(f"Error rejecting item {item_code}: {str(e)}")
        frappe.throw(_("Error rejecting item: {0}").format(str(e)))

def get_item_availability_status(item_code, start_date=None, end_date=None):
    """Check if a rental item is available for a specific date range"""
    try:
        item_doc = frappe.get_doc("Item", item_code)
        
        if not item_doc.is_rental_item:
            return {"available": False, "reason": "Not a rental item"}
        
        if item_doc.approval_status != "Approved":
            return {"available": False, "reason": "Item not approved for rental"}
        
        if item_doc.current_rental_status not in ["Available"]:
            return {"available": False, "reason": f"Item status: {item_doc.current_rental_status}"}
        
        # If no date range specified, just check current status
        if not start_date or not end_date:
            return {"available": True, "reason": "Available"}
        
        # Check for conflicting bookings in the specified date range
        conflicting_bookings = frappe.db.sql("""
            SELECT si.name, si.customer, si.rental_start_date, si.rental_end_date, si.booking_status
            FROM `tabSales Invoice` si
            JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
            WHERE sii.item_code = %s
            AND si.is_rental_booking = 1
            AND si.docstatus = 1
            AND si.booking_status NOT IN ('Completed', 'Cancelled', 'Exchanged')
            AND (
                (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR
                (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR
                (si.rental_start_date >= %s AND si.rental_end_date <= %s)
            )
        """, (item_code, start_date, start_date, end_date, end_date, start_date, end_date), as_dict=True)
        
        if conflicting_bookings:
            conflict_details = []
            for booking in conflicting_bookings:
                conflict_details.append(f"{booking.name} ({booking.rental_start_date} to {booking.rental_end_date})")
            
            return {
                "available": False, 
                "reason": "Already booked",
                "conflicting_bookings": conflict_details
            }
        
        return {"available": True, "reason": "Available for specified dates"}
        
    except Exception as e:
        frappe.log_error(f"Error checking availability for item {item_code}: {str(e)}")
        return {"available": False, "reason": f"Error: {str(e)}"}

def update_item_condition(item_code, condition_notes, condition_rating=None):
    """Update item condition after return"""
    try:
        item_doc = frappe.get_doc("Item", item_code)
        
        if not item_doc.is_rental_item:
            frappe.throw(_("Only rental items can have condition updates"))
        
        # Add condition comment
        condition_comment = f"Condition Update: {condition_notes}"
        if condition_rating:
            condition_comment += f"\nRating: {condition_rating}/5"
        
        item_doc.add_comment("Comment", condition_comment)
        
        # If condition is poor, set for maintenance
        if condition_rating and int(condition_rating) < 3:
            item_doc.current_rental_status = "Maintenance"
            frappe.msgprint(_("Item {0} marked for maintenance due to poor condition").format(item_code))
        
        item_doc.save()
        
    except Exception as e:
        frappe.log_error(f"Error updating condition for item {item_code}: {str(e)}")
        frappe.throw(_("Error updating item condition: {0}").format(str(e)))

def get_rental_items_for_approval():
    """Get list of rental items pending approval"""
    items = frappe.db.sql("""
        SELECT 
            item_code,
            item_name,
            rental_rate_per_day,
            rental_item_type,
            is_third_party_item,
            owner_commission_percent,
            creation,
            owner
        FROM `tabItem`
        WHERE is_rental_item = 1
        AND approval_status = 'Pending Approval'
        ORDER BY creation DESC
    """, as_dict=True)
    
    return items

def get_item_rental_history(item_code, limit=10):
    """Get rental history for an item"""
    history = frappe.db.sql("""
        SELECT 
            si.name,
            si.customer,
            si.posting_date,
            si.rental_start_date,
            si.rental_end_date,
            si.booking_status,
            sii.amount as rental_amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE sii.item_code = %s
        AND si.is_rental_booking = 1
        AND si.docstatus = 1
        ORDER BY si.posting_date DESC
        LIMIT %s
    """, (item_code, limit), as_dict=True)
    
    return history

def calculate_item_utilization(item_code, from_date=None, to_date=None):
    """Calculate utilization percentage for a rental item"""
    try:
        if not from_date:
            from_date = frappe.utils.add_months(frappe.utils.getdate(), -3)  # Last 3 months
        if not to_date:
            to_date = frappe.utils.getdate()
        
        total_days = (getdate(to_date) - getdate(from_date)).days
        
        if total_days <= 0:
            return 0
        
        # Get total rented days in the period
        rented_days = frappe.db.sql("""
            SELECT SUM(DATEDIFF(
                LEAST(si.rental_end_date, %s),
                GREATEST(si.rental_start_date, %s)
            ) + 1) as total_rented_days
            FROM `tabSales Invoice` si
            JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
            WHERE sii.item_code = %s
            AND si.is_rental_booking = 1
            AND si.docstatus = 1
            AND si.booking_status != 'Cancelled'
            AND si.rental_start_date <= %s
            AND si.rental_end_date >= %s
        """, (to_date, from_date, item_code, to_date, from_date))[0][0] or 0
        
        utilization_percentage = (rented_days / total_days) * 100
        return min(utilization_percentage, 100)  # Cap at 100%
        
    except Exception as e:
        frappe.log_error(f"Error calculating utilization for item {item_code}: {str(e)}")
        return 0

# Add alias functions for backward compatibility
def approve_item(item_code, approved_by=None):
    """Alias for approve_rental_item - for backward compatibility"""
    return approve_rental_item(item_code, approved_by)

def reject_item(item_code, reason=None, rejected_by=None):
    """Alias for reject_rental_item - for backward compatibility"""
    return reject_rental_item(item_code, reason, rejected_by)
