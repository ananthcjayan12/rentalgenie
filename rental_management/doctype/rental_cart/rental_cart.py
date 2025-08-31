import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_days

class RentalCart(Document):
    def validate(self):
        self.calculate_total()
        
    def calculate_total(self):
        """Calculate total amount for cart"""
        total = 0
        for item in self.items:
            total += flt(item.line_total)
        self.total_amount = total
    
    def add_item(self, item_code, rental_start_date, rental_end_date, function_date=None):
        """Add item to cart"""
        # Check if item already exists in cart
        existing_item = None
        for cart_item in self.items:
            if cart_item.item_code == item_code:
                existing_item = cart_item
                break
        
        # Get item details
        item_doc = frappe.get_doc("Item", item_code)
        
        # Calculate rental days and amount
        start_date = getdate(rental_start_date)
        end_date = getdate(rental_end_date)
        rental_days = (end_date - start_date).days + 1
        line_total = item_doc.rental_rate_per_day * rental_days
        
        if existing_item:
            # Update existing item
            existing_item.rental_start_date = rental_start_date
            existing_item.rental_end_date = rental_end_date
            existing_item.function_date = function_date
            existing_item.rental_days = rental_days
            existing_item.line_total = line_total
        else:
            # Add new item
            self.append("items", {
                "item_code": item_code,
                "item_name": item_doc.item_name,
                "rental_rate_per_day": item_doc.rental_rate_per_day,
                "rental_start_date": rental_start_date,
                "rental_end_date": rental_end_date,
                "function_date": function_date,
                "rental_days": rental_days,
                "line_total": line_total,
                "service_item_code": item_doc.rental_service_item
            })
        
        self.save()
    
    def remove_item(self, item_code):
        """Remove item from cart"""
        items_to_remove = []
        for i, item in enumerate(self.items):
            if item.item_code == item_code:
                items_to_remove.append(i)
        
        # Remove items in reverse order to maintain indices
        for i in reversed(items_to_remove):
            self.items.pop(i)
        
        self.save()
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.items = []
        self.save()
    
    def convert_to_booking(self, delivery_details):
        """Convert cart to Sales Invoice"""
        if not self.items:
            frappe.throw("Cart is empty")
        
        # Create Sales Invoice
        invoice_doc = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": self.customer,
            "is_rental_booking": 1,
            "posting_date": frappe.utils.today(),
            "items": []
        })
        
        # Add items to invoice
        for cart_item in self.items:
            invoice_doc.append("items", {
                "item_code": cart_item.service_item_code or cart_item.item_code,
                "qty": 1,
                "rate": cart_item.line_total,
                "amount": cart_item.line_total
            })
            
            # Set rental dates from first item (assuming all items have same dates)
            if not invoice_doc.get("function_date") and cart_item.function_date:
                invoice_doc.function_date = cart_item.function_date
                invoice_doc.rental_start_date = cart_item.rental_start_date
                invoice_doc.rental_end_date = cart_item.rental_end_date
                invoice_doc.rental_duration_days = cart_item.rental_days
        
        # Add delivery details if provided
        if delivery_details:
            invoice_doc.update(delivery_details)
        
        # Save and submit invoice
        invoice_doc.insert()
        invoice_doc.submit()
        
        # Mark cart as converted
        self.status = "Converted"
        self.save()
        
        return invoice_doc.name
