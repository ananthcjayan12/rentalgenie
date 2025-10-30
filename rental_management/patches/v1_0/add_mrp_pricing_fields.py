"""
Add MRP pricing fields to existing items
"""

import frappe

def execute():
    """Add MRP pricing fields and update existing rental items"""
    try:
        # First create the custom fields
        from rental_management.custom_fields.item_fields import create_item_custom_fields
        create_item_custom_fields()
        
        # Update existing rental items with sample MRP values
        rental_items = frappe.get_all(
            "Item",
            filters={"is_rental_item": 1},
            fields=["name", "rental_rate_per_day"]
        )
        
        for item in rental_items:
            if item.rental_rate_per_day:
                # Set MRP as 25% higher than current rate for demonstration
                mrp_rate = item.rental_rate_per_day * 1.25  # 25% higher
                discount_percent = 20  # 20% discount
                
                frappe.db.set_value("Item", item.name, {
                    "rental_mrp_per_day": mrp_rate,
                    "discount_percentage": discount_percent
                })
        
        frappe.db.commit()
        print(f"✅ Updated {len(rental_items)} rental items with MRP pricing")
        
    except Exception as e:
        print(f"❌ Error adding MRP pricing: {e}")
        frappe.log_error(f"MRP pricing patch error: {str(e)}")