// Client script for Payment Entry to handle rental booking payments
frappe.ui.form.on('Payment Entry', {
    refresh: function(frm) {
        // Add custom button for rental bookings
        if (frm.doc.party_type === 'Customer' && frm.doc.payment_type === 'Receive') {
            frm.add_custom_button(__('Get Rental Pending Amount'), function() {
                get_rental_pending_amount(frm);
            });
        }
    },
    
    party: function(frm) {
        if (frm.doc.party_type === 'Customer' && frm.doc.party) {
            // Check if this is for a rental booking and update amounts accordingly
            check_rental_outstanding(frm);
        }
    }
});

frappe.ui.form.on('Payment Entry Reference', {
    reference_name: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.reference_doctype === 'Sales Invoice' && row.reference_name) {
            // Check if this is a rental booking and adjust outstanding amount
            frappe.call({
                method: 'rental_management.automations.booking_automation.get_pending_amount',
                args: {
                    sales_invoice_name: row.reference_name
                },
                callback: function(r) {
                    if (r.message && !r.message.error) {
                        // Update the allocated amount to show pending amount instead of full outstanding
                        frappe.model.set_value(cdt, cdn, 'outstanding_amount', r.message.pending_amount);
                        frappe.model.set_value(cdt, cdn, 'allocated_amount', r.message.pending_amount);
                        
                        // Show details in a message
                        frappe.msgprint({
                            title: __('Rental Booking Payment Details'),
                            message: `
                                <div>
                                    <p><strong>Total Amount:</strong> ${format_currency(r.message.total_amount)}</p>
                                    <p><strong>Advance Paid:</strong> ${format_currency(r.message.advance_amount)}</p>
                                    <p><strong>Caution Deposit:</strong> ${format_currency(r.message.caution_deposit)}</p>
                                    <p><strong>Pending Amount:</strong> ${format_currency(r.message.pending_amount)}</p>
                                </div>
                            `,
                            indicator: 'blue'
                        });
                    }
                }
            });
        }
    }
});

function get_rental_pending_amount(frm) {
    let dialog = new frappe.ui.Dialog({
        title: __('Get Rental Booking Pending Amount'),
        fields: [
            {
                label: __('Sales Invoice'),
                fieldname: 'sales_invoice',
                fieldtype: 'Link',
                options: 'Sales Invoice',
                get_query: function() {
                    return {
                        filters: {
                            'is_rental_booking': 1,
                            'docstatus': 1,
                            'customer': frm.doc.party
                        }
                    };
                },
                reqd: 1
            }
        ],
        primary_action: function(values) {
            frappe.call({
                method: 'rental_management.automations.booking_automation.get_pending_amount',
                args: {
                    sales_invoice_name: values.sales_invoice
                },
                callback: function(r) {
                    if (r.message && !r.message.error) {
                        // Clear existing references
                        frm.clear_table('references');
                        
                        // Add the rental booking with pending amount
                        let row = frm.add_child('references');
                        row.reference_doctype = 'Sales Invoice';
                        row.reference_name = values.sales_invoice;
                        row.outstanding_amount = r.message.pending_amount;
                        row.allocated_amount = r.message.pending_amount;
                        
                        // Update payment amounts
                        frm.set_value('paid_amount', r.message.pending_amount);
                        frm.set_value('received_amount', r.message.pending_amount);
                        
                        frm.refresh_fields();
                        
                        frappe.msgprint({
                            title: __('Rental Payment Details Loaded'),
                            message: `
                                <div>
                                    <p><strong>Total Invoice:</strong> ${format_currency(r.message.total_amount)}</p>
                                    <p><strong>Advance Paid:</strong> ${format_currency(r.message.advance_amount)}</p>
                                    <p><strong>Caution Deposit:</strong> ${format_currency(r.message.caution_deposit)}</p>
                                    <p><strong>Pending Amount:</strong> ${format_currency(r.message.pending_amount)}</p>
                                </div>
                            `,
                            indicator: 'green'
                        });
                        
                        dialog.hide();
                    } else {
                        frappe.msgprint(__('Error: ') + (r.message.error || 'Unknown error'));
                    }
                }
            });
        }
    });
    
    dialog.show();
}

function check_rental_outstanding(frm) {
    // Auto-check for rental bookings when party is selected
    if (frm.doc.party) {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Sales Invoice',
                filters: {
                    'customer': frm.doc.party,
                    'is_rental_booking': 1,
                    'docstatus': 1,
                    'outstanding_amount': ['>', 0]
                },
                fields: ['name', 'grand_total', 'outstanding_amount', 'advance_amount']
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    frappe.show_alert({
                        message: __(`Found ${r.message.length} rental booking(s) with outstanding amounts. Use "Get Rental Pending Amount" button for accurate payment processing.`),
                        indicator: 'blue'
                    }, 5);
                }
            }
        });
    }
}
