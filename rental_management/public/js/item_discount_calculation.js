/**
 * Auto-calculate discount percentage for rental items
 */

frappe.ui.form.on('Item', {
    rental_mrp_per_day: function(frm) {
        calculate_discount_percentage(frm);
    },
    
    rental_rate_per_day: function(frm) {
        calculate_discount_percentage(frm);
    }
});

function calculate_discount_percentage(frm) {
    const mrp = frm.doc.rental_mrp_per_day;
    const rate = frm.doc.rental_rate_per_day;
    
    if (mrp && rate && mrp > 0) {
        const discount = ((mrp - rate) / mrp) * 100;
        frm.set_value('discount_percentage', Math.round(discount * 100) / 100);
    } else {
        frm.set_value('discount_percentage', 0);
    }
}