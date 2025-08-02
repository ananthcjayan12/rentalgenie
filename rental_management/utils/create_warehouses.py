"""
Manual Warehouse Creation Script for Rental Management

This script can be run from the ERPNext console to manually create rental warehouses
if they weren't created during app installation.

Usage:
1. Go to ERPNext Console: bench --site your-site.localhost console
2. Run: exec(open('apps/rental_management/rental_management/utils/create_warehouses.py').read())
"""

import frappe

def create_rental_warehouses_manual():
    """Manually create rental warehouses"""
    try:
        print("🏭 Starting manual warehouse creation...")
        
        # Get all active companies
        companies = frappe.get_all("Company", filters={"disabled": 0}, fields=["name"])
        
        if not companies:
            print("❌ No active companies found!")
            return
        
        warehouses = [
            {"warehouse_name": "Rental Store"},
            {"warehouse_name": "Rental Display"},
            {"warehouse_name": "Rental Maintenance"}
        ]
        
        created_count = 0
        
        for company_doc in companies:
            company = company_doc.name
            print(f"\n📦 Processing company: {company}")
            
            for wh in warehouses:
                warehouse_name = wh['warehouse_name']
                full_warehouse_name = f"{warehouse_name} - {company}"
                
                if frappe.db.exists("Warehouse", full_warehouse_name):
                    print(f"⚠️  Warehouse already exists: {full_warehouse_name}")
                    continue
                
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
                    created_count += 1
                    
                except Exception as e:
                    print(f"❌ Error creating warehouse {full_warehouse_name}: {str(e)}")
        
        print(f"\n🎉 Warehouse creation completed! Created {created_count} warehouses.")
        
        # List all rental warehouses
        print("\n📋 All rental warehouses:")
        rental_warehouses = frappe.get_all("Warehouse", 
                                         filters=[["warehouse_name", "like", "%Rental%"]], 
                                         fields=["name", "company", "warehouse_type"])
        
        for wh in rental_warehouses:
            print(f"   📦 {wh.name} ({wh.warehouse_type})")
        
    except Exception as e:
        print(f"❌ Error in manual warehouse creation: {str(e)}")
        frappe.log_error(f"Manual warehouse creation error: {str(e)}")

if __name__ == "__main__":
    create_rental_warehouses_manual()
