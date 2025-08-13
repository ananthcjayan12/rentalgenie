"""
Cleanup Test Data - Rental Management System
Remove test data created during integration testing
"""

import frappe

def cleanup_test_items():
    """Remove test items created during integration testing"""
    test_patterns = [
        "TEST-%",
        "VALIDATE-%", 
        "BOOKING-TEST-%",
        "%-RENTAL"  # Service items
    ]
    
    removed_items = []
    
    for pattern in test_patterns:
        items = frappe.db.get_list("Item", 
                                 filters={"item_code": ["like", pattern]}, 
                                 pluck="name")
        
        for item in items:
            try:
                frappe.delete_doc("Item", item, force=True)
                removed_items.append(item)
            except Exception as e:
                print(f"Could not delete item {item}: {e}")
    
    return removed_items

def cleanup_test_customers():
    """Remove test customers created during testing"""
    test_patterns = [
        "%Test%Customer%",
        "%Validation%",
        "%Booking%Test%"
    ]
    
    removed_customers = []
    
    for pattern in test_patterns:
        customers = frappe.db.get_list("Customer", 
                                     filters={"customer_name": ["like", pattern]}, 
                                     pluck="name")
        
        for customer in customers:
            try:
                frappe.delete_doc("Customer", customer, force=True)
                removed_customers.append(customer)
            except Exception as e:
                print(f"Could not delete customer {customer}: {e}")
    
    return removed_customers

def cleanup_test_bookings():
    """Remove test bookings/sales invoices created during testing"""
    # Find bookings with test customers or test items
    test_invoices = []
    
    # Get invoices that are rental bookings
    invoices = frappe.db.get_list("Sales Invoice",
                                filters={"is_rental_booking": 1},
                                fields=["name", "customer"])
    
    for invoice in invoices:
        # Check if customer name contains test patterns
        if any(pattern in invoice.customer for pattern in ["Test", "Validation", "Booking"]):
            test_invoices.append(invoice.name)
    
    removed_invoices = []
    
    for invoice in test_invoices:
        try:
            # Cancel if submitted
            doc = frappe.get_doc("Sales Invoice", invoice)
            if doc.docstatus == 1:
                doc.cancel()
            
            frappe.delete_doc("Sales Invoice", invoice, force=True)
            removed_invoices.append(invoice)
        except Exception as e:
            print(f"Could not delete invoice {invoice}: {e}")
    
    return removed_invoices

def cleanup_test_journal_entries():
    """Remove journal entries created for test bookings"""
    test_entries = frappe.db.get_list("Journal Entry",
                                    filters={"user_remark": ["like", "%Caution deposit%test%"]},
                                    pluck="name")
    
    removed_entries = []
    
    for entry in test_entries:
        try:
            doc = frappe.get_doc("Journal Entry", entry)
            if doc.docstatus == 1:
                doc.cancel()
            
            frappe.delete_doc("Journal Entry", entry, force=True)
            removed_entries.append(entry)
        except Exception as e:
            print(f"Could not delete journal entry {entry}: {e}")
    
    return removed_entries

def run_cleanup():
    """Run complete test data cleanup"""
    print("🧹 Starting test data cleanup...")
    print("=" * 50)
    
    # Track all removals
    total_removed = 0
    
    # Cleanup in order (invoices first to avoid foreign key issues)
    print("Cleaning up test bookings...")
    removed_invoices = cleanup_test_bookings()
    if removed_invoices:
        print(f"✅ Removed {len(removed_invoices)} test invoices")
        total_removed += len(removed_invoices)
    
    print("Cleaning up test journal entries...")
    removed_entries = cleanup_test_journal_entries()
    if removed_entries:
        print(f"✅ Removed {len(removed_entries)} test journal entries")
        total_removed += len(removed_entries)
    
    print("Cleaning up test customers...")
    removed_customers = cleanup_test_customers()
    if removed_customers:
        print(f"✅ Removed {len(removed_customers)} test customers")
        total_removed += len(removed_customers)
    
    print("Cleaning up test items...")
    removed_items = cleanup_test_items()
    if removed_items:
        print(f"✅ Removed {len(removed_items)} test items")
        total_removed += len(removed_items)
    
    # Commit all deletions
    frappe.db.commit()
    
    print("=" * 50)
    print(f"🎉 Cleanup completed! Removed {total_removed} test records.")
    
    if total_removed == 0:
        print("ℹ️ No test data found to cleanup.")
    
    return total_removed

def cleanup_specific_pattern(doctype, pattern):
    """Cleanup documents matching a specific pattern"""
    if doctype not in ["Item", "Customer", "Sales Invoice", "Journal Entry"]:
        print(f"❌ Unsupported doctype: {doctype}")
        return 0
    
    docs = frappe.db.get_list(doctype,
                            filters={"name": ["like", pattern]},
                            pluck="name")
    
    removed = 0
    for doc in docs:
        try:
            frappe.delete_doc(doctype, doc, force=True)
            removed += 1
        except Exception as e:
            print(f"Could not delete {doctype} {doc}: {e}")
    
    frappe.db.commit()
    return removed

if __name__ == "__main__":
    frappe.init()
    frappe.connect()
    
    run_cleanup()
