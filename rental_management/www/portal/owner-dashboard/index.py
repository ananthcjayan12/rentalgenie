import frappe
from frappe.utils import flt, formatdate

def get_context(context):
    """Get context for owner dashboard page"""
    
    context.no_cache = 1
    
    # Check if user is logged in
    if not frappe.session.user or frappe.session.user == 'Guest':
        frappe.local.flags.redirect_location = '/login?redirect-to=/portal/owner-dashboard'
        raise frappe.Redirect
    
    # Get owner_id from URL parameter (for admin viewing specific owner)
    owner_id = frappe.form_dict.get('owner')
    
    # If no owner specified, try to find owner linked to current user's email
    if not owner_id:
        owner_id = frappe.db.get_value(
            'Third Party Owner',
            {'email': frappe.session.user, 'disabled': 0},
            'name'
        )
    
    # Check if user is admin (System Manager role)
    is_admin = 'System Manager' in frappe.get_roles(frappe.session.user)
    
    # If not admin and trying to view different owner, redirect
    if owner_id and not is_admin:
        user_owner = frappe.db.get_value(
            'Third Party Owner',
            {'email': frappe.session.user, 'disabled': 0},
            'name'
        )
        if user_owner and user_owner != owner_id:
            frappe.throw("You don't have permission to view this owner's dashboard")
    
    context.owner = None
    context.owner_stats = {}
    context.owner_items = []
    context.recent_sales = []
    context.commission_history = []
    context.all_owners = []
    context.is_admin = is_admin
    context.selected_owner_id = owner_id
    
    # If admin, get list of all owners for dropdown
    if is_admin:
        context.all_owners = frappe.db.sql("""
            SELECT name, owner_name, email, phone, default_commission_rate
            FROM `tabThird Party Owner`
            WHERE disabled = 0
            ORDER BY owner_name
        """, as_dict=True)
    
    if not owner_id:
        context.page_title = "Owner Dashboard | Blush & Glow"
        context.meta_description = "Third party owner rental dashboard"
        return context
    
    # Get owner details
    try:
        owner = frappe.get_doc('Third Party Owner', owner_id)
        context.owner = owner
    except Exception:
        context.error_message = "Owner not found"
        return context
    
    # Get owner statistics
    context.owner_stats = get_owner_stats(owner_id)
    
    # Get owner's items
    context.owner_items = get_owner_items(owner_id)
    
    # Get recent sales
    context.recent_sales = get_owner_sales(owner_id)
    
    # Get commission history
    context.commission_history = get_commission_history(owner_id)
    
    context.page_title = f"Owner Dashboard - {owner.owner_name} | Blush & Glow"
    context.meta_description = f"Dashboard for {owner.owner_name} showing rental items and commission details"
    
    return context


def get_owner_stats(owner_id):
    """Calculate owner statistics"""
    stats = {
        'total_items': 0,
        'active_items': 0,
        'total_rentals': 0,
        'total_sales_amount': 0,
        'commission_earned': 0,
        'commission_received': 0,
        'commission_pending': 0
    }
    
    # Count items
    items_count = frappe.db.sql("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN disabled = 0 THEN 1 ELSE 0 END) as active
        FROM `tabItem`
        WHERE third_party_owner = %s
    """, (owner_id,), as_dict=True)
    
    if items_count:
        stats['total_items'] = items_count[0].total or 0
        stats['active_items'] = items_count[0].active or 0
    
    # Get sales data from submitted Sales Invoices
    sales_data = frappe.db.sql("""
        SELECT 
            COUNT(DISTINCT si.name) as rentals,
            SUM(sii.amount) as total_amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        JOIN `tabItem` i ON sii.item_code = i.name
        WHERE i.third_party_owner = %s
        AND si.docstatus = 1
        AND si.is_rental_booking = 1
    """, (owner_id,), as_dict=True)
    
    if sales_data and sales_data[0]:
        stats['total_rentals'] = sales_data[0].rentals or 0
        stats['total_sales_amount'] = flt(sales_data[0].total_amount or 0)
    
    # Calculate commission from Journal Entries (commission payable entries)
    commission_data = frappe.db.sql("""
        SELECT 
            SUM(CASE WHEN je.docstatus = 1 THEN jea.credit ELSE 0 END) as earned,
            SUM(CASE WHEN je.docstatus = 1 AND jea.is_advance = 1 THEN jea.credit ELSE 0 END) as received
        FROM `tabJournal Entry` je
        JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
        WHERE jea.party_type = 'Supplier'
        AND jea.party = (SELECT supplier_link FROM `tabThird Party Owner` WHERE name = %s)
        AND je.docstatus = 1
    """, (owner_id,), as_dict=True)
    
    if commission_data and commission_data[0]:
        stats['commission_earned'] = flt(commission_data[0].earned or 0)
        stats['commission_received'] = flt(commission_data[0].received or 0)
    
    # Alternative: Calculate commission directly from invoice items with owner commission
    commission_from_invoices = frappe.db.sql("""
        SELECT SUM(
            CASE 
                WHEN i.owner_commission_fixed > 0 THEN i.owner_commission_fixed * sii.qty
                WHEN i.owner_commission_percent > 0 THEN sii.amount * (i.owner_commission_percent / 100)
                ELSE 0
            END
        ) as total_commission
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        JOIN `tabItem` i ON sii.item_code = i.name
        WHERE i.third_party_owner = %s
        AND si.docstatus = 1
        AND si.is_rental_booking = 1
    """, (owner_id,), as_dict=True)
    
    if commission_from_invoices and commission_from_invoices[0]:
        calculated_commission = flt(commission_from_invoices[0].total_commission or 0)
        if calculated_commission > stats['commission_earned']:
            stats['commission_earned'] = calculated_commission
    
    # Commission pending = earned - received
    stats['commission_pending'] = stats['commission_earned'] - stats['commission_received']
    
    return stats


def get_owner_items(owner_id):
    """Get items belonging to owner"""
    items = frappe.db.sql("""
        SELECT 
            i.name,
            i.item_name,
            i.item_group,
            i.rental_rate_per_day,
            i.disabled,
            i.owner_commission_percent,
            i.owner_commission_fixed,
            i.image,
            (SELECT COUNT(*) FROM `tabSales Invoice Item` sii 
             JOIN `tabSales Invoice` si ON sii.parent = si.name
             WHERE sii.item_code = i.name AND si.docstatus = 1 AND si.is_rental_booking = 1) as rental_count,
            (SELECT SUM(sii.amount) FROM `tabSales Invoice Item` sii 
             JOIN `tabSales Invoice` si ON sii.parent = si.name
             WHERE sii.item_code = i.name AND si.docstatus = 1 AND si.is_rental_booking = 1) as total_revenue
        FROM `tabItem` i
        WHERE i.third_party_owner = %s
        ORDER BY i.creation DESC
    """, (owner_id,), as_dict=True)
    
    return items


def get_owner_sales(owner_id, limit=10):
    """Get recent sales for owner's items"""
    sales = frappe.db.sql("""
        SELECT 
            si.name as invoice_id,
            si.posting_date,
            si.customer_name,
            si.booking_status,
            sii.item_name,
            sii.qty,
            sii.amount,
            i.owner_commission_percent,
            i.owner_commission_fixed,
            CASE 
                WHEN i.owner_commission_fixed > 0 THEN i.owner_commission_fixed * sii.qty
                WHEN i.owner_commission_percent > 0 THEN sii.amount * (i.owner_commission_percent / 100)
                ELSE 0
            END as commission_amount
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        JOIN `tabItem` i ON sii.item_code = i.name
        WHERE i.third_party_owner = %s
        AND si.docstatus = 1
        AND si.is_rental_booking = 1
        ORDER BY si.posting_date DESC, si.creation DESC
        LIMIT %s
    """, (owner_id, limit), as_dict=True)
    
    return sales


def get_commission_history(owner_id, limit=10):
    """Get commission payment history for owner"""
    # Get supplier link
    supplier = frappe.db.get_value('Third Party Owner', owner_id, 'supplier_link')
    
    if not supplier:
        return []
    
    history = frappe.db.sql("""
        SELECT 
            je.name as journal_entry,
            je.posting_date,
            je.cheque_no as reference,
            jea.credit as amount,
            je.user_remark as remarks
        FROM `tabJournal Entry` je
        JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
        WHERE jea.party_type = 'Supplier'
        AND jea.party = %s
        AND jea.credit > 0
        AND je.docstatus = 1
        ORDER BY je.posting_date DESC
        LIMIT %s
    """, (supplier, limit), as_dict=True)
    
    return history
