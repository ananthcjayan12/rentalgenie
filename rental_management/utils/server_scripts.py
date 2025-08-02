# Server Script for Item Approval Workflow
# This will be added as a Server Script in ERPNext

import frappe
from frappe import _

# Button click handler for Item Approval
def approve_item(doc, method=None):
    """Server script function to approve rental item"""
    if not doc.is_rental_item:
        frappe.throw(_("Only rental items can be approved"))
    
    if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles():
        doc.approval_status = "Approved"
        doc.current_rental_status = "Available"
        frappe.msgprint(_("Item approved successfully"))
    else:
        frappe.throw(_("Only System Managers can approve items"))

def reject_item(doc, method=None):
    """Server script function to reject rental item"""
    if not doc.is_rental_item:
        frappe.throw(_("Only rental items can be rejected"))
    
    if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles():
        doc.approval_status = "Rejected"
        doc.current_rental_status = ""
        frappe.msgprint(_("Item rejected"))
    else:
        frappe.throw(_("Only System Managers can reject items"))

# Auto-update rental statistics
def update_rental_statistics(doc, method=None):
    """Update rental statistics when item is rented"""
    if hasattr(doc, 'is_rental_booking') and doc.is_rental_booking and doc.docstatus == 1:
        for item in doc.items:
            item_doc = frappe.get_doc("Item", item.item_code)
            if item_doc.is_rental_item:
                current_count = item_doc.total_rental_count or 0
                frappe.db.set_value("Item", item.item_code, "total_rental_count", current_count + 1)
