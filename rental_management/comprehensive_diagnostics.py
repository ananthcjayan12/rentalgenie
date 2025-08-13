"""
Comprehensive Diagnostic Script for Rental Management System
This script will check all aspects of the system and provide detailed information
"""

import frappe
from frappe.utils import getdate, add_days, today, flt

def check_app_installation():
    """Check if rental_management app is properly installed"""
    print("🔍 CHECKING APP INSTALLATION")
    print("-" * 50)
    
    try:
        installed_apps = frappe.get_installed_apps()
        print(f"✅ Installed apps: {installed_apps}")
        
        if 'rental_management' in installed_apps:
            print("✅ rental_management app is installed")
            
            # Check app hooks
            hooks = frappe.get_hooks()
            rental_hooks = {k: v for k, v in hooks.items() if 'rental_management' in str(v)}
            print(f"✅ Rental management hooks: {rental_hooks}")
            
            return True
        else:
            print("❌ rental_management app is NOT installed")
            return False
            
    except Exception as e:
        print(f"❌ Error checking app installation: {e}")
        return False

def check_custom_fields():
    """Check all custom fields for Item, Customer, and Sales Invoice"""
    print("\n🔍 CHECKING CUSTOM FIELDS")
    print("-" * 50)
    
    # Define expected fields
    expected_fields = {
        'Item': [
            'is_rental_item',
            'rental_rate_per_day', 
            'item_category',
            'current_rental_status',
            'is_third_party_item',
            'owner_commission_percent',
            'owner_commission_percentage',  # Check both variations
            'approval_status',
            'supplier_for_third_party'
        ],
        'Customer': [
            'customer_unique_id',
            'mobile_number',
            'total_bookings', 
            'last_booking_date',
            'total_rental_amount',
            'customer_preferences',
            'special_instructions'
        ],
        'Sales Invoice': [
            'is_rental_booking',
            'function_date',
            'rental_duration_days',
            'rental_start_date',
            'rental_end_date',
            'booking_status',
            'caution_deposit_amount',
            'caution_deposit_refunded',
            'total_owner_commission',
            'commission_paid_to_owners',
            'exchange_booking',
            'original_booking_reference',
            'exchange_amount_adjustment',
            'exchange_notes',
            'actual_delivery_time',
            'actual_return_time',
            'delivery_notes',
            'return_notes'
        ]
    }
    
    results = {}
    
    for doctype, fields in expected_fields.items():
        print(f"\n📋 Checking {doctype} fields:")
        results[doctype] = {'existing': [], 'missing': []}
        
        # Get all existing custom fields for this doctype
        existing_fields = frappe.db.get_list("Custom Field", 
                                           filters={"dt": doctype}, 
                                           fields=["fieldname", "label", "fieldtype"])
        
        existing_fieldnames = [f['fieldname'] for f in existing_fields]
        
        print(f"   Existing custom fields ({len(existing_fields)}): {existing_fieldnames}")
        
        # Check each expected field
        for field in fields:
            if field in existing_fieldnames:
                print(f"   ✅ {field}")
                results[doctype]['existing'].append(field)
            else:
                print(f"   ❌ {field} - MISSING")
                results[doctype]['missing'].append(field)
    
    return results

def check_item_groups():
    """Check if rental item groups exist"""
    print("\n🔍 CHECKING ITEM GROUPS")
    print("-" * 50)
    
    expected_groups = [
        "Women's Wear",
        "Men's Wear", 
        "Accessories",
        "Jewelry",
        "Footwear"
    ]
    
    results = {'existing': [], 'missing': []}
    
    for group in expected_groups:
        if frappe.db.exists("Item Group", group):
            print(f"✅ {group}")
            results['existing'].append(group)
        else:
            print(f"❌ {group} - MISSING")
            results['missing'].append(group)
    
    # Show all item groups
    all_groups = frappe.db.get_list("Item Group", pluck="name")
    print(f"\n📋 All Item Groups ({len(all_groups)}): {all_groups}")
    
    return results

def check_warehouses():
    """Check if rental warehouses exist"""
    print("\n🔍 CHECKING WAREHOUSES")
    print("-" * 50)
    
    # Get company info
    companies = frappe.db.get_list("Company", fields=["name", "abbr"])
    print(f"📋 Companies: {companies}")
    
    expected_warehouse_types = ["Rental Store", "Rental Display", "Rental Maintenance"]
    results = {}
    
    for company in companies:
        company_name = company['name']
        company_abbr = company['abbr']
        print(f"\n🏢 Checking warehouses for {company_name} ({company_abbr}):")
        
        results[company_name] = {'existing': [], 'missing': []}
        
        for warehouse_type in expected_warehouse_types:
            warehouse_name = f"{warehouse_type} - {company_abbr}"
            
            if frappe.db.exists("Warehouse", warehouse_name):
                print(f"   ✅ {warehouse_name}")
                results[company_name]['existing'].append(warehouse_name)
            else:
                print(f"   ❌ {warehouse_name} - MISSING")
                results[company_name]['missing'].append(warehouse_name)
    
    # Show all rental warehouses
    rental_warehouses = frappe.db.sql("""
        SELECT name, company FROM tabWarehouse 
        WHERE name LIKE '%Rental%'
    """, as_dict=True)
    print(f"\n📋 All Rental Warehouses ({len(rental_warehouses)}): {[w['name'] for w in rental_warehouses]}")
    
    return results

def check_accounts():
    """Check if rental-related accounts exist"""
    print("\n🔍 CHECKING ACCOUNTS")
    print("-" * 50)
    
    companies = frappe.db.get_list("Company", fields=["name", "abbr"])
    results = {}
    
    for company in companies:
        company_name = company['name']
        company_abbr = company['abbr']
        print(f"\n🏢 Checking accounts for {company_name} ({company_abbr}):")
        
        results[company_name] = {'existing': [], 'missing': []}
        
        # Check for caution deposit account
        caution_account_name = f"Caution Deposits Received - {company_abbr}"
        if frappe.db.exists("Account", caution_account_name):
            print(f"   ✅ {caution_account_name}")
            results[company_name]['existing'].append(caution_account_name)
        else:
            print(f"   ❌ {caution_account_name} - MISSING")
            results[company_name]['missing'].append(caution_account_name)
    
    return results

def test_item_creation():
    """Test creating a rental item to check automation"""
    print("\n🔍 TESTING ITEM CREATION")
    print("-" * 50)
    
    try:
        item_code = "DIAGNOSTIC-TEST-ITEM-001"
        
        # Clean up if exists
        if frappe.db.exists("Item", item_code):
            frappe.delete_doc("Item", item_code, force=True)
        
        # Create test item
        item_doc = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": "Diagnostic Test Wedding Dress",
            "stock_uom": "Nos",
            "is_rental_item": 1,
            "rental_rate_per_day": 500,
            "item_category": "Women's Wear"
        })
        
        print(f"📝 Creating item with data: {item_doc.as_dict()}")
        item_doc.insert()
        print(f"✅ Item created: {item_code}")
        
        # Check automation results
        item_doc.reload()
        automation_results = {
            'item_group': getattr(item_doc, 'item_group', 'NOT SET'),
            'current_rental_status': getattr(item_doc, 'current_rental_status', 'NOT SET'),
            'approval_status': getattr(item_doc, 'approval_status', 'NOT SET')
        }
        
        print(f"📊 Automation results: {automation_results}")
        
        # Check service item creation
        service_item_code = f"{item_code}-RENTAL"
        service_item_exists = frappe.db.exists("Item", service_item_code)
        print(f"🔧 Service item '{service_item_code}' exists: {service_item_exists}")
        
        # Clean up
        frappe.delete_doc("Item", item_code, force=True)
        if service_item_exists:
            frappe.delete_doc("Item", service_item_code, force=True)
        print("🧹 Test item cleaned up")
        
        return True, automation_results
        
    except Exception as e:
        print(f"❌ Item creation failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error details: {str(e)}")
        return False, {'error': str(e)}

def test_customer_creation():
    """Test creating a customer to check automation"""
    print("\n🔍 TESTING CUSTOMER CREATION")
    print("-" * 50)
    
    try:
        customer_name = "Diagnostic Test Customer"
        
        # Clean up if exists
        if frappe.db.exists("Customer", customer_name):
            frappe.delete_doc("Customer", customer_name, force=True)
        
        # Create test customer
        customer_doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual",
            "customer_group": "Individual",
            "territory": "India",
            "mobile_number": "9876543210"
        })
        
        print(f"📝 Creating customer with data: {customer_doc.as_dict()}")
        customer_doc.insert()
        print(f"✅ Customer created: {customer_name}")
        
        # Check automation results
        customer_doc.reload()
        automation_results = {
            'customer_unique_id': getattr(customer_doc, 'customer_unique_id', 'NOT SET'),
            'mobile_number': getattr(customer_doc, 'mobile_number', 'NOT SET'),
            'total_bookings': getattr(customer_doc, 'total_bookings', 'NOT SET'),
            'total_rental_amount': getattr(customer_doc, 'total_rental_amount', 'NOT SET')
        }
        
        print(f"📊 Automation results: {automation_results}")
        
        # Clean up
        frappe.delete_doc("Customer", customer_name, force=True)
        print("🧹 Test customer cleaned up")
        
        return True, automation_results
        
    except Exception as e:
        print(f"❌ Customer creation failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error details: {str(e)}")
        return False, {'error': str(e)}

def check_hooks_integration():
    """Check if hooks are properly configured"""
    print("\n🔍 CHECKING HOOKS INTEGRATION")
    print("-" * 50)
    
    try:
        # Check doc_events in hooks
        hooks = frappe.get_hooks("doc_events")
        print(f"📋 Doc events hooks: {hooks}")
        
        # Check specific rental management hooks
        rental_doc_events = {}
        for doctype, events in hooks.items():
            if isinstance(events, dict):
                for event, handlers in events.items():
                    if any('rental_management' in str(handler) for handler in handlers):
                        if doctype not in rental_doc_events:
                            rental_doc_events[doctype] = {}
                        rental_doc_events[doctype][event] = handlers
        
        print(f"🎯 Rental management doc events: {rental_doc_events}")
        
        return rental_doc_events
        
    except Exception as e:
        print(f"❌ Error checking hooks: {e}")
        return {}

def generate_summary_report():
    """Generate a comprehensive summary report"""
    print("\n" + "="*70)
    print("COMPREHENSIVE DIAGNOSTIC REPORT")
    print("="*70)
    
    # Run all checks
    app_status = check_app_installation()
    field_results = check_custom_fields()
    group_results = check_item_groups()
    warehouse_results = check_warehouses()
    account_results = check_accounts()
    hooks_results = check_hooks_integration()
    item_test_status, item_test_results = test_item_creation()
    customer_test_status, customer_test_results = test_customer_creation()
    
    # Generate summary
    print("\n" + "="*70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*70)
    
    total_checks = 0
    passed_checks = 0
    
    # App installation
    total_checks += 1
    if app_status:
        passed_checks += 1
        print("✅ App Installation: PASSED")
    else:
        print("❌ App Installation: FAILED")
    
    # Custom fields
    for doctype, results in field_results.items():
        total_checks += 1
        if not results['missing']:
            passed_checks += 1
            print(f"✅ {doctype} Custom Fields: PASSED ({len(results['existing'])} fields)")
        else:
            print(f"❌ {doctype} Custom Fields: FAILED ({len(results['missing'])} missing)")
    
    # Item groups
    total_checks += 1
    if not group_results['missing']:
        passed_checks += 1
        print(f"✅ Item Groups: PASSED ({len(group_results['existing'])} groups)")
    else:
        print(f"❌ Item Groups: FAILED ({len(group_results['missing'])} missing)")
    
    # Warehouses
    total_checks += 1
    warehouse_issues = sum(len(company_data['missing']) for company_data in warehouse_results.values())
    if warehouse_issues == 0:
        passed_checks += 1
        print("✅ Warehouses: PASSED")
    else:
        print(f"❌ Warehouses: FAILED ({warehouse_issues} missing)")
    
    # Item creation test
    total_checks += 1
    if item_test_status:
        passed_checks += 1
        print("✅ Item Creation Test: PASSED")
    else:
        print("❌ Item Creation Test: FAILED")
    
    # Customer creation test
    total_checks += 1
    if customer_test_status:
        passed_checks += 1
        print("✅ Customer Creation Test: PASSED")
    else:
        print("❌ Customer Creation Test: FAILED")
    
    # Overall status
    success_rate = (passed_checks / total_checks) * 100
    print("\n" + "-"*50)
    print(f"📈 OVERALL SYSTEM HEALTH: {success_rate:.1f}%")
    print(f"✅ Passed: {passed_checks}/{total_checks}")
    print(f"❌ Failed: {total_checks - passed_checks}/{total_checks}")
    
    if success_rate >= 90:
        print("🎉 SYSTEM STATUS: EXCELLENT - Ready for production!")
    elif success_rate >= 70:
        print("⚠️  SYSTEM STATUS: GOOD - Minor issues need fixing")
    elif success_rate >= 50:
        print("🔧 SYSTEM STATUS: NEEDS WORK - Several issues to resolve")
    else:
        print("🚨 SYSTEM STATUS: CRITICAL - Major issues need immediate attention")
    
    print("="*70)
    
    # Return detailed results for further analysis
    return {
        'app_status': app_status,
        'field_results': field_results,
        'group_results': group_results,
        'warehouse_results': warehouse_results,
        'account_results': account_results,
        'hooks_results': hooks_results,
        'item_test': {'status': item_test_status, 'results': item_test_results},
        'customer_test': {'status': customer_test_status, 'results': customer_test_results},
        'summary': {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'success_rate': success_rate
        }
    }

def run_comprehensive_diagnostics():
    """Main function to run all diagnostics"""
    print("🔍 STARTING COMPREHENSIVE RENTAL MANAGEMENT DIAGNOSTICS")
    print("⏰ This may take a few minutes...")
    print("\n")
    
    try:
        results = generate_summary_report()
        return results
    except Exception as e:
        print(f"🚨 CRITICAL ERROR during diagnostics: {e}")
        import traceback
        print("📋 Full error traceback:")
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    frappe.init()
    frappe.connect()
    
    results = run_comprehensive_diagnostics()
    
    if results and results['summary']['success_rate'] < 70:
        print("\n🔧 RECOMMENDATIONS:")
        print("1. Run installation script: bench execute rental_management.setup.install.after_install")
        print("2. Check missing custom fields and recreate them")
        print("3. Verify app hooks are properly configured")
        print("4. Check ERPNext logs for any installation errors")
