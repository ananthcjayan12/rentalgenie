"""
Custom hooks for Item doctype to add rental approval functionality
Add this to your hooks.py file
"""

import frappe
from frappe import _

def add_approval_buttons(doc, handler=""):
    """Add approval buttons to Item form for rental items"""
    if not doc.is_rental_item:
        return
        
    if doc.approval_status == "Pending Approval":
        # Add Approve button
        doc.add_custom_button(
            _("Approve for Rental"),
            lambda: approve_item_from_form(doc.name),
            icon="fa fa-check",
            btn_class="btn-success"
        )
        
        # Add Reject button  
        doc.add_custom_button(
            _("Reject"),
            lambda: reject_item_from_form(doc.name),
            icon="fa fa-times",
            btn_class="btn-danger"
        )
    
    elif doc.approval_status == "Approved":
        # Add button to view rental history
        doc.add_custom_button(
            _("Rental History"),
            lambda: show_rental_history(doc.name),
            icon="fa fa-history"
        )
        
        # Add button to check availability
        doc.add_custom_button(
            _("Check Availability"),
            lambda: check_item_availability(doc.name),
            icon="fa fa-calendar"
        )

@frappe.whitelist()
def approve_item_from_form(item_code):
    """Handle item approval from form button"""
    try:
        from rental_management.utils.item_utils import approve_rental_item
        approve_rental_item(item_code)
        
        # Refresh the form
        frappe.response["type"] = "success"
        frappe.response["message"] = _("Item approved successfully")
        frappe.response["reload"] = True
        
    except Exception as e:
        frappe.response["type"] = "error"
        frappe.response["message"] = str(e)

@frappe.whitelist()
def reject_item_from_form(item_code):
    """Handle item rejection from form button"""
    try:
        # Get rejection reason through dialog
        reason = frappe.form_dict.get("reason", "No reason provided")
        
        from rental_management.utils.item_utils import reject_rental_item
        reject_rental_item(item_code, reason)
        
        # Refresh the form
        frappe.response["type"] = "success"
        frappe.response["message"] = _("Item rejected successfully")
        frappe.response["reload"] = True
        
    except Exception as e:
        frappe.response["type"] = "error"
        frappe.response["message"] = str(e)

@frappe.whitelist()
def show_rental_history(item_code):
    """Show rental history for an item"""
    try:
        from rental_management.utils.item_utils import get_item_rental_history
        history = get_item_rental_history(item_code, limit=20)
        
        if not history:
            frappe.msgprint(_("No rental history found for this item"))
            return
        
        # Format history for display
        history_html = "<table class='table table-bordered'>"
        history_html += "<tr><th>Booking</th><th>Customer</th><th>Start Date</th><th>End Date</th><th>Status</th><th>Amount</th></tr>"
        
        for record in history:
            history_html += f"""
            <tr>
                <td><a href='/app/sales-invoice/{record.name}'>{record.name}</a></td>
                <td>{record.customer}</td>
                <td>{record.rental_start_date}</td>
                <td>{record.rental_end_date}</td>
                <td>{record.booking_status}</td>
                <td>{frappe.utils.fmt_money(record.rental_amount)}</td>
            </tr>
            """
        
        history_html += "</table>"
        
        frappe.msgprint(history_html, title=_("Rental History for {0}").format(item_code))
        
    except Exception as e:
        frappe.msgprint(_("Error fetching rental history: {0}").format(str(e)))

@frappe.whitelist()
def check_item_availability(item_code):
    """Check current availability status of an item"""
    try:
        from rental_management.utils.item_utils import get_item_availability_status
        availability = get_item_availability_status(item_code)
        
        if availability.get("available"):
            frappe.msgprint(_("Item is currently available for rental"), 
                          title=_("Availability Status"), indicator="green")
        else:
            reason = availability.get("reason", "Unknown reason")
            frappe.msgprint(_("Item is not available. Reason: {0}").format(reason), 
                          title=_("Availability Status"), indicator="red")
            
    except Exception as e:
        frappe.msgprint(_("Error checking availability: {0}").format(str(e)))

@frappe.whitelist()
def get_pending_approval_count():
    """Get count of items pending approval"""
    count = frappe.db.count("Item", {
        "is_rental_item": 1,
        "approval_status": "Pending Approval"
    })
    return count

@frappe.whitelist()
def bulk_approve_items(item_codes):
    """Bulk approve multiple items"""
    if isinstance(item_codes, str):
        item_codes = frappe.parse_json(item_codes)
    
    success_count = 0
    errors = []
    
    for item_code in item_codes:
        try:
            from rental_management.utils.item_utils import approve_rental_item
            approve_rental_item(item_code)
            success_count += 1
        except Exception as e:
            errors.append(f"{item_code}: {str(e)}")
    
    message = _("Successfully approved {0} items").format(success_count)
    if errors:
        message += _("<br><br>Errors:<br>") + "<br>".join(errors)
    
    frappe.msgprint(message, title=_("Bulk Approval Results"))
    
    return {
        "success_count": success_count,
        "errors": errors
    }

# Client-side JavaScript functions to add to Item form
def get_item_approval_js():
    """JavaScript code to enhance Item form for rental approval"""
    return """
    // Add this to a custom script for Item doctype
    frappe.ui.form.on('Item', {
        refresh: function(frm) {
            if (frm.doc.is_rental_item && frm.doc.approval_status === 'Pending Approval') {
                // Add approval buttons with dialogs
                frm.add_custom_button(__('Approve for Rental'), function() {
                    frappe.confirm(
                        __('Are you sure you want to approve this item for rental?'),
                        function() {
                            frappe.call({
                                method: 'rental_management.utils.item_hooks.approve_item_from_form',
                                args: {
                                    item_code: frm.doc.name
                                },
                                callback: function(r) {
                                    if (r.message) {
                                        frappe.show_alert({
                                            message: __('Item approved successfully'),
                                            indicator: 'green'
                                        });
                                        frm.reload_doc();
                                    }
                                }
                            });
                        }
                    );
                }, __('Actions')).addClass('btn-success');
                
                frm.add_custom_button(__('Reject'), function() {
                    let d = new frappe.ui.Dialog({
                        title: __('Reject Item'),
                        fields: [
                            {
                                label: __('Rejection Reason'),
                                fieldname: 'reason',
                                fieldtype: 'Small Text',
                                reqd: 1
                            }
                        ],
                        primary_action_label: __('Reject'),
                        primary_action: function() {
                            let values = d.get_values();
                            frappe.call({
                                method: 'rental_management.utils.item_hooks.reject_item_from_form',
                                args: {
                                    item_code: frm.doc.name,
                                    reason: values.reason
                                },
                                callback: function(r) {
                                    if (r.message) {
                                        frappe.show_alert({
                                            message: __('Item rejected'),
                                            indicator: 'red'
                                        });
                                        frm.reload_doc();
                                        d.hide();
                                    }
                                }
                            });
                        }
                    });
                    d.show();
                }, __('Actions')).addClass('btn-danger');
            }
            
            // Add utilization display for approved rental items
            if (frm.doc.is_rental_item && frm.doc.approval_status === 'Approved') {
                frm.add_custom_button(__('Show Utilization'), function() {
                    frappe.call({
                        method: 'rental_management.utils.item_utils.calculate_item_utilization',
                        args: {
                            item_code: frm.doc.name
                        },
                        callback: function(r) {
                            if (r.message !== undefined) {
                                frappe.msgprint(__('Item utilization in last 3 months: {0}%', [r.message.toFixed(1)]));
                            }
                        }
                    });
                }, __('Reports'));
            }
        }
    });
    
    // Auto-refresh pending approval count in sidebar
    if (frappe.route_hooks) {
        frappe.route_hooks.after_load = function() {
            if (frappe.get_route()[0] === 'List' && frappe.get_route()[1] === 'Item') {
                frappe.call({
                    method: 'rental_management.utils.item_hooks.get_pending_approval_count',
                    callback: function(r) {
                        if (r.message > 0) {
                            frappe.show_alert({
                                message: __('You have {0} rental items pending approval', [r.message]),
                                indicator: 'orange'
                            });
                        }
                    }
                });
            }
        };
    }
    """
