import frappe
from frappe import _
from frappe.utils import cstr

def before_item_save(doc, method):
    """Validate and set defaults for rental items"""
    if doc.is_rental_item:
        # Set mandatory fields for rental items
        doc.is_stock_item = 1  # Must maintain stock
        doc.include_item_in_manufacturing = 0  # Not a manufacturing item
        doc.is_fixed_asset = 0  # Not a fixed asset
        
        # Set default UOM if not set
        if not doc.stock_uom:
            doc.stock_uom = "Nos"
        
        # Set default item group
        if not doc.item_group or doc.item_group == "All Item Groups":
            if doc.rental_item_type:
                if doc.rental_item_type in ["Dress", "Dresses"]:
                    doc.item_group = "Dresses"
                elif doc.rental_item_type in ["Ornament", "Ornaments"]:
                    doc.item_group = "Ornaments"
                elif doc.rental_item_type in ["Accessory", "Accessories"]:
                    doc.item_group = "Accessories"
                else:
                    doc.item_group = "Rental Items"
        
        # Validate rental rate
        if not doc.rental_rate_per_day or doc.rental_rate_per_day <= 0:
            frappe.throw(_("Rental Rate Per Day is mandatory for rental items"))
    
    # Item automation logic here - no automatic caution deposit calculation
    # Caution deposit is manually entered by salesman at invoice level

def after_item_insert(doc, method):
    """Perform post-creation tasks for rental items"""
    if doc.is_rental_item:
        try:
            # 1. Create rental service item
            create_rental_service_item(doc)
            
            # 2. Handle third party supplier creation
            if doc.is_third_party_item:
                handle_third_party_supplier(doc)
            
            # 3. Create initial stock entry
            create_initial_stock_entry(doc)
            
        except Exception as e:
            frappe.log_error(f"Error in after_item_insert for {doc.name}: {str(e)}")

def create_rental_service_item(item_doc):
    """Create corresponding service item for rental billing"""
    service_item_code = f"{item_doc.item_code}-RENTAL"
    
    # Check if service item already exists
    if frappe.db.exists("Item", service_item_code):
        return
    
    service_item = frappe.get_doc({
        "doctype": "Item",
        "item_code": service_item_code,
        "item_name": f"{item_doc.item_name} - Rental Service",
        "item_group": "Services",
        "stock_uom": "Nos",
        "is_stock_item": 0,  # Service item
        "is_sales_item": 1,
        "include_item_in_manufacturing": 0,
        "description": f"Rental service for {item_doc.item_name}",
        "standard_rate": item_doc.rental_rate_per_day
    })
    service_item.insert()
    
    # Link service item back to original item
    frappe.db.set_value("Item", item_doc.name, "rental_service_item", service_item.name)

def handle_third_party_supplier(item_doc):
    """Create or link third party supplier"""
    if not item_doc.third_party_supplier:
        # Auto-create supplier if not provided
        supplier_name = f"Owner-{item_doc.item_code}"
        
        if not frappe.db.exists("Supplier", supplier_name):
            supplier = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": supplier_name,
                "supplier_type": "Individual",
                "supplier_group": "Local"
            })
            supplier.insert()
            
            # Update item with supplier reference
            frappe.db.set_value("Item", item_doc.name, "third_party_supplier", supplier.name)

def create_initial_stock_entry(item_doc):
    """Create initial stock entry for the rental item"""
    # We'll implement this when we handle stock management
    pass
