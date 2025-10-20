import frappe
from frappe import _

def get_context(context):
    """Context for Add Item page"""
    context.page_title = "Add New Item"
    context.meta_description = "Add new rental items to inventory"
    
    # Get item groups for dropdown
    context.item_groups = frappe.get_all(
        "Item Group", 
        filters={"is_group": 0}, 
        fields=["name", "item_group_name"], 
        order_by="item_group_name"
    )
    
    # Get existing suppliers for dropdown
    context.suppliers = frappe.get_all(
        "Supplier",
        fields=["name", "supplier_name"],
        order_by="supplier_name"
    )
    
    return context