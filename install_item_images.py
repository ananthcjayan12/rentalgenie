#!/usr/bin/env python3

"""
Script to install Item Images functionality and migrate existing images
"""

import frappe
from frappe import _

def install_item_images():
    """Install item images functionality"""
    print("Installing Item Images functionality...")
    
    # 1. Create custom fields
    from rental_management.custom_fields.item_fields import create_item_custom_fields
    create_item_custom_fields()
    print("✅ Custom fields created")
    
    # 2. Migrate existing images to Item Image child table
    migrate_existing_images()
    print("✅ Existing images migrated")
    
    # 3. Update service items with images
    update_service_items_with_images()
    print("✅ Service items updated with images")
    
    print("🎉 Item Images functionality installed successfully!")

def migrate_existing_images():
    """Migrate existing single images to Item Image child table"""
    print("Migrating existing images...")
    
    # Get all items with images
    items_with_images = frappe.db.sql("""
        SELECT name, image, item_name
        FROM `tabItem`
        WHERE image IS NOT NULL AND image != ''
        AND is_rental_item = 1
    """, as_dict=True)
    
    migrated_count = 0
    
    for item in items_with_images:
        try:
            # Check if already exists in Item Image table
            existing = frappe.db.exists("Item Image", {
                "item": item.name,
                "image": item.image
            })
            
            if not existing:
                # Create Item Image record
                item_image = frappe.get_doc({
                    "doctype": "Item Image",
                    "item": item.name,
                    "image": item.image,
                    "image_description": f"Main image for {item.item_name}",
                    "is_primary": 1,
                    "display_order": 1
                })
                item_image.insert()
                migrated_count += 1
                
        except Exception as e:
            print(f"Error migrating image for {item.name}: {str(e)}")
            continue
    
    print(f"Migrated {migrated_count} images to Item Image table")

def update_service_items_with_images():
    """Update service items to have images from their main items"""
    print("Updating service items with images...")
    
    # Get all rental items that have service items
    rental_items = frappe.db.sql("""
        SELECT name, rental_service_item, item_name
        FROM `tabItem`
        WHERE is_rental_item = 1 
        AND rental_service_item IS NOT NULL
        AND rental_service_item != ''
    """, as_dict=True)
    
    updated_count = 0
    
    for item in rental_items:
        try:
            if frappe.db.exists("Item", item.rental_service_item):
                # Copy images from main item to service item
                from rental_management.automations.item_automation import copy_item_images
                copy_item_images(item.name, item.rental_service_item)
                updated_count += 1
                
        except Exception as e:
            print(f"Error updating service item images for {item.name}: {str(e)}")
            continue
    
    print(f"Updated {updated_count} service items with images")

if __name__ == "__main__":
    frappe.init()
    frappe.connect()
    
    try:
        install_item_images()
    except Exception as e:
        print(f"Error: {str(e)}")
        frappe.db.rollback()
    else:
        frappe.db.commit()
    finally:
        frappe.destroy()
