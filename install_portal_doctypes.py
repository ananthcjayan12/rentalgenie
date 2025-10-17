#!/usr/bin/env python3

import frappe

def install_portal_doctypes():
    """Install Portal Banner and Portal Category doctypes"""
    
    print("Installing Portal Banner and Portal Category DocTypes...")
    
    try:
        # Create sample portal banners
        if not frappe.db.exists("Portal Banner", "Welcome Banner"):
            banner = frappe.get_doc({
                "doctype": "Portal Banner",
                "title": "Welcome Banner",
                "subtitle": "Discover our premium rental collection",
                "button_text": "Shop Now",
                "button_link": "/portal/category",
                "is_active": 1,
                "display_order": 1
            })
            banner.save()
            print("✓ Created sample Portal Banner")
        
        # Create sample portal categories
        categories = [
            {"name": "Lehenga", "icon": "fa-person-dress"},
            {"name": "Gown", "icon": "fa-person-dress"},
            {"name": "Saree", "icon": "fa-person-dress"},
            {"name": "Jewellery", "icon": "fa-gem"},
            {"name": "Ornament", "icon": "fa-gem"},
            {"name": "Bracelet", "icon": "fa-gem"},
            {"name": "Accessory", "icon": "fa-star"}
        ]
        
        for i, cat in enumerate(categories):
            if not frappe.db.exists("Portal Category", cat["name"]):
                category = frappe.get_doc({
                    "doctype": "Portal Category",
                    "category_name": cat["name"],
                    "icon": cat["icon"],
                    "is_active": 1,
                    "display_order": i + 1
                })
                category.save()
                print(f"✓ Created Portal Category: {cat['name']}")
        
        frappe.db.commit()
        print("✓ Portal DocTypes installation completed successfully!")
        
    except Exception as e:
        print(f"✗ Error installing portal doctypes: {str(e)}")
        frappe.db.rollback()

if __name__ == "__main__":
    install_portal_doctypes()
