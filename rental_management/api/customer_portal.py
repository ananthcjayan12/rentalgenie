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

@frappe.whitelist(allow_guest=True)
def get_cart_items():
    """Get session-based cart items for shopkeeper portal"""
    try:
        # Get cart items from session instead of user-based cart
        cart_items = frappe.session.get('cart_items', [])
        
        if not cart_items:
            return {'items': [], 'total': 0}
            
        processed_items = []
        total_amount = 0
        
        for item in cart_items:
            try:
                item_details = frappe.get_doc("Item", item['item_code'])
                rental_days = (getdate(item['rental_end_date']) - getdate(item['rental_start_date'])).days + 1
                line_total = item_details.rental_rate_per_day * rental_days
                
                processed_items.append({
                    'cart_item_id': item.get('cart_item_id', item['item_code']),  # Use for removal
                    'item_code': item['item_code'],
                    'item_name': item_details.item_name,
                    'item_image': item_details.image,
                    'rental_rate': item_details.rental_rate_per_day,
                    'rental_start_date': item['rental_start_date'],
                    'rental_end_date': item['rental_end_date'],
                    'rental_days': rental_days,
                    'total_amount': line_total,
                    'function_date': item.get('function_date')
                })
                
                total_amount += line_total
                
            except Exception as e:
                # Skip invalid items
                frappe.log_error(f"Error processing cart item {item.get('item_code')}: {str(e)}")
                continue
        
        return {
            'items': processed_items,
            'total': total_amount
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting cart items: {str(e)}")
        return {'items': [], 'total': 0}

@frappe.whitelist(allow_guest=True)
def add_to_cart(item_code, rental_start_date, rental_end_date, function_date=None):
    """Add item to session-based cart for shopkeeper portal"""
    try:
        # Check item availability
        availability = check_item_availability(item_code, rental_start_date, rental_end_date)
        if not availability['is_available']:
            return {'success': False, 'message': availability['message']}
            
        # Get current cart from session
        cart_items = frappe.session.get('cart_items', [])
        
        # Generate unique cart item ID
        import uuid
        cart_item_id = str(uuid.uuid4())
        
        # Add item to session cart
        cart_items.append({
            'cart_item_id': cart_item_id,
            'item_code': item_code,
            'rental_start_date': rental_start_date,
            'rental_end_date': rental_end_date,
            'function_date': function_date,
            'added_at': frappe.utils.now()
        })
        
        # Save to session
        frappe.session['cart_items'] = cart_items
        
        return {
            'success': True,
            'message': 'Item added to cart successfully',
            'cart_item_id': cart_item_id,
            'cart_count': len(cart_items)
        }
        
    except Exception as e:
        frappe.log_error(f"Error adding to cart: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist(allow_guest=True)
def remove_from_cart(cart_item_id):
    """Remove item from session-based cart"""
    try:
        # Get current cart from session
        cart_items = frappe.session.get('cart_items', [])
        
        # Find and remove the item
        cart_items = [item for item in cart_items if item.get('cart_item_id') != cart_item_id]
        
        # Save updated cart to session
        frappe.session['cart_items'] = cart_items
        
        return {
            'success': True,
            'message': 'Item removed from cart successfully',
            'cart_count': len(cart_items)
        }
        
    except Exception as e:
        frappe.log_error(f"Error removing from cart: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist(allow_guest=True)
def create_booking_from_cart(customer_info, address_type, new_address=None, special_instructions=""):
    """Create booking/sales invoice from session cart items"""
    try:
        # Get cart items from session
        cart_items = frappe.session.get('cart_items', [])
        
        if not cart_items:
            return {'success': False, 'message': 'Cart is empty'}
            
        # Get or create customer
        customer_id = customer_info.get('customer_id')
        if customer_id:
            # Use existing customer
            customer_doc = frappe.get_doc("Customer", customer_id)
        else:
            # Create new customer
            customer_doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_info.get('name'),
                "mobile_no": customer_info.get('mobile'),
                "email_id": customer_info.get('email', ''),
                "customer_group": "Individual",
                "territory": "All Territories"
            })
            customer_doc.insert(ignore_permissions=True)
            customer_id = customer_doc.name
        
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
                    "link_name": customer_id
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
            "customer": customer_id,
            "customer_name": customer_doc.customer_name,
            "customer_address": address_name,
            "is_rental_booking": 1,
            "booking_status": "Confirmed",
            "remarks": special_instructions,
            "due_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),
            "items": []
        })
        
        # Add items from session cart
        total_amount = 0
        for cart_item in cart_items:
            item_details = frappe.get_doc("Item", cart_item['item_code'])
            rental_days = (frappe.utils.getdate(cart_item['rental_end_date']) - 
                          frappe.utils.getdate(cart_item['rental_start_date'])).days + 1
            line_total = item_details.rental_rate_per_day * rental_days
            
            sales_invoice.append("items", {
                "item_code": cart_item['item_code'],
                "item_name": item_details.item_name,
                "description": item_details.description,
                "qty": 1,
                "rate": line_total,
                "amount": line_total,
                "rental_start_date": cart_item['rental_start_date'],
                "rental_end_date": cart_item['rental_end_date'],
                "function_date": cart_item.get('function_date')
            })
            total_amount += line_total
        
        # Save and submit the sales invoice
        sales_invoice.insert(ignore_permissions=True)
        sales_invoice.submit()
        
        # Clear the session cart
        frappe.session['cart_items'] = []
        
        # Log the booking creation
        frappe.log_error(f"Booking created successfully: {sales_invoice.name} for customer {customer_id}")
        
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

# Customer Management APIs for Shopkeeper Interface

@frappe.whitelist()
def search_customers(query=""):
    """Search customers by name, mobile, or email"""
    try:
        if not query:
            return []
            
        query = f"%{query}%"
        
        customers = frappe.db.sql("""
            SELECT 
                name, customer_name, mobile_no, email_id, customer_group,
                creation, modified,
                (SELECT COUNT(*) FROM `tabSales Invoice` 
                 WHERE customer = c.name AND is_rental_booking = 1 AND docstatus = 1) as booking_count,
                (SELECT MAX(posting_date) FROM `tabSales Invoice` 
                 WHERE customer = c.name AND is_rental_booking = 1 AND docstatus = 1) as last_booking_date
            FROM `tabCustomer` c
            WHERE (customer_name LIKE %s 
                   OR mobile_no LIKE %s 
                   OR email_id LIKE %s
                   OR name LIKE %s)
            AND disabled = 0
            ORDER BY modified DESC
            LIMIT 20
        """, (query, query, query, query), as_dict=True)
        
        return customers
        
    except Exception as e:
        frappe.log_error(f"Error searching customers: {str(e)}")
        return []

@frappe.whitelist()
def create_customer(customer_name, mobile_no, email_id="", address_line1="", city="", state="", pincode=""):
    """Create a new customer"""
    try:
        # Validate required fields
        if not customer_name or not mobile_no:
            return {'success': False, 'message': 'Customer name and mobile number are required'}
        
        # Check if customer with same mobile already exists
        existing = frappe.db.get_value("Customer", {"mobile_no": mobile_no}, "name")
        if existing:
            return {'success': False, 'message': 'Customer with this mobile number already exists'}
        
        # Create customer
        customer_doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name.strip(),
            "mobile_no": mobile_no.strip(),
            "email_id": email_id.strip() if email_id else "",
            "customer_group": "Individual",
            "territory": "All Territories"
        })
        
        customer_doc.insert(ignore_permissions=True)
        
        # Create address if provided
        if address_line1:
            address_doc = frappe.get_doc({
                "doctype": "Address",
                "address_title": customer_name,
                "address_line1": address_line1.strip(),
                "city": city.strip() if city else "",
                "state": state.strip() if state else "",
                "pincode": pincode.strip() if pincode else "",
                "country": "India",
                "address_type": "Billing",
                "is_primary_address": 1,
                "links": [{
                    "link_doctype": "Customer",
                    "link_name": customer_doc.name
                }]
            })
            address_doc.insert(ignore_permissions=True)
            
            # Update customer with primary address
            customer_doc.customer_primary_address = address_doc.name
            customer_doc.save(ignore_permissions=True)
        
        return {
            'success': True, 
            'message': 'Customer created successfully',
            'customer': {
                'name': customer_doc.name,
                'customer_name': customer_doc.customer_name,
                'mobile_no': customer_doc.mobile_no,
                'email_id': customer_doc.email_id
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating customer: {str(e)}")
        return {'success': False, 'message': f'Error creating customer: {str(e)}'}

@frappe.whitelist()
def get_customer_details(customer_id):
    """Get detailed customer information"""
    try:
        customer = frappe.get_doc("Customer", customer_id)
        
        # Get customer's addresses
        addresses = frappe.get_all("Address", 
            filters={"link_name": customer_id, "link_doctype": "Customer"},
            fields=["name", "address_title", "address_line1", "address_line2", 
                   "city", "state", "pincode", "country", "address_type", "is_primary_address"])
        
        # Get booking statistics
        booking_stats = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_bookings,
                SUM(total) as total_spent,
                COUNT(CASE WHEN booking_status IN ('Confirmed', 'Delivered') THEN 1 END) as active_bookings,
                COUNT(CASE WHEN booking_status = 'Completed' THEN 1 END) as completed_bookings,
                MAX(posting_date) as last_booking_date
            FROM `tabSales Invoice`
            WHERE customer = %s 
            AND is_rental_booking = 1
            AND docstatus = 1
        """, (customer_id,), as_dict=True)
        
        stats = booking_stats[0] if booking_stats else {
            'total_bookings': 0, 'total_spent': 0, 'active_bookings': 0, 
            'completed_bookings': 0, 'last_booking_date': None
        }
        
        # Get recent bookings
        recent_bookings = frappe.db.sql("""
            SELECT 
                si.name, si.posting_date, si.total, si.booking_status,
                si.customer_name, si.due_date,
                COUNT(sii.name) as item_count,
                MIN(sii.rental_start_date) as earliest_rental_date,
                MAX(sii.rental_end_date) as latest_rental_date
            FROM `tabSales Invoice` si
            LEFT JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
            WHERE si.customer = %s 
            AND si.is_rental_booking = 1
            AND si.docstatus = 1
            GROUP BY si.name
            ORDER BY si.posting_date DESC
            LIMIT 10
        """, (customer_id,), as_dict=True)
        
        return {
            'success': True,
            'customer': customer.as_dict(),
            'addresses': addresses,
            'stats': stats,
            'recent_bookings': recent_bookings
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting customer details: {str(e)}")
        return {'success': False, 'message': f'Error loading customer details: {str(e)}'}

@frappe.whitelist()
def update_customer(customer_id, customer_name, mobile_no, email_id=""):
    """Update customer information"""
    try:
        customer = frappe.get_doc("Customer", customer_id)
        
        # Update fields
        customer.customer_name = customer_name.strip()
        customer.mobile_no = mobile_no.strip()
        customer.email_id = email_id.strip() if email_id else ""
        
        customer.save(ignore_permissions=True)
        
        return {
            'success': True,
            'message': 'Customer updated successfully',
            'customer': {
                'name': customer.name,
                'customer_name': customer.customer_name,
                'mobile_no': customer.mobile_no,
                'email_id': customer.email_id
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error updating customer: {str(e)}")
        return {'success': False, 'message': f'Error updating customer: {str(e)}'}
