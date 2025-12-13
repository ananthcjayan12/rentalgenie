
import frappe

def create_rental_invoice_format():
    html_content = """
<div class="print-format">
    <!-- Header -->
    <div class="row section-break">
        <div class="col-xs-12">
            <h1 style="text-align: center;">RENTAL INVOICE</h1>
            <div style="text-align: center;">
                <p>{{ frappe.db.get_value("Company", doc.company, "country") or "" }}</p>
            </div>
        </div>
    </div>
    
    <hr>
    
    <!-- Info -->
    <div class="row">
        <div class="col-xs-6">
            <p><strong>Invoice#:</strong> {{ doc.name }}</p>
            <p><strong>Date:</strong> {{ doc.posting_date }}</p>
            <p><strong>Booking Status:</strong> {{ doc.booking_status or "Draft" }}</p>
        </div>
        <div class="col-xs-6" style="text-align: right;">
            <p><strong>Customer:</strong> {{ doc.customer_name }}</p>
            <p><strong>Rental Period:</strong><br>
               From: {{ doc.rental_start_date or "N/A" }}<br>
               To: {{ doc.rental_end_date or "N/A" }}
            </p>
        </div>
    </div>
    
    <!-- Items -->
    <table class="table table-bordered table-condensed">
        <thead>
            <tr>
                <th>Item</th>
                <th class="text-right">Rate</th>
                <th class="text-right">Days</th>
                <th class="text-right">Qty</th>
                <th class="text-right">Amount</th>
            </tr>
        </thead>
        <tbody>
            {% for item in doc.items %}
            <tr>
                <td>
                    <b>{{ item.item_name }}</b><br>
                    <small>{{ item.description }}</small>
                </td>
                <td class="text-right">{{ item.get_formatted("rate") }}</td>
                <td class="text-right">{{ doc.rental_duration_days }}</td>
                <td class="text-right">{{ item.qty }}</td>
                <td class="text-right">{{ item.get_formatted("amount") }}</td>
            </tr>
            {% endfor %}
        </tbody>
        <tfoot>
            <tr>
                <td colspan="4" class="text-right"><b>Total</b></td>
                <td class="text-right"><b>{{ doc.get_formatted("total") }}</b></td>
            </tr>
            {% if doc.discount_amount %}
            <tr>
                <td colspan="4" class="text-right">Discount</td>
                <td class="text-right">{{ doc.get_formatted("discount_amount") }}</td>
            </tr>
            {% endif %}
            {% if doc.total_taxes_and_charges %}
            <tr>
                <td colspan="4" class="text-right">Tax</td>
                <td class="text-right">{{ doc.get_formatted("total_taxes_and_charges") }}</td>
            </tr>
            {% endif %}
             <tr>
                <td colspan="4" class="text-right"><b>Grand Total</b></td>
                <td class="text-right"><b>{{ doc.get_formatted("grand_total") }}</b></td>
            </tr>
        </tfoot>
    </table>
    
    <!-- Footer -->
    <div class="row section-break">
        <div class="col-xs-12">
            {% if doc.terms %}
            <p><strong>Terms and Conditions:</strong></p>
            <div>{{ doc.terms }}</div>
            {% endif %}
            <p style="text-align: center; margin-top: 50px;">Thank you for your business!</p>
        </div>
    </div>
</div>
    """
    
    if not frappe.db.exists("Print Format", "Rental Invoice"):
        pf = frappe.new_doc("Print Format")
        pf.name = "Rental Invoice"
        pf.doc_type = "Sales Invoice"
        pf.module = "Rental Management"
        pf.standard = "No"  # Custom format
        pf.custom_format = 1
        pf.print_format_type = "Jinja"
        pf.html = html_content
        pf.insert()
        print("Rental Invoice Print Format created.")
    else:
        pf = frappe.get_doc("Print Format", "Rental Invoice")
        pf.html = html_content
        pf.save()
        print("Rental Invoice Print Format updated.")

if __name__ == "__main__":
    create_rental_invoice_format()
