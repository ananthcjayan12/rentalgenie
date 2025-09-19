import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, add_days
import json

@frappe.whitelist(allow_guest=True)
def get_rental_categories():
    """Get rental item categories for portal home page (count only enabled/approved service items)"""
    try:
        categories = frappe.db.sql("""
            SELECT 
                m.rental_item_type AS name,
                m.rental_item_type AS label,
                COUNT(s.item_code) AS item_count
            FROM `tabItem` m
            JOIN `tabItem` s ON s.item_code = CONCAT(m.item_code, '-RENTAL')
            WHERE m.is_rental_item = 1
              AND m.approval_status = 'Approved'
              AND m.disabled = 0
              AND s.is_stock_item = 0
              AND s.disabled = 0
              AND COALESCE(s.approval_status, m.approval_status) = 'Approved'
              AND m.rental_item_type IS NOT NULL
            GROUP BY m.rental_item_type
            ORDER BY item_count DESC
        """, as_dict=True)
        
        # Map icons per category for better visual distinction
        icon_map = {
            'Dress': 'fa-person-dress',
            'Ornament': 'fa-gem',
            'Accessory': 'fa-star',
            'Other': 'fa-tags'
        }
        
        # Add default image and icon for categories
        for category in categories:
            category['image'] = f"/assets/rental_management/images/categories/{(category['name'] or '').lower()}.jpg"
            category['icon'] = icon_map.get(category.get('label'), 'fa-tag')
            
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
        
        # Build conditions for main item (alias m)
        conditions_m = [
            "m.is_rental_item = 1",
            "m.approval_status = 'Approved'",
            "m.disabled = 0"
        ]
        values = []
        
        if category:
            conditions_m.append("m.rental_item_type = %s")
            values.append(category)
            
        if search:
            conditions_m.append("(m.item_name LIKE %s OR m.description LIKE %s)")
            search_term = f"%{search}%"
            values.extend([search_term, search_term])
            
        trending_mode = False
        # Parse filters if provided
        if filters:
            if isinstance(filters, str):
                filters = json.loads(filters)
            
            if filters.get('price_range'):
                min_price, max_price = filters['price_range']
                conditions_m.append("m.rental_rate_per_day BETWEEN %s AND %s")
                values.extend([min_price, max_price])
            
            # Allow a simple trending flag from callers
            if filters.get('is_trending'):
                trending_mode = True
                # Optional: only consider items that have been rented at least once
                conditions_m.append("COALESCE(m.total_rental_count, 0) > 0")
                
        where_clause_m = " AND ".join(conditions_m)
        
        # Handle sorting (qualify with m.)
        if sort_by == "name":
            order_clause = "m.item_name ASC"
        elif sort_by == "price_low":
            order_clause = "m.rental_rate_per_day ASC"
        elif sort_by == "price_high":
            order_clause = "m.rental_rate_per_day DESC"
        elif sort_by == "newest":
            order_clause = "m.modified DESC"
        elif sort_by == "trending" or trending_mode:
            order_clause = "m.total_rental_count DESC, m.modified DESC"
        else:
            order_clause = "m.total_rental_count DESC, m.modified DESC"
        
        # Get service items joined with main items
        items = frappe.db.sql(f"""
            SELECT 
                s.item_code as service_item_code,
                s.item_name as service_item_name,
                s.image as service_image,
                m.item_code as main_item_code,
                m.item_name as main_item_name,
                m.rental_rate_per_day,
                m.rental_item_type,
                m.current_rental_status,
                m.is_third_party_item,
                m.description,
                m.total_rental_count
            FROM `tabItem` s
            JOIN `tabItem` m ON s.item_code = CONCAT(m.item_code, '-RENTAL')
            WHERE {where_clause_m}
            AND s.is_stock_item = 0
            AND s.disabled = 0
            AND COALESCE(s.approval_status, m.approval_status) = 'Approved'
            ORDER BY {order_clause}
            LIMIT %s OFFSET %s
        """, values + [limit, start], as_dict=True)
        
        # Add computed fields and multiple images
        for item in items:
            item['is_available'] = item['current_rental_status'] == 'Available'
            item['item_code'] = item['service_item_code']  # Use service item code everywhere
            item['item_name'] = item['service_item_name']
            item['main_item_code'] = item['main_item_code']  # Keep reference to main item
            
            # Get multiple images for the main item
            item['images'] = get_item_images(item['main_item_code'])
            item['primary_image'] = item['images'][0] if item['images'] else item['service_image']
            # Generic image key for templates (e.g., related items)
            item['image'] = item['primary_image']
            
            # Add discount calculation if needed
            item['discount_percent'] = 0  # Placeholder for future discount logic
            
        # Build where clause for count on main items table (no alias)
        conditions_plain = [
            "is_rental_item = 1",
            "approval_status = 'Approved'",
            "disabled = 0"
        ]
        if category:
            conditions_plain.append("rental_item_type = %s")
        if search:
            conditions_plain.append("(item_name LIKE %s OR description LIKE %s)")
        if filters and isinstance(filters, dict) and filters.get('price_range'):
            conditions_plain.append("rental_rate_per_day BETWEEN %s AND %s")
        if trending_mode:
            conditions_plain.append("COALESCE(total_rental_count, 0) > 0")
        where_clause_plain = " AND ".join(conditions_plain)
        
        # Get total count for pagination (count only mains that have a qualifying service item)
        total_count_row = frappe.db.sql(f"""
            SELECT COUNT(*) as count
            FROM `tabItem` m
            JOIN `tabItem` s ON s.item_code = CONCAT(m.item_code, '-RENTAL')
            WHERE {where_clause_m}
              AND s.is_stock_item = 0
              AND s.disabled = 0
              AND COALESCE(s.approval_status, m.approval_status) = 'Approved'
        """, values, as_dict=True)
        total_count = total_count_row[0]['count'] if total_count_row else 0
        
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
    """Get detailed item information for product page (always return the rental service item where available)"""
    try:
        # Resolve main vs service
        if item_code.endswith('-RENTAL'):
            main_item_code = item_code[:-7]
            main_item = frappe.get_doc("Item", main_item_code)
            service_item = frappe.get_doc("Item", item_code)
        else:
            main_item = frappe.get_doc("Item", item_code)
            service_item = frappe.get_doc("Item", f"{item_code}-RENTAL") if frappe.db.exists("Item", f"{item_code}-RENTAL") else None
        
        if not main_item.is_rental_item or main_item.approval_status != 'Approved':
            frappe.throw(_("Item not available for rental"))
        
        images = get_item_images(main_item.item_code)
        
        # Prefer service item fields for display
        display_code = service_item.item_code if service_item else main_item.item_code
        display_name = service_item.item_name if service_item else main_item.item_name
        display_desc = service_item.description if (service_item and getattr(service_item, 'description', None)) else main_item.description
        
        return {
            'item_code': display_code,
            'main_item_code': main_item.item_code,
            'item_name': display_name,
            'description': display_desc,
            'rental_rate_per_day': main_item.rental_rate_per_day,
            'rental_item_type': main_item.rental_item_type,
            'current_rental_status': main_item.current_rental_status,
            'is_available': main_item.current_rental_status == 'Available',
            'total_rental_count': main_item.total_rental_count or 0,
            'condition_rating': getattr(main_item, 'condition_rating', 0),
            'images': images,
            'service_item_code': service_item.item_code if service_item else None,
            'is_third_party': main_item.is_third_party_item,
            'purchase_cost': main_item.purchase_cost if main_item.is_third_party_item else None
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











# Customer Management APIs for Shopkeeper Interface

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
def update_customer(customer_id, customer_name, mobile_number, email_id=""):
    """Update customer information"""
    try:
        customer = frappe.get_doc("Customer", customer_id)
        
        # Update fields
        customer.customer_name = customer_name.strip()
        customer.mobile_number = mobile_number.strip()  # ERPNext uses mobile_number
        customer.email_id = email_id.strip() if email_id else ""
        
        customer.save(ignore_permissions=True)
        
        return {
            'success': True,
            'message': 'Customer updated successfully',
            'customer': {
                'name': customer.name,
                'customer_name': customer.customer_name,
                'mobile_number': customer.mobile_number,
                'email_id': customer.email_id
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error updating customer: {str(e)}")
        return {'success': False, 'message': f'Error updating customer: {str(e)}'}

def get_item_images(item_code):
    """Get all images for an item"""
    try:
        # Prefer images from Item Image child table via parent link
        images_rows = frappe.get_all(
            "Item Image",
            filters={"parent": item_code, "parenttype": "Item"},
            fields=["image", "image_description", "is_primary"],
            order_by="is_primary desc, display_order, creation"
        )
        
        # Fallback to legacy 'item' link if needed
        if not images_rows:
            images_rows = frappe.get_all(
                "Item Image",
                filters={"item": item_code},
                fields=["image", "image_description", "is_primary"],
                order_by="is_primary desc, display_order, creation"
            )
        
        # If no images in child table, fallback to main image field
        if not images_rows:
            main_image = frappe.db.get_value("Item", item_code, "image")
            if main_image:
                return [main_image]
            return []
        
        # Return list of image URLs
        return [img.image for img in images_rows if img.image]
        
    except Exception as e:
        frappe.log_error(f"Error getting images for item {item_code}: {str(e)}")
        return []

def get_primary_item_image(item_code):
    """Get primary image for an item"""
    try:
        # First try to get primary image from child table
        primary_image = frappe.db.get_value("Item Image",
                                          {"item": item_code, "is_primary": 1},
                                          "image")
        
        if primary_image:
            return primary_image
            
        # Fallback to first image in child table
        first_image = frappe.db.get_value("Item Image",
                                        {"item": item_code},
                                        "image",
                                        order_by="display_order")
        
        if first_image:
            return first_image
            
        # Final fallback to main image field
        return frappe.db.get_value("Item", item_code, "image")
        
    except Exception as e:
        frappe.log_error(f"Error getting primary image for item {item_code}: {str(e)}")
        return None

# Database-based cart management functions

@frappe.whitelist()
def add_to_customer_cart(item_code, customer_id, rental_start_date, rental_end_date, function_date=None, quantity=1):
    """Add item to customer-specific cart using Rental Cart doctype"""
    try:
        # Validate customer exists
        customer = frappe.db.get_value("Customer", customer_id, "name")
        if not customer:
            return {'success': False, 'message': 'Customer not found'}
            
        # Check item availability
        availability = check_item_availability(item_code, rental_start_date, rental_end_date)
        if not availability['is_available']:
            return {'success': False, 'message': availability['message']}
            
        # Get or create active cart for customer
        cart_doc_name = frappe.db.get_value("Rental Cart", {
            "customer": customer_id,
            "status": "Active",
            "docstatus": 0
        })
        
        if cart_doc_name:
            cart_doc = frappe.get_doc("Rental Cart", cart_doc_name)
        else:
            # Create new cart
            cart_doc = frappe.get_doc({
                "doctype": "Rental Cart",
                "customer": customer_id,
                "status": "Active",
                "created_date": frappe.utils.today()
            })
            cart_doc.insert(ignore_permissions=True)
            
        # Check if item already exists in cart for same dates
        existing_item = None
        for item in cart_doc.items:
            if (item.item_code == item_code and 
                str(item.rental_start_date) == str(rental_start_date) and 
                str(item.rental_end_date) == str(rental_end_date)):
                existing_item = item
                break
                
        # Get item details - always get the main item for rental rate
        if item_code.endswith('-RENTAL'):
            # If service item code is passed, get the main item for rate
            main_item_code = item_code[:-7]
            main_item = frappe.get_doc("Item", main_item_code)
            service_item = frappe.get_doc("Item", item_code)
            item_details = service_item  # For name and other details
        else:
            # If main item code is passed, use it directly for rate
            main_item_code = item_code
            main_item = frappe.get_doc("Item", main_item_code)
            item_details = main_item
        
        # Get rental rate from main item only (rental rates are not on service items)
        rental_rate = main_item.rental_rate_per_day or 0
        
        if rental_rate <= 0:
            return {'success': False, 'message': f'Rental rate not configured for item {main_item.item_name}. Please contact administrator.'}
        
        # For function bookings, charge only 1 day regardless of rental period
        if function_date:
            rental_days = 1
        else:
            rental_days = (getdate(rental_end_date) - getdate(rental_start_date)).days + 1
            
        line_total = rental_rate * rental_days
        
        # Debug logging
        print(f"DEBUG Cart: item={item_code}, main_item={main_item_code}, function_date={function_date}, rental_days={rental_days}, rate={rental_rate}, total={line_total}")
        
        if existing_item:
            # Update existing item (if needed, this implementation doesn't support quantity updates)
            return {'success': False, 'message': 'Item already in cart for these dates'}
        else:
            # Add new item to cart
            cart_doc.append("items", {
                "item_code": item_code,
                "item_name": item_details.item_name,
                "service_item_code": getattr(main_item, 'rental_service_item', None),
                "rental_rate_per_day": rental_rate,
                "rental_days": rental_days,
                "line_total": line_total,
                "rental_start_date": rental_start_date,
                "rental_end_date": rental_end_date,
                "function_date": function_date
            })
            cart_doc.save(ignore_permissions=True)
            
        # Get updated cart count
        cart_count = len(cart_doc.items)
        
        return {
            'success': True,
            'message': 'Item added to cart successfully',
            'cart_count': cart_count
        }
        
    except Exception as e:
        frappe.log_error(f"Error adding to customer cart: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def get_customer_cart_items(customer_id):
    """Get customer-specific cart items from database using Rental Cart doctype"""
    try:
        if not customer_id:
            return {'items': [], 'total': 0, 'item_count': 0}
            
        # Validate customer exists
        customer = frappe.db.get_value("Customer", customer_id, "name")
        if not customer:
            return {'items': [], 'total': 0, 'item_count': 0, 'error': 'Customer not found'}
            
        # Get active cart for customer
        cart_doc = frappe.db.get_value("Rental Cart", {
            "customer": customer_id,
            "status": "Active",
            "docstatus": 0
        })
        
        if not cart_doc:
            return {'items': [], 'total': 0, 'item_count': 0}
            
        # Get cart document with items
        cart = frappe.get_doc("Rental Cart", cart_doc)
        
        processed_items = []
        total_amount = 0
        
        for cart_item in cart.items:
            try:
                item_code = cart_item.item_code
                # Resolve service vs main item for images
                main_item_code = item_code[:-7] if item_code.endswith('-RENTAL') else item_code

                item_details = frappe.get_doc("Item", item_code)

                # Normalize dates to date objects for template strftime
                start_date = getdate(cart_item.rental_start_date) if cart_item.rental_start_date else None
                end_date = getdate(cart_item.rental_end_date) if cart_item.rental_end_date else None
                function_date = getdate(cart_item.function_date) if cart_item.function_date else None

                rental_days = cart_item.rental_days or 0
                line_total = cart_item.line_total or 0

                # Prefer primary image from main item (multi-image support), fallback to service item image
                images = get_item_images(main_item_code)
                primary_image = images[0] if images else getattr(item_details, 'image', None)
                
                processed_items.append({
                    'cart_item_id': cart_item.name,  # Use child table row name for removal
                    'item_code': item_code,
                    'item_name': cart_item.item_name,
                    'item_image': primary_image,
                    'rental_rate': cart_item.rental_rate_per_day,
                    'rental_start_date': start_date,
                    'rental_end_date': end_date,
                    'rental_days': rental_days,
                    'total_amount': line_total,
                    'function_date': function_date
                })
                
                total_amount += line_total
                
            except Exception as e:
                # Skip invalid items
                frappe.log_error(f"Error processing cart item {cart_item.item_code}: {str(e)}")
                continue
        
        return {
            'items': processed_items,
            'total': total_amount,
            'item_count': len(processed_items)
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting customer cart items: {str(e)}")
        return {'items': [], 'total': 0, 'item_count': 0, 'error': str(e)}

@frappe.whitelist()
def remove_from_customer_cart(cart_item_id, customer_id):
    """Remove item from customer-specific cart using Rental Cart doctype"""
    try:
        # Find the cart document that contains this item
        cart_docs = frappe.get_all("Rental Cart", {
            "customer": customer_id,
            "status": "Active",
            "docstatus": 0
        })
        
        if not cart_docs:
            return {'success': False, 'message': 'Cart not found'}
            
        cart_doc = frappe.get_doc("Rental Cart", cart_docs[0].name)
        
        # Find and remove the specific cart item
        item_found = False
        for i, item in enumerate(cart_doc.items):
            if item.name == cart_item_id:
                cart_doc.remove(item)
                item_found = True
                break
                
        if not item_found:
            return {'success': False, 'message': 'Cart item not found'}
            
        # Save the updated cart
        cart_doc.save(ignore_permissions=True)
        
        # Get updated cart count
        cart_count = len(cart_doc.items)
        
        return {
            'success': True,
            'message': 'Item removed from cart successfully',
            'cart_count': cart_count
        }
        
    except Exception as e:
        frappe.log_error(f"Error removing from customer cart: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def clear_customer_cart(customer_id):
    """Clear all items from customer's cart using Rental Cart doctype"""
    try:
        # Get active cart for customer
        cart_docs = frappe.get_all("Rental Cart", {
            "customer": customer_id,
            "status": "Active",
            "docstatus": 0
        })
        
        if not cart_docs:
            return {'success': True, 'message': 'Cart already empty'}
            
        cart_doc = frappe.get_doc("Rental Cart", cart_docs[0].name)
        
        # Clear all items
        cart_doc.items = []
        cart_doc.save(ignore_permissions=True)
        
        return {
            'success': True,
            'message': 'Cart cleared successfully'
        }
        
    except Exception as e:
        frappe.log_error(f"Error clearing customer cart: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def create_customer_booking_from_cart(customer_id, advance_amount=0, special_instructions=""):
    """Create booking/sales invoice from customer's cart items with advance payment collection"""
    try:
        # Validate customer exists
        customer = frappe.get_doc("Customer", customer_id)
        if not customer:
            return {'success': False, 'message': 'Customer not found'}
            
        # Get cart items
        cart_result = get_customer_cart_items(customer_id)
        cart_items = cart_result.get('items', [])
        
        if not cart_items:
            return {'success': False, 'message': 'Cart is empty'}
            
        # Validate all items are still available
        for item in cart_items:
            availability = check_item_availability(
                item['item_code'],
                item['rental_start_date'], 
                item['rental_end_date']
            )
            if not availability['is_available']:
                return {
                    'success': False, 
                    'message': f"Item {item['item_name']} is no longer available for the selected dates"
                }
        
        # Create Sales Invoice (Booking) - Draft status initially
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": customer_id,
            "customer_name": customer.customer_name,
            "posting_date": frappe.utils.today(),
            "due_date": frappe.utils.add_days(frappe.utils.today(), 7),
            "is_rental_booking": 1,
            "booking_status": "",  # Start with empty status, will be set to "Confirmed" after advance collection
            "special_instructions": special_instructions,
            "advance_amount": flt(advance_amount),
            "items": []
        })
        
        total_rental_amount = 0
        total_caution_deposit = 0
        
        # Add cart items to invoice
        for cart_item in cart_items:
            rental_days = cart_item['rental_days']
            rate = flt(cart_item['rental_rate'])
            line_total = flt(cart_item['total_amount'])
            
            # Add rental service item
            sales_invoice.append("items", {
                "item_code": cart_item['item_code'],
                "item_name": cart_item['item_name'],
                "description": f"Rental for {rental_days} days",
                "qty": 1,
                "uom": "Nos",
                "rate": line_total,
                "rental_start_date": cart_item['rental_start_date'],
                "rental_end_date": cart_item['rental_end_date'],
                "function_date": cart_item.get('function_date'),
                "rental_days": rental_days
            })
            
            total_rental_amount += line_total
            
            # Get caution deposit from main item
            main_item_code = cart_item['item_code'][:-7] if cart_item['item_code'].endswith('-RENTAL') else cart_item['item_code']
            main_item = frappe.get_doc("Item", main_item_code)
            caution_deposit = flt(main_item.get('caution_deposit', 0))
            total_caution_deposit += caution_deposit
        
        # Set caution deposit amount on the booking
        sales_invoice.caution_deposit_amount = total_caution_deposit
        
        # Calculate pending amount after advance
        pending_amount = total_rental_amount - flt(advance_amount)
        sales_invoice.pending_payment_amount = pending_amount
        
        # Insert the sales invoice (don't submit yet - keep as draft for advance collection)
        sales_invoice.insert()
        
        # Clear customer's cart after successful booking creation
        clear_customer_cart(customer_id)
        
        return {
            'success': True,
            'message': 'Booking created successfully',
            'booking_id': sales_invoice.name,
            'total_rental_amount': total_rental_amount,
            'advance_amount': flt(advance_amount),
            'pending_amount': pending_amount,
            'caution_deposit_amount': total_caution_deposit,
            'booking_url': f"/app/sales-invoice/{sales_invoice.name}"
        }
        
    except Exception as e:
        print(f"Error creating customer booking: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def search_customers(query="", limit=20):
    """Search customers for sales staff portal"""
    try:
        # Search by name, mobile, or email
        customers = frappe.db.sql("""
            SELECT 
                name, customer_name, mobile_number, email_id, 
                customer_group, creation,
                (SELECT COUNT(*) FROM `tabSales Invoice` si 
                 WHERE si.customer = c.name AND si.is_rental_booking = 1 AND si.docstatus = 1) as booking_count,
                (SELECT MAX(posting_date) FROM `tabSales Invoice` si 
                 WHERE si.customer = c.name AND si.is_rental_booking = 1 AND si.docstatus = 1) as last_booking_date
            FROM `tabCustomer` c
            WHERE c.disabled = 0
            AND (
                c.customer_name LIKE %s 
                OR c.mobile_number LIKE %s 
                OR c.email_id LIKE %s
                OR c.name LIKE %s
            )
            ORDER BY 
                CASE WHEN last_booking_date IS NULL THEN 1 ELSE 0 END,
                last_booking_date DESC,
                c.creation DESC
            LIMIT %s
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit), as_dict=True)
        
        return customers
        
    except Exception as e:
        frappe.log_error(f"Error searching customers: {str(e)}")
        return []

@frappe.whitelist()
def create_customer(customer_name, mobile_number=None, email_id=None, customer_group="Individual"):
    """Create new customer for sales staff portal"""
    try:
        # Check if customer with same mobile/email already exists
        if mobile_number:
            existing = frappe.db.get_value("Customer", {"mobile_number": mobile_number})
            if existing:
                return {'success': False, 'message': 'Customer with this mobile number already exists'}
                
        if email_id:
            existing = frappe.db.get_value("Customer", {"email_id": email_id})
            if existing:
                return {'success': False, 'message': 'Customer with this email already exists'}
        
        # Create customer
        customer_doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_group": customer_group,
            "territory": "All Territories",
            "mobile_number": mobile_number,
            "email_id": email_id
        })
        customer_doc.insert()
        
        return {
            'success': True,
            'message': 'Customer created successfully',
            'customer_id': customer_doc.name,
            'customer_name': customer_doc.customer_name
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating customer: {str(e)}")
        return {'success': False, 'message': str(e)}


# 3-Stage Booking Management Functions

@frappe.whitelist()
def confirm_booking_with_advance(booking_id, advance_amount, payment_mode="Cash"):
    """Stage 1: Confirm booking and collect advance payment"""
    try:
        advance_amount = flt(advance_amount)
        
        # Get the booking
        booking = frappe.get_doc("Sales Invoice", booking_id)
        if not booking.is_rental_booking:
            return {'success': False, 'message': 'Not a rental booking'}
        
        if booking.booking_status not in ("", None):
            return {'success': False, 'message': f'Booking is not in initial status (current: {booking.booking_status})'}
        
        # Update booking with advance amount
        booking.advance_amount = advance_amount
        booking.booking_status = "Confirmed"
        booking.save()
        
        # Submit the booking now that advance is collected
        booking.submit()
        
        # Create advance payment journal entry (handled by booking automation)
        
        # Calculate remaining amounts
        total_rental = booking.total
        remaining_balance = total_rental - advance_amount
        caution_deposit = booking.caution_deposit_amount or 0
        
        return {
            'success': True,
            'message': 'Booking confirmed with advance payment',
            'booking_id': booking.name,
            'advance_collected': advance_amount,
            'remaining_balance': remaining_balance,
            'caution_deposit_required': caution_deposit,
            'total_due_at_delivery': remaining_balance + caution_deposit
        }
        
    except Exception as e:
        frappe.log_error(f"Error confirming booking with advance: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def collect_balance_and_caution_deposit(booking_id, balance_amount, caution_deposit_amount, payment_mode="Cash"):
    """Stage 2: Collect remaining balance + caution deposit at item delivery"""
    try:
        balance_amount = flt(balance_amount)
        caution_deposit_amount = flt(caution_deposit_amount)
        
        # Get the booking
        booking = frappe.get_doc("Sales Invoice", booking_id)
        if not booking.is_rental_booking:
            return {'success': False, 'message': 'Not a rental booking'}
        
        if booking.booking_status != "Confirmed":
            return {'success': False, 'message': 'Booking must be confirmed first'}
        
        # Calculate expected amounts
        total_rental = booking.total
        advance_paid = booking.advance_amount or 0
        expected_balance = total_rental - advance_paid
        expected_caution = booking.caution_deposit_amount or 0
        
        # Validate amounts
        if abs(balance_amount - expected_balance) > 0.01:
            return {'success': False, 'message': f'Balance amount should be {expected_balance}'}
        
        if abs(caution_deposit_amount - expected_caution) > 0.01:
            return {'success': False, 'message': f'Caution deposit should be {expected_caution}'}
        
        # Update booking status and amounts using db_set for submitted documents
        booking.db_set('balance_amount_collected', balance_amount)
        booking.db_set('caution_deposit_collected', caution_deposit_amount)
        booking.db_set('booking_status', "Out for Rental")
        booking.db_set('actual_delivery_time', frappe.utils.now_datetime())
        
        # Reload the document to get updated values
        booking.reload()
        
        # Create payment entries for balance and caution deposit (handled by booking automation)
        
        return {
            'success': True,
            'message': 'Balance and caution deposit collected successfully',
            'booking_id': booking.name,
            'balance_collected': balance_amount,
            'caution_deposit_collected': caution_deposit_amount,
            'total_collected': balance_amount + caution_deposit_amount,
            'status': 'Out for Rental'
        }
        
    except Exception as e:
        frappe.log_error(f"Error collecting balance and caution deposit: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def process_item_return_and_refund(booking_id, caution_deposit_refund, deduction_amount=0, deduction_reason="", payment_mode="Cash"):
    """Stage 3: Process item return and caution deposit refund"""
    try:
        caution_deposit_refund = flt(caution_deposit_refund)
        deduction_amount = flt(deduction_amount)
        
        # Get the booking
        booking = frappe.get_doc("Sales Invoice", booking_id)
        if not booking.is_rental_booking:
            return {'success': False, 'message': 'Not a rental booking'}
        
        if booking.booking_status != "Out for Rental":
            return {'success': False, 'message': 'Items must be out for rental to process return'}
        
        # Calculate refund amounts
        caution_collected = booking.caution_deposit_collected or 0
        max_refund = caution_collected - deduction_amount
        
        if caution_deposit_refund > max_refund:
            return {'success': False, 'message': f'Refund cannot exceed {max_refund} (collected: {caution_collected} - deductions: {deduction_amount})'}
        
        # Update booking with return details using db_set for submitted documents
        booking.db_set('caution_deposit_refunded', caution_deposit_refund)
        booking.db_set('caution_deposit_deduction', deduction_amount)
        booking.db_set('deduction_reason', deduction_reason)
        booking.db_set('booking_status', "Completed")
        booking.db_set('actual_return_time', frappe.utils.now_datetime())
        
        if deduction_reason:
            existing_notes = booking.return_notes or ""
            new_notes = f"{existing_notes}\nDeduction: {deduction_reason}".strip()
            booking.db_set('return_notes', new_notes)
        
        # Reload the document to get updated values
        booking.reload()
        
        # Create refund journal entry (handled by booking automation)
        
        return {
            'success': True,
            'message': 'Item return processed and caution deposit refunded',
            'booking_id': booking.name,
            'caution_refunded': caution_deposit_refund,
            'deduction_amount': deduction_amount,
            'net_refund': caution_deposit_refund,
            'status': 'Completed'
        }
        
    except Exception as e:
        frappe.log_error(f"Error processing item return: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def get_booking_payment_summary(booking_id):
    """Get payment summary for a booking showing all 3 stages"""
    try:
        booking = frappe.get_doc("Sales Invoice", booking_id)
        if not booking.is_rental_booking:
            return {'success': False, 'message': 'Not a rental booking'}
        
        # Calculate amounts
        total_rental = booking.total
        advance_amount = booking.advance_amount or 0
        balance_collected = booking.balance_amount_collected or 0
        caution_collected = booking.caution_deposit_collected or 0
        caution_refunded = booking.caution_deposit_refunded or 0
        caution_deduction = booking.caution_deposit_deduction or 0
        
        # Calculate remaining amounts
        remaining_balance = total_rental - advance_amount - balance_collected
        remaining_caution_due = (booking.caution_deposit_amount or 0) - caution_collected
        remaining_caution_refund = caution_collected - caution_refunded - caution_deduction
        
        # Get booking items
        items = []
        for item in booking.items:
            items.append({
                'item_code': item.item_code,
                'item_name': item.item_name or item.item_code,
                'qty': item.qty,
                'rate': item.rate,
                'amount': item.amount
            })
        
        payment_summary = {
            'booking_id': booking.name,
            'customer': booking.customer_name,
            'customer_id': booking.customer,
            'booking_status': booking.booking_status,
            'total_rental_amount': total_rental,
            'items': items,
            
            # Stage 1: Advance
            'advance_amount': advance_amount,
            'advance_collected': advance_amount > 0,
            
            # Stage 2: Balance + Caution
            'balance_amount_due': total_rental - advance_amount,
            'balance_amount_collected': balance_collected,
            'remaining_balance': remaining_balance,
            'caution_deposit_due': booking.caution_deposit_amount or 0,
            'caution_deposit_collected': caution_collected,
            'remaining_caution_due': remaining_caution_due,
            'total_due_at_delivery': remaining_balance + remaining_caution_due,
            
            # Stage 3: Return & Refund
            'caution_deposit_refunded': caution_refunded,
            'caution_deposit_deduction': caution_deduction,
            'remaining_caution_refund': remaining_caution_refund,
            'deduction_reason': booking.deduction_reason or "",
            
            # Timestamps
            'booking_date': booking.posting_date,
            'delivery_time': booking.actual_delivery_time,
            'return_time': booking.actual_return_time,
            
            # Next actions
            'can_collect_advance': booking.booking_status in ("", None),
            'can_collect_balance': booking.booking_status == "Confirmed" and remaining_balance > 0,
            'can_collect_caution': booking.booking_status == "Confirmed" and remaining_caution_due > 0,
            'can_process_return': booking.booking_status == "Out for Rental",
            'can_refund_caution': booking.booking_status in ["Out for Rental", "Completed"] and remaining_caution_refund > 0
        }
        
        return {
            'success': True,
            'summary': payment_summary
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting booking payment summary: {str(e)}")
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def get_customer_active_bookings(customer_id):
    """Get all active bookings for a customer"""
    try:
        bookings = frappe.db.sql("""
            SELECT 
                si.name as booking_id,
                si.posting_date,
                si.customer_name,
                si.total as rental_amount,
                si.booking_status,
                si.advance_amount,
                si.caution_deposit_amount,
                si.balance_amount_collected,
                si.caution_deposit_collected,
                si.caution_deposit_refunded,
                si.actual_delivery_time,
                si.actual_return_time,
                COUNT(sii.name) as item_count,
                GROUP_CONCAT(sii.item_name SEPARATOR ', ') as items
            FROM `tabSales Invoice` si
            LEFT JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
            WHERE si.customer = %s 
            AND si.is_rental_booking = 1
            AND si.docstatus = 1
            AND si.booking_status NOT IN ('Cancelled', 'Completed')
            GROUP BY si.name
            ORDER BY si.posting_date DESC
        """, (customer_id,), as_dict=True)
        
        return {
            'success': True,
            'bookings': bookings
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting customer active bookings: {str(e)}")
        return {'success': False, 'message': str(e)}
