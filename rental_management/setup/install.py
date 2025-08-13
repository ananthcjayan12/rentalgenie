import frappe
from rental_management.custom_fields.item_fields import create_item_custom_fields
from rental_management.custom_fields.customer_fields import create_customer_custom_fields
from rental_management.custom_fields.sales_invoice_fields import create_sales_invoice_custom_fields

def after_install():
    """Setup custom fields and configurations after app installation"""
    print("Setting up Rental Management...")
    
    # Create custom fields
    create_item_custom_fields()
    create_customer_custom_fields()
    create_sales_invoice_custom_fields()
    
    # Create default item groups if they don't exist
    create_rental_item_groups()
    
    # Setup default accounts template
    setup_rental_accounts()
    
    # Create default warehouses for rental items
    create_rental_warehouses()
    
    print("Rental Management setup completed!")

def create_rental_item_groups():
    """Create rental-specific item groups"""
    item_groups = [
        {"item_group_name": "Rental Items", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Women's Wear", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Men's Wear", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Jewelry", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Footwear", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Dresses", "parent_item_group": "Women's Wear"},
        {"item_group_name": "Ornaments", "parent_item_group": "Jewelry"}
    ]
    
    for group in item_groups:
        if not frappe.db.exists("Item Group", group["item_group_name"]):
            item_group = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": group["item_group_name"],
                "parent_item_group": group["parent_item_group"],
                "is_group": 1 if group["item_group_name"] == "Rental Items" else 0
            })
            item_group.insert()
            print(f"Created Item Group: {group['item_group_name']}")

def setup_rental_accounts():
    """Setup rental-specific account templates"""
    # This will be expanded in later phases
    pass

def create_rental_warehouses():
    """Create default warehouses for rental inventory management"""
    try:
        # Get all companies (removed disabled filter as it doesn't exist)
        companies = frappe.get_all("Company", fields=["name"])
        
        if not companies:
            print("No companies found. Skipping warehouse creation.")
            return
        
        warehouses = [
            {"warehouse_name": "Rental Store"},
            {"warehouse_name": "Rental Display"},
            {"warehouse_name": "Rental Maintenance"}
        ]
        
        for company_doc in companies:
            company = company_doc.name
            print(f"Creating warehouses for company: {company}")
            
            for wh in warehouses:
                warehouse_name = wh['warehouse_name']
                full_warehouse_name = f"{warehouse_name} - {company}"
                
                if not frappe.db.exists("Warehouse", full_warehouse_name):
                    try:
                        warehouse = frappe.get_doc({
                            "doctype": "Warehouse",
                            "warehouse_name": warehouse_name,
                            "company": company,
                            "is_group": 0
                        })
                        warehouse.insert()
                        frappe.db.commit()
                        print(f"✅ Created warehouse: {full_warehouse_name}")
                    except Exception as e:
                        print(f"❌ Error creating warehouse {full_warehouse_name}: {str(e)}")
                else:
                    print(f"⚠️ Warehouse already exists: {full_warehouse_name}")
    
    except Exception as e:
        print(f"❌ Error in warehouse creation process: {str(e)}")
        frappe.log_error(f"Warehouse creation error: {str(e)}")

def create_warehouses_manually():
    """Manual function to create warehouses - can be called from console"""
    create_rental_warehouses()

def setup_item_groups():
    """Standalone function to setup item groups"""
    create_rental_item_groups()
    frappe.db.commit()
    print("Item groups setup completed!")
