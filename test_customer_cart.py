#!/usr/bin/env python3
"""
Test script to verify customer-based cart operations
Run this to test if the database-based cart is working properly
"""

import frappe
from rental_management.api.customer_portal import (
    add_to_customer_cart, 
    get_customer_cart_items, 
    remove_from_customer_cart,
    search_customers,
    create_customer
)

def test_customer_cart():
    """Test customer-based cart operations"""
    print("🧪 Testing Customer-Based Cart Operations")
    print("="*50)
    
    # Test 1: Create a test customer
    print("\n1. Creating test customer...")
    customer_result = create_customer(
        customer_name="Test Customer Cart",
        mobile_number="9999999999",
        email_id="test@cart.com"
    )
    
    if not customer_result.get('success'):
        print(f"❌ Failed to create customer: {customer_result.get('message')}")
        return
        
    customer_id = customer_result['customer_id']
    print(f"✅ Created customer: {customer_id}")
    
    # Test 2: Add item to cart
    print("\n2. Adding item to customer cart...")
    add_result = add_to_customer_cart(
        item_code="DRESS-001-RENTAL",  # Replace with actual item code
        customer_id=customer_id,
        rental_start_date="2025-09-20",
        rental_end_date="2025-09-22",
        function_date="2025-09-21"
    )
    
    if add_result.get('success'):
        print(f"✅ Added item to cart. Cart count: {add_result.get('cart_count')}")
    else:
        print(f"❌ Failed to add item: {add_result.get('message')}")
        return
    
    # Test 3: Get cart items
    print("\n3. Retrieving customer cart items...")
    cart_result = get_customer_cart_items(customer_id)
    
    if cart_result.get('items'):
        print(f"✅ Found {len(cart_result['items'])} items in cart")
        print(f"   Total: ₹{cart_result.get('total', 0)}")
        for item in cart_result['items']:
            print(f"   - {item['item_name']} (₹{item['total_amount']})")
    else:
        print("❌ No items found in cart")
        return
    
    # Test 4: Remove item from cart
    print("\n4. Removing item from cart...")
    cart_item_id = cart_result['items'][0]['cart_item_id']
    remove_result = remove_from_customer_cart(cart_item_id, customer_id)
    
    if remove_result.get('success'):
        print(f"✅ Removed item from cart. New cart count: {remove_result.get('cart_count')}")
    else:
        print(f"❌ Failed to remove item: {remove_result.get('message')}")
    
    # Test 5: Verify empty cart
    print("\n5. Verifying cart is empty...")
    final_cart = get_customer_cart_items(customer_id)
    
    if len(final_cart.get('items', [])) == 0:
        print("✅ Cart is empty as expected")
    else:
        print(f"❌ Cart still has {len(final_cart['items'])} items")
    
    print("\n" + "="*50)
    print("🎉 Test completed!")

def test_session_vs_customer_cart():
    """Compare session-based vs customer-based cart"""
    print("\n🔄 Testing Session vs Customer Cart Isolation")
    print("="*50)
    
    # This would require actual session context to test properly
    print("ℹ️  Session vs customer cart isolation should be tested in browser")
    print("   - Session cart: Uses frappe.session['cart_items']")
    print("   - Customer cart: Uses Rental Cart doctype in database")
    print("   - Both should work independently")

if __name__ == "__main__":
    # Initialize Frappe
    try:
        frappe.init()
        frappe.connect()
        
        test_customer_cart()
        test_session_vs_customer_cart()
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    finally:
        frappe.destroy()
