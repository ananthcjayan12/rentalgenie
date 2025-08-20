import frappe
from frappe import _
from frappe.utils import cstr, flt

def auto_create_supplier_for_item(item_doc):
    """Auto-create supplier for third-party rental items"""
    if not item_doc.is_third_party_item:
        return None
    
    try:
        # Generate supplier name based on item code and name
        supplier_name = f"Owner-{item_doc.item_code}"
        
        # Check if supplier already exists
        if frappe.db.exists("Supplier", supplier_name):
            return supplier_name
        
        # Create new supplier
        supplier = frappe.get_doc({
            "doctype": "Supplier",
            "supplier_name": supplier_name,
            "supplier_type": "Individual",
            "supplier_group": "Local"
        })
        supplier.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return supplier.name
        
    except Exception as e:
        frappe.log_error(f"Error creating supplier for item {item_doc.name}: {str(e)}")
        return None

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
        
        # Set item category based on item group if not already set
        if not doc.rental_item_type and doc.item_group:
            if "dress" in doc.item_group.lower():
                doc.rental_item_type = "Dress"
            elif "ornament" in doc.item_group.lower():
                doc.rental_item_type = "Ornament"
            elif "accessor" in doc.item_group.lower():
                doc.rental_item_type = "Accessory"
            else:
                doc.rental_item_type = "Other"
        
        # Set default item group based on category if needed
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
        rental_rate = flt(doc.rental_rate_per_day)
        if not rental_rate or rental_rate <= 0:
            frappe.throw(_("Rental Rate Per Day is mandatory for rental items"))
        
        # Enhanced validations for third-party items
        if doc.is_third_party_item:
            commission_percent = flt(doc.owner_commission_percent)
            if not commission_percent or commission_percent <= 0:
                frappe.throw(_("Owner Commission % is mandatory for third-party items"))
            
            if commission_percent > 100:
                frappe.throw(_("Owner Commission % cannot exceed 100%"))
                
            # Auto-create/assign supplier if not already set
            if not doc.third_party_supplier:
                supplier_name = auto_create_supplier_for_item(doc)
                if supplier_name:
                    doc.third_party_supplier = supplier_name
        
        # Clear supplier if not a third-party item
        if not doc.is_third_party_item:
            doc.third_party_supplier = ""
            doc.owner_commission_percent = 0
        
        # Auto-generate item description if not provided
        if not doc.description:
            category = doc.rental_item_type or "Item"
            party_type = "Third-party" if doc.is_third_party_item else "In-house"
            doc.description = f"{party_type} {category} available for rental at ₹{doc.rental_rate_per_day}/day"
        
        # Set default approval status for new items
        if not doc.approval_status:
            doc.approval_status = "Pending Approval"
    
    # For non-rental items, ensure rental fields are cleared
    else:
        doc.rental_rate_per_day = 0
        doc.rental_item_type = ""
        doc.current_rental_status = ""
        doc.approval_status = ""
        doc.is_third_party_item = 0
        doc.owner_commission_percent = 0
        doc.third_party_supplier = ""

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
        "description": f"Rental service for {item_doc.item_name}"
    })
    service_item.insert()
    
    # Create Item Price for the service item
    if item_doc.rental_rate_per_day:
        item_price = frappe.get_doc({
            "doctype": "Item Price",
            "item_code": service_item_code,
            "price_list": "Standard Selling",
            "price_list_rate": item_doc.rental_rate_per_day,
            "currency": frappe.defaults.get_global_default("currency") or "INR"
        })
        item_price.insert()
    
    # Link service item back to original item
    frappe.db.set_value("Item", item_doc.name, "rental_service_item", service_item.name)

def handle_third_party_supplier(item_doc):
    """Handle supplier creation for third-party items - only if not already done in before_save"""
    if not item_doc.is_third_party_item:
        return
    
    # If supplier is already set, no need to create again
    if item_doc.third_party_supplier and frappe.db.exists("Supplier", item_doc.third_party_supplier):
        return
    
    # Create supplier if not already done
    supplier_name = auto_create_supplier_for_item(item_doc)
    if supplier_name and supplier_name != item_doc.third_party_supplier:
        # Update the item document with the supplier reference
        frappe.db.set_value("Item", item_doc.name, "third_party_supplier", supplier_name)
        frappe.db.commit()

def create_initial_stock_entry(item_doc):
    """Create initial stock entry for the rental item"""
    if not item_doc.is_rental_item:
        return
    
    try:
        # Get default company
        company = frappe.defaults.get_global_default("company")
        if not company:
            # Get the first company if no default
            company = frappe.db.get_value("Company", {}, "name")
        
        if not company:
            frappe.log_error(f"No company found. Cannot create stock entry for {item_doc.name}")
            return
        
        # Try to find a rental warehouse first, otherwise use any warehouse
        rental_warehouse = f"Rental Store - {company}"
        if not frappe.db.exists("Warehouse", rental_warehouse):
            # Get any warehouse for the company
            rental_warehouse = frappe.db.get_value("Warehouse", 
                                                 {"company": company, "is_group": 0}, 
                                                 "name")
        
        if not rental_warehouse:
            frappe.log_error(f"No warehouse found for company {company}. Cannot create stock entry for {item_doc.name}")
            return
        
        # Get cost center
        cost_center = frappe.db.get_value("Company", company, "cost_center")
        if not cost_center:
            cost_center = frappe.db.get_value("Cost Center", {"company": company}, "name")
        
        # Calculate basic rate (use rental rate * 30 as estimated value)
        basic_rate = float(item_doc.rental_rate_per_day or 0) * 30
        if basic_rate <= 0:
            basic_rate = 1000  # Default fallback value
        
        # Create stock entry for initial inventory
        stock_entry = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "company": company,
            "title": f"Initial Stock - {item_doc.item_name}",
            "items": [{
                "item_code": item_doc.item_code,
                "qty": 1,  # Default quantity for rental items
                "t_warehouse": rental_warehouse,
                "basic_rate": basic_rate,
                "uom": item_doc.stock_uom or "Nos"
            }]
        })
        
        # Add cost center if available
        if cost_center:
            stock_entry.items[0].cost_center = cost_center
        
        stock_entry.insert()
        # Auto-submit the stock entry
        stock_entry.submit()
        
        frappe.msgprint(f"✅ Initial stock entry created: {stock_entry.name}")
        
    except Exception as e:
        error_msg = f"Error creating stock entry for {item_doc.name}: {str(e)}"
        frappe.log_error(error_msg)
        frappe.msgprint(f"⚠️ Warning: Could not create initial stock entry. Error: {str(e)}", alert=True)
