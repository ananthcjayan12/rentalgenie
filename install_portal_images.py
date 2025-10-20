#!/usr/bin/env python3

"""
Quick Installation script for Portal Image Upload functionality
This script calls the main installation functions that are now integrated
into the Rental Management app's install.py
"""

import frappe

def install_portal_functionality():
    """Install portal banner and category image functionality"""
    print("🚀 Installing Portal Image Upload functionality...")
    print("=" * 50)
    
    try:
        # Import the installation functions
        from rental_management.custom_fields.item_group_fields import create_item_group_custom_fields, update_existing_item_groups
        from rental_management.setup.install import setup_portal_banners, create_rental_item_groups
        
        # Install Item Group portal fields
        print("📋 Installing Item Group portal fields...")
        create_item_group_custom_fields()
        
        # Update existing item groups
        print("🔄 Updating existing Item Groups...")
        update_existing_item_groups()
        
        # Setup portal banners
        print("🎨 Setting up Portal Banners...")
        setup_portal_banners()
        
        # Ensure rental item groups exist with portal settings
        print("📁 Creating/updating rental item groups...")
        create_rental_item_groups()
        
        print("\n" + "=" * 50)
        print("🎉 Installation completed!")
        print("\n📋 Next Steps:")
        print("1. Go to Portal Banner list to upload banner images: /app/portal-banner")
        print("2. Go to Item Group list to configure category images: /app/item-group")
        print("3. Refresh your portal to see the changes")
        
    except ImportError as e:
        print(f"❌ Error importing installation functions: {e}")
        print("Make sure the Rental Management app is properly installed")
    except Exception as e:
        print(f"❌ Installation error: {e}")
        frappe.log_error(f"Portal installation error: {str(e)}")

def main():
    """Main function - can be called standalone or from console"""
    if not frappe.db:
        print("Connecting to Frappe...")
        frappe.connect()
    
    install_portal_functionality()

if __name__ == "__main__":
    main()