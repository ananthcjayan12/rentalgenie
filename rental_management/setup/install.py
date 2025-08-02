import frappe
from rental_management.custom_fields.item_fields import create_item_custom_fields

def after_install():
    """Setup custom fields and configurations after app installation"""
    print("Setting up Rental Management...")
    
    # Create custom fields
    create_item_custom_fields()
    
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
        {"item_group_name": "Dresses", "parent_item_group": "Rental Items"},
        {"item_group_name": "Ornaments", "parent_item_group": "Rental Items"},
        {"item_group_name": "Accessories", "parent_item_group": "Rental Items"}
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

def setup_rental_accounts():
    """Setup rental-specific account templates"""
    # This will be expanded in later phases
    pass

def create_rental_warehouses():
    """Create default warehouses for rental inventory management"""
    try:
        company = frappe.defaults.get_global_default("company")
        if not company:
            company = frappe.db.get_value("Company", {"disabled": 0}, "name")
        
        if not company:
            print("No company found. Skipping warehouse creation.")
            return
        
        warehouses = [
            {"warehouse_name": "Rental Store", "warehouse_type": "Stock"},
            {"warehouse_name": "Rental Display", "warehouse_type": "Stock"},
            {"warehouse_name": "Rental Maintenance", "warehouse_type": "Stock"}
        ]
        
        for wh in warehouses:
            full_warehouse_name = f"{wh['warehouse_name']} - {company}"
            if not frappe.db.exists("Warehouse", full_warehouse_name):
                warehouse = frappe.get_doc({
                    "doctype": "Warehouse",
                    "warehouse_name": wh['warehouse_name'],
                    "company": company,
                    "warehouse_type": wh['warehouse_type'],
                    "is_group": 0
                })
                warehouse.insert()
                print(f"Created warehouse: {full_warehouse_name}")
    
    except Exception as e:
        print(f"Error creating warehouses: {str(e)}")
