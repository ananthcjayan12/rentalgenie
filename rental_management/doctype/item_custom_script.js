// Custom script for Item doctype to handle Third Party Owner auto-creation

frappe.ui.form.on('Item', {
    owner_supplier_source: function(frm) {
        if (frm.doc.owner_supplier_source && frm.doc.is_third_party_item) {
            // Auto-create Third Party Owner from Supplier
            frappe.call({
                method: "rental_management.doctype.third_party_owner.third_party_owner.create_third_party_owner_from_supplier",
                args: {
                    supplier_name: frm.doc.owner_supplier_source
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('third_party_owner', r.message);
                        frappe.show_alert({
                            message: __('Third Party Owner created/linked successfully'),
                            indicator: 'green'
                        });
                    }
                }
            });
        }
    },
    
    is_third_party_item: function(frm) {
        if (!frm.doc.is_third_party_item) {
            // Clear fields when unchecked
            frm.set_value('third_party_owner', '');
            frm.set_value('owner_supplier_source', '');
            frm.set_value('owner_commission_percent', 0);
        }
    }
});
