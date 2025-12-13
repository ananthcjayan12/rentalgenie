import frappe
from frappe.utils import formatdate, flt

def get_context(context):
    """Get context for print invoice page"""
    
    context.no_cache = 1
    
    # Get booking ID from URL
    booking_id = frappe.form_dict.get('booking', '')
    
    if not booking_id:
        context.error = "No booking ID provided"
        return context
    
    try:
        # Get invoice details
        invoice = frappe.get_doc("Sales Invoice", booking_id)
        
        # Get company details
        company = frappe.get_doc("Company", invoice.company)
        
        # Get customer details
        customer = frappe.get_doc("Customer", invoice.customer)
        
        # Get customer address if available
        customer_address = None
        if customer.customer_primary_address:
            try:
                customer_address = frappe.get_doc("Address", customer.customer_primary_address)
            except:
                pass
        
        # Format dates
        invoice_date = formatdate(invoice.posting_date, "dd MMM yyyy")
        
        # Calculate rental period
        rental_start = formatdate(invoice.rental_start_date, "dd MMM yyyy") if invoice.rental_start_date else ""
        rental_end = formatdate(invoice.rental_end_date, "dd MMM yyyy") if invoice.rental_end_date else ""
        function_date = formatdate(invoice.function_date, "dd MMM yyyy") if invoice.function_date else ""
        
        # Get items with details
        items = []
        for item in invoice.items:
            items.append({
                "item_code": item.item_code,
                "item_name": item.item_name or item.item_code,
                "description": item.description or "",
                "qty": item.qty,
                "rate": flt(item.rate),
                "amount": flt(item.amount)
            })
        
        # Calculate totals
        subtotal = flt(invoice.total)
        tax_amount = flt(invoice.total_taxes_and_charges or 0)
        grand_total = flt(invoice.grand_total)
        advance_paid = flt(invoice.advance_amount or 0)
        balance_due = grand_total - advance_paid
        caution_deposit = flt(invoice.caution_deposit_amount or 0)
        
        context.invoice = invoice
        context.company = company
        context.customer = customer
        context.customer_address = customer_address
        context.items = items
        context.invoice_date = invoice_date
        context.rental_start = rental_start
        context.rental_end = rental_end
        context.function_date = function_date
        context.subtotal = subtotal
        context.tax_amount = tax_amount
        context.grand_total = grand_total
        context.advance_paid = advance_paid
        context.balance_due = balance_due
        context.caution_deposit = caution_deposit
        
        context.page_title = f"Invoice #{booking_id}"
        
    except Exception as e:
        frappe.log_error(f"Error loading invoice {booking_id}: {str(e)}")
        context.error = f"Error loading invoice: {str(e)}"
    
    return context
