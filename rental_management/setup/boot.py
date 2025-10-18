"""
Boot session configuration for Rental Management
Controls module visibility and desk customizations
"""

import frappe

def boot_session(bootinfo):
    """Called when user logs in - customize boot info"""
    try:
        # Customize modules shown in desk
        customize_modules(bootinfo)
        
        # Add custom branding
        bootinfo["app_name"] = "Blush & Glow Rental"
        bootinfo["app_logo_url"] = "/assets/rental_management/images/blush_glow_logo.png"
        
    except Exception as e:
        frappe.log_error(f"Error in boot_session: {str(e)}", "Rental Management Boot")


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
