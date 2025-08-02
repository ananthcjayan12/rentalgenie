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
