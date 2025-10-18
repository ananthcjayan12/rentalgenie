import frappe
from rental_management.custom_fields.item_fields import create_item_custom_fields
from rental_management.custom_fields.item_group_fields import create_item_group_custom_fields, update_existing_item_groups
from rental_management.custom_fields.customer_fields import create_customer_custom_fields
from rental_management.custom_fields.sales_invoice_fields import create_sales_invoice_custom_fields

def after_install():
    """Setup custom fields and configurations after app installation"""
    print("Setting up Rental Management...")
    
    # Create custom fields
    create_item_custom_fields()
    create_item_group_custom_fields()  # Portal category fields
    create_customer_custom_fields()
    create_sales_invoice_custom_fields()
    
    # Create default item groups if they don't exist
    create_rental_item_groups()
    
    # Update existing item groups for portal display
    update_existing_item_groups()
    
    # Create Portal Banner DocType and sample data
    setup_portal_banners()
    
    # Setup default accounts template
    setup_rental_accounts()
    
    # Create default warehouses for rental items
    create_rental_warehouses()
    
    # Setup desk customizations and branding
    setup_desk_customization()
    
    # Hide unwanted modules
    hide_unwanted_modules()
    
    print("Rental Management setup completed!")
    print("\n📋 Next Steps:")
    print("1. Upload Blush & Glow logo to: /public/images/blush_glow_logo.png")
    print("2. Go to Portal Banner list to upload banner images: /app/portal-banner")
    print("3. Go to Item Group list to configure category images: /app/item-group")
    print("4. Refresh your browser to see the new desk customizations")
    print("5. Your portal is now ready for image uploads!")

def setup_portal_banners():
    """Create Portal Banner DocType and sample banner"""
    try:
        # Install Portal Banner DocType (should be automatically loaded from JSON)
        if not frappe.db.exists("DocType", "Portal Banner"):
            print("Portal Banner DocType not found - will be loaded from JSON file")
        
        # Create sample banner
        if not frappe.db.exists("Portal Banner", "Welcome Banner"):
            banner = frappe.get_doc({
                "doctype": "Portal Banner",
                "title": "Welcome Banner",
                "subtitle": "Rent premium designer wear for your special occasions",
                "button_text": "Shop Now",
                "button_link": "/portal/category",
                "is_active": 1,
                "display_order": 1
            })
            banner.insert(ignore_permissions=True)
            print("✅ Sample banner created! Add an image to complete setup")
    except Exception as e:
        print(f"❌ Error setting up portal banners: {e}")
        frappe.log_error(f"Portal banner setup error: {str(e)}")

def create_rental_item_groups():
    """Create rental-specific item groups with portal settings"""
    item_groups = [
        {
            "item_group_name": "Rental Items", 
            "parent_item_group": "All Item Groups",
            "is_group": 1,
            "show_in_portal": 0  # Parent group, don't show in portal
        },
        {
            "item_group_name": "Dresses", 
            "parent_item_group": "Rental Items",
            "is_group": 0,
            "show_in_portal": 1,
            "portal_display_order": 1,
            "portal_icon": "fa-person-dress",
            "portal_description": "Designer dresses for special occasions"
        },
        {
            "item_group_name": "Ornaments", 
            "parent_item_group": "Rental Items",
            "is_group": 0,
            "show_in_portal": 1,
            "portal_display_order": 2,
            "portal_icon": "fa-gem",
            "portal_description": "Premium jewelry and ornaments"
        },
        {
            "item_group_name": "Accessories", 
            "parent_item_group": "Rental Items",
            "is_group": 0,
            "show_in_portal": 1,
            "portal_display_order": 3,
            "portal_icon": "fa-star",
            "portal_description": "Bags, shoes and accessories"
        }
    ]
    
    for group in item_groups:
        if not frappe.db.exists("Item Group", group["item_group_name"]):
            item_group = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": group["item_group_name"],
                "parent_item_group": group["parent_item_group"],
                "is_group": group["is_group"],
                "show_in_portal": group["show_in_portal"],
                "portal_display_order": group.get("portal_display_order", 1),
                "portal_icon": group.get("portal_icon", "fa-tag"),
                "portal_description": group.get("portal_description", "")
            })
            item_group.insert()
            print(f"✅ Created item group: {group['item_group_name']}")
        else:
            # Update existing item group with portal settings
            frappe.db.set_value("Item Group", group["item_group_name"], {
                "show_in_portal": group["show_in_portal"],
                "portal_display_order": group.get("portal_display_order", 1),
                "portal_icon": group.get("portal_icon", "fa-tag"),
                "portal_description": group.get("portal_description", "")
            })
            print(f"✅ Updated item group: {group['item_group_name']}")

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

def setup_desk_customization():
    """Setup desk customizations including logo and theme"""
    try:
        print("Setting up desk customizations...")
        
        # Update Website Settings with custom branding
        if frappe.db.exists("Website Settings", "Website Settings"):
            website_settings = frappe.get_doc("Website Settings", "Website Settings")
            website_settings.app_name = "Blush & Glow"
            website_settings.app_logo = "/assets/rental_management/images/blush_glow_logo.png"
            website_settings.brand_html = """
                <div class="app-logo navbar-brand-custom">
                    <img src="/assets/rental_management/images/blush_glow_logo.png" 
                         alt="Blush & Glow" 
                         style="max-height: 40px; width: auto;" />
                </div>
            """
            website_settings.save(ignore_permissions=True)
            print("✅ Website settings updated with Blush & Glow branding")
        
        # Update System Settings
        if frappe.db.exists("System Settings", "System Settings"):
            system_settings = frappe.get_doc("System Settings", "System Settings")
            system_settings.app_name = "Blush & Glow - Rental Management"
            system_settings.save(ignore_permissions=True)
            print("✅ System settings updated")
            
    except Exception as e:
        print(f"❌ Error setting up desk customization: {e}")
        frappe.log_error(f"Desk customization error: {str(e)}")

def hide_unwanted_modules():
    """Hide modules not needed for rental management"""
    try:
        print("Hiding unwanted modules...")
        
        # List of modules to hide
        modules_to_hide = [
            'CRM', 'Projects', 'Support', 'Quality', 'Manufacturing',
            'Buying', 'Selling', 'HR', 'Payroll', 'Assets',
            'Loan Management', 'Healthcare', 'Education', 'Agriculture',
            'Non Profit', 'Hospitality', 'Utilities'
        ]
        
        for module_name in modules_to_hide:
            if frappe.db.exists("Module Def", module_name):
                try:
                    # Simply set the module as disabled
                    frappe.db.set_value("Module Def", module_name, "disabled", 1)
                    print(f"✅ Hidden module: {module_name}")
                except Exception as e:
                    print(f"⚠️  Could not hide module {module_name}: {str(e)}")
        
        frappe.db.commit()
        print("✅ Module hiding complete!")
        print("📌 Refresh your browser to see the changes")
        
    except Exception as e:
        print(f"❌ Error hiding modules: {e}")
        frappe.log_error(f"Module hiding error: {str(e)}")

def create_rental_workspace():
    """Create a custom Rental Management workspace as the default home"""
    try:
        workspace_name = "Rental Management"
        
        # Delete existing workspace if it exists
        if frappe.db.exists("Workspace", workspace_name):
            frappe.delete_doc("Workspace", workspace_name, force=1)
            print(f"🔄 Deleted existing {workspace_name} workspace")
        
        # Create new workspace
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "name": workspace_name,
            "title": "Rental Management",
            "module": "Rental Management",
            "icon": "retail",
            "indicator_color": "purple",
            "is_standard": 0,
            "public": 1,
            "extends": "",
            "extends_another_page": 0,
            "is_hidden": 0,
            "label": "Rental Management",
        })
        
        # Add shortcuts section
        workspace.append("shortcuts", {
            "type": "DocType",
            "label": "New Item",
            "doc_view": "List",
            "link_to": "Item",
            "color": "Blue"
        })
        
        workspace.append("shortcuts", {
            "type": "DocType",
            "label": "New Customer",
            "doc_view": "List",
            "link_to": "Customer",
            "color": "Green"
        })
        
        workspace.append("shortcuts", {
            "type": "DocType",
            "label": "New Invoice",
            "doc_view": "List",
            "link_to": "Sales Invoice",
            "color": "Orange"
        })
        
        workspace.append("shortcuts", {
            "type": "DocType",
            "label": "Payment Entry",
            "doc_view": "List",
            "link_to": "Payment Entry",
            "color": "Green"
        })
        
        workspace.append("shortcuts", {
            "type": "DocType",
            "label": "Portal Banners",
            "doc_view": "List",
            "link_to": "Portal Banner",
            "color": "Purple"
        })
        
        workspace.append("shortcuts", {
            "type": "Page",
            "label": "Customer Portal",
            "link_to": "/portal",
            "color": "Cyan"
        })
        
        # Add links section - Rental Operations
        workspace.append("links", {
            "label": "Rental Operations",
            "type": "Card Break"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Item",
            "label": "Items",
            "onboard": 1
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Customer",
            "label": "Customers"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Sales Invoice",
            "label": "Sales Invoices"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Rental Cart",
            "label": "Rental Carts"
        })
        
        # Portal Management section
        workspace.append("links", {
            "label": "Portal Management",
            "type": "Card Break"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Portal Banner",
            "label": "Portal Banners"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Item Group",
            "label": "Categories"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "Page",
            "link_to": "/portal",
            "label": "View Customer Portal"
        })
        
        # Accounting section
        workspace.append("links", {
            "label": "Accounting",
            "type": "Card Break"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Payment Entry",
            "label": "Payment Entries"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Journal Entry",
            "label": "Journal Entries"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Third Party Owner",
            "label": "Third Party Owners"
        })
        
        # Reports section
        workspace.append("links", {
            "label": "Reports",
            "type": "Card Break"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "Report",
            "link_to": "Profit and Loss Statement",
            "label": "Profit & Loss"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "Report",
            "link_to": "Balance Sheet",
            "label": "Balance Sheet"
        })
        
        workspace.append("links", {
            "type": "Link",
            "link_type": "Report",
            "link_to": "Stock Ledger",
            "label": "Stock Ledger"
        })
        
        workspace.insert(ignore_permissions=True)
        
        # Set as default workspace for users
        frappe.db.set_value("Workspace Settings", "Workspace Settings", "home_page", workspace_name)
        
        print(f"✅ Created {workspace_name} workspace and set as default home")
        
    except Exception as e:
        print(f"❌ Error creating workspace: {e}")
        frappe.log_error(f"Workspace creation error: {str(e)}")

def setup_rental_roles_and_users():
    """Create Rental Manager role with proper permissions and test user"""
    try:
        print("Setting up Rental Manager role and permissions...")
        
        # Create Rental Manager role if it doesn't exist
        if not frappe.db.exists("Role", "Rental Manager"):
            rental_role = frappe.get_doc({
                "doctype": "Role",
                "role_name": "Rental Manager",
                "desk_access": 1,
            })
            rental_role.insert(ignore_permissions=True)
            print("✅ Created Rental Manager role")
        
        # Create test user
        test_email = "rental.manager@example.com"
        
        if not frappe.db.exists("User", test_email):
            user = frappe.get_doc({
                "doctype": "User",
                "email": test_email,
                "first_name": "Rental",
                "last_name": "Manager",
                "send_welcome_email": 0,
                "enabled": 1,
                "user_type": "System User"
            })
            user.insert(ignore_permissions=True)
            user.new_password = "rental123"
            user.save(ignore_permissions=True)
            print(f"✅ Created test user: {test_email}")
        
        # Add standard roles for full functionality
        user = frappe.get_doc("User", test_email)
        roles_to_add = [
            "Rental Manager",
            "Item Manager",
            "Stock Manager", 
            "Accounts Manager",
            "Sales Manager",
            "Sales User",
            "Stock User",
            "Accounts User"
        ]
        
        for role in roles_to_add:
            if frappe.db.exists("Role", role) and not any(d.role == role for d in user.get("roles", [])):
                user.append("roles", {"role": role})
        
        user.save(ignore_permissions=True)
        frappe.db.commit()
        
        print("\n" + "="*60)
        print("✅ Rental Manager Setup Complete!")
        print("="*60)
        print(f"📧 Email: {test_email}")
        print(f"🔑 Password: rental123")
        print(f"🎯 Roles: " + ", ".join(roles_to_add))
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error setting up roles: {e}")
        frappe.log_error(f"Role setup error: {str(e)}")
