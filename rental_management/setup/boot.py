"""
Boot session configuration for Rental Management
Controls module visibility and desk customizations
"""

import frappe

def boot_session(bootinfo):
    """Called when user logs in - customize what modules are shown"""
    import frappe
    
    try:
        # Define modules to show for Rental Management
        rental_modules = {
            'Stock',           # For managing rental items
            'Accounting',      # For invoicing and payments  
            'Accounts',        # Financial accounting
            'Home',           # Dashboard
            'Setup',          # Configuration
            'Website',        # Portal management
            'Rental Management'  # Our custom module
        }
        
        # Get the user's role to determine access
        user_roles = frappe.get_roles()
        
        # System Manager sees everything, others see only rental modules
        if "System Manager" not in user_roles:
            # Filter modules in bootinfo
            if 'modules' in bootinfo:
                original_count = len(bootinfo['modules'])
                bootinfo['modules'] = [
                    m for m in bootinfo['modules'] 
                    if m.get('module_name') in rental_modules or m.get('name') in rental_modules
                ]
                filtered_count = len(bootinfo['modules'])
                print(f"✅ Filtered modules: {original_count} → {filtered_count}")
            
            # Filter desktop items
            if 'desktop_items' in bootinfo:
                bootinfo['desktop_items'] = [
                    item for item in bootinfo['desktop_items']
                    if item.get('module_name') in rental_modules
                ]
        else:
            print("ℹ️ System Manager - showing all modules")
        
    except Exception as e:
        frappe.log_error(f"Error in boot_session: {str(e)}", "Rental Boot Error")
        print(f"❌ Error in boot_session: {e}")


def extend_bootinfo(bootinfo):
    """Extend bootinfo with custom configurations"""
    try:
        # Define modules to show/hide
        allowed_modules = [
            "Home",
            "Stock",
            "Accounts",
            "Accounting",
            "Rental Management",
            "Setup",
            "Website",
            "Tools",
            "Build"
        ]
        
        # Filter modules
        if "modules" in bootinfo:
            bootinfo["modules"] = [
                m for m in bootinfo["modules"] 
                if m.get("module_name") in allowed_modules
            ]
        
        # Hide unwanted modules
        hidden_modules = [
            "CRM", "Projects", "Support", "Quality", "Manufacturing",
            "Buying", "Selling", "HR", "Payroll", "Assets",
            "Loan Management", "Healthcare", "Education", "Agriculture",
            "Non Profit", "Hospitality", "Utilities"
        ]
        
        bootinfo["hidden_modules"] = hidden_modules
        
    except Exception as e:
        frappe.log_error(f"Error extending bootinfo: {str(e)}", "Rental Management Boot")


def customize_modules(bootinfo):
    """Customize which modules are visible in the desk"""
    try:
        # Get all modules
        all_modules = bootinfo.get("modules", [])
        
        # Modules we want to keep visible
        visible_modules = {
            "Home", "Stock", "Accounts", "Accounting", 
            "Rental Management", "Setup", "Website", "Tools", "Build"
        }
        
        # Filter to only show our modules
        filtered_modules = []
        for module in all_modules:
            module_name = module.get("module_name")
            if module_name in visible_modules:
                filtered_modules.append(module)
        
        bootinfo["modules"] = filtered_modules
        
        print(f"✅ Showing {len(filtered_modules)} modules: {', '.join(visible_modules)}")
        
    except Exception as e:
        frappe.log_error(f"Error customizing modules: {str(e)}", "Rental Management Boot")
        print(f"❌ Error customizing modules: {e}")
