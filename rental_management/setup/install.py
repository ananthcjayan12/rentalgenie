import frappe
from rental_management.custom_fields.item_fields import create_item_custom_fields
from rental_management.custom_fields.customer_fields import create_customer_custom_fields
from rental_management.custom_fields.sales_invoice_fields import create_sales_invoice_custom_fields

def after_install():
    """Setup custom fields and configurations after app installation"""
    print("Setting up Rental Management...")
    
    # Create custom fields
    create_item_custom_fields()
    create_customer_custom_fields()
    create_sales_invoice_custom_fields()
    
    # Create default item groups if they don't exist
    create_rental_item_groups()
    
    # Setup default accounts template
    setup_rental_accounts()
    
    # Create default warehouses for rental items
    create_rental_warehouses()
    
    print("Rental Management setup completed!")

def create_rental_item_groups():
    """Create rental-specific item groups"""
    item_groups = [
        {"item_group_name": "Rental Items", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Dresses", "parent_item_group": "Rental Items"},
        {"item_group_name": "Ornaments", "parent_item_group": "Rental Items"},
        {"item_group_name": "Accessories", "parent_item_group": "Rental Items"}
    ]
    
    for group in item_groups:
        if not frappe.db.exists("Item Group", group["item_group_name"]):
            item_group = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": group["item_group_name"],
                "parent_item_group": group["parent_item_group"],
                "is_group": 1 if group["item_group_name"] == "Rental Items" else 0
            })
            item_group.insert()

def setup_rental_accounts():
    """Setup rental-specific account templates"""
    try:
        companies = frappe.get_all("Company", fields=["name", "abbr"])
        
        if not companies:
            print("No companies found. Skipping account creation.")
            return
        
        for company_doc in companies:
            company = company_doc.name
            abbr = company_doc.abbr
            print(f"Setting up rental accounts for company: {company}")
            
            accounts = [
                {
                    "account_name": "Caution Deposit Payable",
                    "parent_account": f"Current Liabilities - {abbr}",
                    "account_type": "Payable",
                    "account_currency": "INR",
                    "is_group": 0
                },
                {
                    "account_name": "Owner Commission Payable",
                    "parent_account": f"Current Liabilities - {abbr}",
                    "account_type": "Payable", 
                    "account_currency": "INR",
                    "is_group": 0
                },
                {
                    "account_name": "Rental Revenue",
                    "parent_account": f"Direct Income - {abbr}",
                    "account_type": "Income Account",
                    "account_currency": "INR",
                    "is_group": 0
                },
                {
                    "account_name": "Damage Deduction Income",
                    "parent_account": f"Indirect Income - {abbr}",
                    "account_type": "Income Account",
                    "account_currency": "INR", 
                    "is_group": 0
                },
                {
                    "account_name": "Owner Commission Expense",
                    "parent_account": f"Indirect Expenses - {abbr}",
                    "account_type": "Expense Account",
                    "account_currency": "INR",
                    "is_group": 0
                }
            ]
            
            for account_data in accounts:
                account_name_with_company = f"{account_data['account_name']} - {abbr}"
                
                if not frappe.db.exists("Account", account_name_with_company):
                    try:
                        account = frappe.get_doc({
                            "doctype": "Account",
                            "account_name": account_data["account_name"],
                            "parent_account": account_data["parent_account"],
                            "company": company,
                            "account_type": account_data["account_type"],
                            "account_currency": account_data["account_currency"],
                            "is_group": account_data["is_group"]
                        })
                        account.insert()
                        frappe.db.commit()
                        print(f"✅ Created account: {account_name_with_company}")
                    except Exception as e:
                        print(f"❌ Error creating account {account_name_with_company}: {str(e)}")
                else:
                    print(f"⚠️ Account already exists: {account_name_with_company}")
                    
    except Exception as e:
        print(f"❌ Error in account setup process: {str(e)}")
        frappe.log_error(f"Account setup error: {str(e)}")

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

# Utility functions for getting rental accounts
def get_rental_accounts(company=None):
    """Get rental-specific account names for a company"""
    if not company:
        company = frappe.defaults.get_user_default("Company")
    
    if not company:
        company_doc = frappe.get_all("Company", limit=1)
        if company_doc:
            company = company_doc[0].name
        else:
            frappe.throw("No company found")
    
    abbr = frappe.get_cached_value("Company", company, "abbr")
    
    return {
        "cash_account": f"Cash - {abbr}",
        "caution_deposit_payable": f"Caution Deposit Payable - {abbr}",
        "owner_commission_payable": f"Owner Commission Payable - {abbr}",
        "rental_revenue": f"Rental Revenue - {abbr}",
        "damage_deduction_income": f"Damage Deduction Income - {abbr}",
        "owner_commission_expense": f"Owner Commission Expense - {abbr}",
        "accounts_receivable": f"Debtors - {abbr}",
        "company": company,
        "abbr": abbr
    }

def setup_accounts_manually():
    """Manual function to setup accounts - can be called from console"""
    setup_rental_accounts()
