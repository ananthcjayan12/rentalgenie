"""
Boot session configuration for Rental Management
Module hiding is handled at Module Def level via install.py
"""

import frappe

def boot_session(bootinfo):
    """
    Add rental management specific bootinfo
    Module visibility is controlled by Module Def.disabled field
    """
    # Module hiding is handled at database level in install.py
    # via frappe.db.set_value("Module Def", module_name, "disabled", 1)
    pass
