import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, add_days
import json

@frappe.whitelist(allow_guest=True)
def get_rental_categories():
    """Get rental item categories for portal home page"""
    try:
        categories = frappe.db.sql("""
            SELECT DISTINCT rental_item_type as name, 
                   rental_item_type as label,
                   COUNT(*) as item_count
            FROM `tabItem` 
            WHERE is_rental_item = 1 
            AND approval_status = 'Approved'
            AND rental_item_type IS NOT NULL
            GROUP BY rental_item_type
            ORDER BY item_count DESC
        """, as_dict=True)
        
        # Add default image for categories
        for category in categories:
            category['image'] = f"/assets/rental_management/images/categories/{category['name'].lower()}.jpg"
            
        return categories
    except Exception as e:
        frappe.log_error(f"Error getting rental categories: {str(e)}")
        return []

@frappe.whitelist(allow_guest=True)
def get_rental_items(category=None, search=None, sort_by="name", filters=None, page=1, limit=20):
    """Get rental items for portal listing"""
    try:
        page = cint(page)
        limit = cint(limit)
        start = (page - 1) * limit
        
        conditions = ["is_rental_item = 1", "approval_status = 'Approved'"]
        values = []
        
        if category:
            conditions.append("rental_item_type = %s")
            values.append(category)
            
        if search:
            conditions.append("(item_name LIKE %s OR description LIKE %s)")
            search_term = f"%{search}%"
            values.extend([search_term, search_term])
            
        # Parse filters if provided
        if filters:
            if isinstance(filters, str):
                filters = json.loads(filters)
            
            if filters.get('price_range'):
                min_price, max_price = filters['price_range']
                conditions.append("rental_rate_per_day BETWEEN %s AND %s")
                values.extend([min_price, max_price])
                
        where_clause = " AND ".join(conditions)
        
        # Handle sorting
        order_clause = "total_rental_count DESC, modified DESC"  # default
        if sort_by == "name":
            order_clause = "item_name ASC"
        elif sort_by == "price_low":
            order_clause = "rental_rate_per_day ASC"
        elif sort_by == "price_high":
            order_clause = "rental_rate_per_day DESC"
        elif sort_by == "newest":
            order_clause = "modified DESC"
        
        items = frappe.db.sql(f"""
            SELECT 
                item_code,
                item_name,
                rental_rate_per_day,
                rental_item_type,
                image,
                current_rental_status,
                is_third_party_item,
                description,
                total_rental_count,
                rental_service_item
            FROM `tabItem`
            WHERE {where_clause}
            ORDER BY {order_clause}
            LIMIT %s OFFSET %s
        """, values + [limit, start], as_dict=True)
        
        # Add computed fields
        for item in items:
            item['is_available'] = item['current_rental_status'] == 'Available'
            item['rental_service_code'] = item['rental_service_item']
            # Add discount calculation if needed
            item['discount_percent'] = 0  # Placeholder for future discount logic
            
        # Get total count for pagination
        total_count = frappe.db.sql(f"""
            SELECT COUNT(*) as count
            FROM `tabItem`
            WHERE {where_clause}
        """, values, as_dict=True)[0]['count']
        
        return {
            'items': items,
            'total_count': total_count,
            'page': page,
            'has_more': (start + limit) < total_count
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting rental items: {str(e)}")
        return {'items': [], 'total_count': 0, 'page': 1, 'has_more': False}

@frappe.whitelist(allow_guest=True)
def get_item_details(item_code):
    """Get detailed item information for product page"""
    try:
        item = frappe.get_doc("Item", item_code)
        
        if not item.is_rental_item or item.approval_status != 'Approved':
            frappe.throw(_("Item not available for rental"))
            
        # Get item images (placeholder - extend based on your image storage)
        images = [item.image] if item.image else []
        
        # Get rental service item for booking
        service_item = None
        if item.rental_service_item:
            service_item = frappe.get_doc("Item", item.rental_service_item)
            
        return {
            'item_code': item.item_code,
            'item_name': item.item_name,
            'description': item.description,
            'rental_rate_per_day': item.rental_rate_per_day,
            'rental_item_type': item.rental_item_type,
            'current_rental_status': item.current_rental_status,
            'is_available': item.current_rental_status == 'Available',
            'total_rental_count': item.total_rental_count,
            'condition_rating': item.condition_rating,
            'images': images,
            'service_item_code': item.rental_service_item,
            'is_third_party': item.is_third_party_item,
            'purchase_cost': item.purchase_cost if item.is_third_party_item else None
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting item details for {item_code}: {str(e)}")
        frappe.throw(_("Item not found or not available"))

@frappe.whitelist()
def check_item_availability(item_code, start_date, end_date):
    """Check if item is available for given rental period"""
    try:
        start_date = getdate(start_date)
        end_date = getdate(end_date)
        
        # Check for conflicting bookings
        conflicting_bookings = frappe.db.sql("""
            SELECT si.name, si.customer, si.rental_start_date, si.rental_end_date
            FROM `tabSales Invoice` si
            JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
            WHERE sii.item_code = %s
            AND si.is_rental_booking = 1
            AND si.docstatus = 1
            AND si.booking_status NOT IN ('Cancelled', 'Completed', 'Exchanged')
            AND (
                (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR
                (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR
                (si.rental_start_date >= %s AND si.rental_end_date <= %s)
            )
        """, (item_code, start_date, start_date, end_date, end_date, start_date, end_date))
        
        is_available = len(conflicting_bookings) == 0
        
        return {
            'is_available': is_available,
            'conflicting_bookings': conflicting_bookings,
            'message': 'Available' if is_available else 'Item is already booked for selected dates'
        }
        
    except Exception as e:
        frappe.log_error(f"Error checking availability for {item_code}: {str(e)}")
        return {'is_available': False, 'message': 'Error checking availability'}

@frappe.whitelist()
def add_to_cart(item_code, rental_start_date, rental_end_date, function_date=None):
    """Add item to customer's cart"""
    try:
        if not frappe.session.user or frappe.session.user == 'Guest':
            frappe.throw(_("Please login to add items to cart"))
            
        # Check item availability
        availability = check_item_availability(item_code, rental_start_date, rental_end_date)
        if not availability['is_available']:
            frappe.throw(_(availability['message']))
            
        # Get or create cart
        customer = get_portal_customer(frappe.session.user)
        cart = get_or_create_cart(customer)
        
        # Add item to cart
        cart.add_item(item_code, rental_start_date, rental_end_date, function_date)
        
        return {
            'success': True,
            'message': 'Item added to cart successfully',
            'cart_count': len(cart.items)
        }
        
    except Exception as e:
        frappe.log_error(f"Error adding to cart: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def get_cart_items():
    """Get customer's cart items"""
    try:
        if not frappe.session.user or frappe.session.user == 'Guest':
            return {'items': [], 'total': 0}
            
        customer = get_portal_customer(frappe.session.user)
        cart = get_customer_cart(customer)
        
        if not cart:
            return {'items': [], 'total': 0}
            
        cart_items = []
        total_amount = 0
        
        for item in cart.items:
            item_details = frappe.get_doc("Item", item.item_code)
            rental_days = (getdate(item.rental_end_date) - getdate(item.rental_start_date)).days + 1
            line_total = item_details.rental_rate_per_day * rental_days
            
            cart_items.append({
                'name': item.name,  # Cart item document name for removal
                'item_code': item.item_code,
                'item_name': item_details.item_name,
                'item_image': item_details.image,
                'rental_rate': item_details.rental_rate_per_day,
                'rental_start_date': item.rental_start_date,
                'rental_end_date': item.rental_end_date,
                'rental_days': rental_days,
                'total_amount': line_total,
                'function_date': item.function_date
            })
            total_amount += line_total
            
        return {
            'items': cart_items,
            'total': total_amount,
            'item_count': len(cart_items)
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting cart items: {str(e)}")
        return {'items': [], 'total': 0}

@frappe.whitelist()
def remove_from_cart(cart_item_name):
    """Remove item from customer's cart"""
    try:
        if not frappe.session.user or frappe.session.user == 'Guest':
            frappe.throw(_("Please login to modify cart"))
            
        # Get the cart item
        cart_item = frappe.get_doc("Rental Cart Item", cart_item_name)
        
        # Verify this cart item belongs to current user's cart
        customer = get_portal_customer(frappe.session.user)
        cart = frappe.get_doc("Rental Cart", cart_item.parent)
        
        if cart.customer != customer:
            frappe.throw(_("Unauthorized access"))
            
        # Remove the cart item
        cart_item.delete()
        
        # Get updated cart count
        remaining_items = frappe.db.count("Rental Cart Item", {"parent": cart.name})
        
        return {
            'success': True,
            'message': 'Item removed from cart successfully',
            'cart_count': remaining_items
        }
        
    except Exception as e:
        frappe.log_error(f"Error removing from cart: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def create_booking_from_cart(customer_info, address_type, new_address=None, special_instructions=""):
    """Create booking/sales invoice from cart items"""
    try:
        if not frappe.session.user or frappe.session.user == 'Guest':
            frappe.throw(_("Please login to create booking"))
            
        # Get customer and cart
        customer = get_portal_customer(frappe.session.user)
        cart = get_customer_cart(customer)
        
        if not cart or not cart.items:
            frappe.throw(_("Cart is empty"))
            
        # Update customer information
        customer_doc = frappe.get_doc("Customer", customer)
        customer_doc.customer_name = customer_info.get('name')
        customer_doc.mobile_no = customer_info.get('mobile')
        customer_doc.save(ignore_permissions=True)
        
        # Handle address
        address_name = None
        if address_type == 'new' and new_address:
            # Create new address
            address_doc = frappe.get_doc({
                "doctype": "Address",
                "address_title": customer_info.get('name'),
                "address_line1": new_address.get('address_line1'),
                "address_line2": new_address.get('address_line2'),
                "city": new_address.get('city'),
                "state": new_address.get('state'),
                "pincode": new_address.get('pincode'),
                "country": new_address.get('country', 'India'),
                "address_type": "Billing",
                "links": [{
                    "link_doctype": "Customer",
                    "link_name": customer
                }]
            })
            address_doc.insert(ignore_permissions=True)
            address_name = address_doc.name
            
            # Set as primary address if customer doesn't have one
            if not customer_doc.customer_primary_address:
                customer_doc.customer_primary_address = address_name
                customer_doc.save(ignore_permissions=True)
        else:
            # Use existing address
            address_name = customer_doc.customer_primary_address
        
        # Create Sales Invoice (Booking)
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": customer,
            "customer_name": customer_doc.customer_name,
            "customer_address": address_name,
            "is_rental_booking": 1,
            "booking_status": "Confirmed",
            "remarks": special_instructions,
            "due_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),
            "items": []
        })
        
        # Add items from cart
        total_amount = 0
        for cart_item in cart.items:
            item_details = frappe.get_doc("Item", cart_item.item_code)
            rental_days = (frappe.utils.getdate(cart_item.rental_end_date) - 
                          frappe.utils.getdate(cart_item.rental_start_date)).days + 1
            line_total = item_details.rental_rate_per_day * rental_days
            
            sales_invoice.append("items", {
                "item_code": cart_item.item_code,
                "item_name": item_details.item_name,
                "description": item_details.description,
                "qty": 1,
                "rate": line_total,
                "amount": line_total,
                "rental_start_date": cart_item.rental_start_date,
                "rental_end_date": cart_item.rental_end_date,
                "function_date": cart_item.function_date
            })
            total_amount += line_total
        
        # Save and submit the sales invoice
        sales_invoice.insert(ignore_permissions=True)
        sales_invoice.submit()
        
        # Clear the cart
        cart.status = "Converted"
        cart.save(ignore_permissions=True)
        
        # Log the booking creation
        frappe.log_error(f"Booking created successfully: {sales_invoice.name} for customer {customer}")
        
        return {
            'success': True,
            'message': 'Booking created successfully',
            'booking_id': sales_invoice.name,
            'total_amount': total_amount
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating booking from cart: {str(e)}")
        return {'success': False, 'message': str(e)}

def get_portal_customer(user_email):
    """Get customer linked to portal user"""
    customer = frappe.db.get_value("Customer", {"email_id": user_email}, "name")
    if not customer:
        # Create customer if doesn't exist
        customer_doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": user_email.split('@')[0].title(),
            "email_id": user_email,
            "customer_group": "Individual",
            "territory": "All Territories"
        })
        customer_doc.insert(ignore_permissions=True)
        customer = customer_doc.name
    return customer

def get_or_create_cart(customer):
    """Get existing cart or create new one"""
    cart_name = frappe.db.get_value("Rental Cart", {"customer": customer, "status": "Active"}, "name")
    
    if cart_name:
        return frappe.get_doc("Rental Cart", cart_name)
    else:
        cart = frappe.get_doc({
            "doctype": "Rental Cart",
            "customer": customer,
            "status": "Active"
        })
        cart.insert(ignore_permissions=True)
        return cart

def get_customer_cart(customer):
    """Get customer's active cart"""
    cart_name = frappe.db.get_value("Rental Cart", {"customer": customer, "status": "Active"}, "name")
    return frappe.get_doc("Rental Cart", cart_name) if cart_name else None
