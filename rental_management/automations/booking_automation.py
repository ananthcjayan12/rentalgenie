import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, flt

def validate_sales_invoice(doc, method):
    """Validate rental booking before saving"""
    if doc.is_rental_booking:
        # Calculate rental dates
        calculate_rental_dates(doc)
        
        # Check item availability
        check_item_availability(doc)
        
        # Calculate rental amounts
        calculate_rental_amounts(doc)
        
        # Calculate pending amount after advance payments
        calculate_pending_amount(doc)
        
        # Validate exchange booking
        if doc.is_exchange_booking:
            validate_exchange_booking(doc)

def get_owner_commission_account(owner_name, company=None):
	"""Get commission account for an owner"""
	try:
		owner = frappe.get_doc("Third Party Owner", owner_name)
		return owner.get_commission_account(company)
	except Exception as e:
		print(f"Error getting commission account for owner {owner_name}: {str(e)}")
		return None


def calculate_rental_dates(doc):
    """Calculate rental start and end dates based on function date"""
    if doc.function_date and doc.rental_duration_days:
        function_date = getdate(doc.function_date)
        
        # Calculate rental start date (2 days before function)
        rental_start_date = add_days(function_date, -2)
        
        # Calculate rental end date (start date + rental duration)
        rental_end_date = add_days(rental_start_date, doc.rental_duration_days)
        
        doc.rental_start_date = rental_start_date
        doc.rental_end_date = rental_end_date

def check_item_availability(doc):
    """Check if rental items are available for the booking period"""
    if not doc.rental_start_date or not doc.rental_end_date:
        return
    
    for item in doc.items:
        # Get item details to check if it's a rental item
        item_doc = frappe.get_doc("Item", item.item_code)
        
        if item_doc.is_rental_item:
            # Check if item is available for the rental period
            conflicting_bookings = frappe.db.sql("""
                SELECT si.name, si.customer, si.rental_start_date, si.rental_end_date
                FROM `tabSales Invoice` si
                JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
                WHERE sii.item_code = %s
                AND si.is_rental_booking = 1
                AND si.docstatus = 1
                AND si.booking_status NOT IN ('Cancelled', 'Completed', 'Exchanged')
                AND si.name != %s
                AND (
                    (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR
                    (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR
                    (si.rental_start_date >= %s AND si.rental_end_date <= %s)
                )
            """, (
                item.item_code, 
                doc.name or "",
                doc.rental_start_date, doc.rental_start_date,
                doc.rental_end_date, doc.rental_end_date,
                doc.rental_start_date, doc.rental_end_date
            ), as_dict=True)
            
            if conflicting_bookings:
                conflict = conflicting_bookings[0]
                frappe.throw(_(
                    "Item {0} is already booked from {1} to {2} for customer {3} (Booking: {4})"
                ).format(
                    item.item_code,
                    conflict.rental_start_date,
                    conflict.rental_end_date,
                    conflict.customer,
                    conflict.name
                ))

def calculate_rental_amounts(doc):
    """Calculate rental amounts and commission automatically"""
    total_commission = 0
    caution_deposit = 0
    
    for item in doc.items:
        if item.item_code:
            item_doc = frappe.get_doc("Item", item.item_code)
            
            if item_doc.get("is_rental_item"):
                # Calculate commission for this item
                # Calculate commission for this item
                commission_fixed = flt(item_doc.get("owner_commission_fixed", 0))
                commission_rate = flt(item_doc.get("owner_commission_percent", 0))
                
                item_commission = 0
                if commission_fixed > 0:
                    # Fixed commission: Flat amount per item (multiplied only by qty, NOT days)
                    qty = flt(item.qty) or 1
                    item_commission = commission_fixed * qty
                elif commission_rate and item.amount:
                    item_commission = (item.amount * commission_rate) / 100
                    
                if item_commission:
                    total_commission += item_commission
                
                # Add to caution deposit calculation if needed
                item_caution = flt(item_doc.get("suggested_caution_deposit") or 0)
                if item_caution > caution_deposit:
                    caution_deposit = item_caution
    
    doc.total_owner_commission = total_commission
    
    # Set caution deposit if not already set
    if not doc.caution_deposit_amount:
        doc.caution_deposit_amount = caution_deposit  # Default amount

def validate_exchange_booking(doc):
    """Validate exchange booking details"""
    if not doc.original_booking_reference:
        frappe.throw(_("Original Booking Reference is required for exchange bookings"))
    
    # Verify original booking exists and is valid
    original_booking = frappe.get_doc("Sales Invoice", doc.original_booking_reference)
    if not original_booking.is_rental_booking:
        frappe.throw(_("Original booking must be a rental booking"))
    
    if original_booking.booking_status in ['Cancelled', 'Completed', 'Exchanged']:
        frappe.throw(_("Cannot exchange booking with status: {0}").format(original_booking.booking_status))
    
    # Transfer advance from original booking
    if not doc.advance_amount and original_booking.get("advance_amount"):
        doc.advance_amount = original_booking.advance_amount

def on_submit_sales_invoice(doc, method):
    """Handle post-submission tasks for rental bookings"""
    if doc.is_rental_booking:
        # Update booking status
        doc.booking_status = "Confirmed"
        
        # Update item rental status
        update_item_rental_status(doc, "Booked")
        
        # Create advance payment entry if amount is specified
        # NOTE: Advance payment is now handled in confirm_booking_with_advance() API function
        # to ensure proper Payment Entry allocation against the Sales Invoice
        # if doc.advance_amount:
        #     create_advance_payment_entry(doc)
        
        # Create caution deposit entry if amount is specified
        if doc.caution_deposit_amount:
            create_caution_deposit_entry(doc)
        
        # Create owner commission liability entries for third-party items
        # NOTE: Commission creation moved to delivery stage (collect_balance_and_caution_deposit)
        # Commission liability should only be created when items are actually delivered
        # try:
        #     create_owner_commission_liabilities(doc)
        # except Exception as e:
        #     # Log but do not block booking submission
        #     print(f"Error creating owner commission entries for {doc.name}: {str(e)}")
        
        # Update customer statistics
        update_customer_stats(doc)
        
        # Handle exchange booking
        if doc.is_exchange_booking and doc.original_booking_reference:
            # Mark original booking as exchanged
            frappe.db.set_value("Sales Invoice", doc.original_booking_reference, "booking_status", "Exchanged")

def on_cancel_sales_invoice(doc, method):
    """Handle booking cancellation"""
    if doc.is_rental_booking:
        # Update booking status
        doc.booking_status = "Cancelled"
        
        # Update item rental status back to available
        update_item_rental_status(doc, "Available")
        
        # Update customer stats
        update_customer_stats(doc)
        
        # If this was an exchange booking, revert original booking status
        if doc.is_exchange_booking and doc.original_booking_reference:
            frappe.db.set_value("Sales Invoice", doc.original_booking_reference, "booking_status", "Confirmed")

def update_item_rental_status(doc, status):
    """Update rental status of items in the booking"""
    for item in doc.items:
        # Check if item is a rental item
        item_doc = frappe.get_doc("Item", item.item_code)
        if item_doc.is_rental_item:
            frappe.db.set_value("Item", item.item_code, "current_rental_status", status)

def create_caution_deposit_entry(doc):
    """Create journal entry for caution deposit liability"""
    try:
        company_abbr = frappe.get_value("Company", doc.company, "abbr")
        
        # Create caution deposit liability account if it doesn't exist
        caution_deposit_account = create_caution_deposit_account(doc.company)
        
        # Get default cash account
        cash_account = frappe.get_value("Company", doc.company, "default_cash_account")
        if not cash_account:
            cash_account = frappe.db.get_value("Account", 
                                             {"account_type": "Cash", "company": doc.company}, 
                                             "name")
        
        if not cash_account:
            print(f"No cash account found for company {doc.company}")
            return
        
        # Create journal entry for caution deposit
        je = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "posting_date": doc.posting_date,
            "company": doc.company,
            "user_remark": f"Caution deposit received for booking {doc.name}",
            "accounts": [
                {
                    "account": cash_account,
                    "debit_in_account_currency": flt(doc.caution_deposit_amount),
                    "credit_in_account_currency": 0
                },
                {
                    "account": caution_deposit_account,
                    "debit_in_account_currency": 0,
                    "credit_in_account_currency": flt(doc.caution_deposit_amount),
                    "party_type": "Customer",
                    "party": doc.customer
                }
            ]
        })
        
        # Try to insert without submit first
        je.insert(ignore_permissions=True)
        
        # Then submit if insertion successful
        try:
            je.submit()
            frappe.msgprint(f"Caution deposit journal entry {je.name} created successfully", alert=True)
        except Exception as submit_error:
            frappe.msgprint(f"Journal entry created but submission failed: {str(submit_error)}", alert=True)
        
    except Exception as e:
        # Don't fail the booking if journal entry fails, just log it
        frappe.msgprint(f"Caution deposit journal entry could not be created: {str(e)}", alert=True)
        print(f"Error creating caution deposit entry for {doc.name}: {str(e)}", "Rental Management")

def create_caution_deposit_account(company):
    """Create caution deposit liability account if it doesn't exist"""
    company_abbr = frappe.get_value("Company", company, "abbr")
    account_name = f"Caution Deposits Received - {company_abbr}"
    
    if not frappe.db.exists("Account", account_name):
        # Get parent account - use Current Liabilities
        parent_account = f"Current Liabilities - {company_abbr}"
        
        # Create as a regular liability account without special account type
        account = frappe.get_doc({
            "doctype": "Account",
            "account_name": "Caution Deposits Received",
            "parent_account": parent_account,
            "company": company,
            "is_group": 0,
            "account_currency": frappe.get_value("Company", company, "default_currency")
        })
        account.insert(ignore_permissions=True)
        return account.name
    
    return account_name

def update_customer_stats(doc):
    """Update customer booking statistics"""
    try:
        from rental_management.automations.customer_automation import update_customer_booking_stats
        update_customer_booking_stats(doc.customer, doc.posting_date)
    except Exception as e:
        print(f"Error updating customer stats for {doc.name}: {str(e)}")

# Utility functions for booking status management
@frappe.whitelist()
def update_booking_status(booking_name, new_status, notes=None):
    """Update booking status with proper validation"""
    booking = frappe.get_doc("Sales Invoice", booking_name)
    
    if not booking.is_rental_booking:
        frappe.throw(_("Not a rental booking"))
    
    old_status = booking.booking_status
    booking.booking_status = new_status
    
    # Handle status-specific actions
    if new_status == "Out for Rental":
        booking.actual_delivery_time = now_datetime()
        if notes:
            booking.delivery_notes = notes
            
    elif new_status == "Returned":
        booking.actual_return_time = now_datetime()
        if notes:
            booking.return_notes = notes
            
    elif new_status == "Completed":
        booking.actual_return_time = booking.actual_return_time or now_datetime()
        
    booking.save()
    frappe.db.commit()
    
    return {
        "status": "success",
        "message": f"Booking status updated from {old_status} to {new_status}"
    }

@frappe.whitelist()
def process_caution_deposit_refund(booking_name, refund_amount, refund_notes=None):
    """Process caution deposit refund"""
    booking = frappe.get_doc("Sales Invoice", booking_name)
    refund_amount = flt(refund_amount)
    
    # Validate refund amount
    max_refund = booking.caution_deposit_amount - booking.caution_deposit_refunded
    if refund_amount > max_refund:
        frappe.throw(_("Refund amount cannot exceed remaining deposit of {0}").format(max_refund))
    
    # Update booking
    booking.caution_deposit_refunded += refund_amount
    
    if refund_notes:
        existing_notes = booking.return_notes or ""
        booking.return_notes = f"{existing_notes}\nRefund: {refund_notes}".strip()
    
    booking.save()
    frappe.db.commit()
    
    return {
        "status": "success",
        "message": f"Refund of {refund_amount} processed successfully"
    }

# Quick action functions for booking management
@frappe.whitelist()
def mark_delivered(booking_name, notes=None):
    """Quick action to mark booking as delivered"""
    return update_booking_status(booking_name, "Out for Rental", notes)

@frappe.whitelist()
def mark_returned(booking_name, notes=None):
    """Quick action to mark booking as returned"""
    return update_booking_status(booking_name, "Returned", notes)

@frappe.whitelist()
def complete_booking(booking_name, notes=None):
    """Quick action to complete booking"""
    return update_booking_status(booking_name, "Completed", notes)

def create_owner_commission_liabilities(doc):
    """Aggregate owner commissions per supplier and create Journal Entries to reflect liability.

    Added verbose debug logging to help trace why commission JEs may not be created or reflected.
    """
    try:
        company = doc.company
        print(f"[DEBUG] create_owner_commission_liabilities START - doc: {doc.name}, company: {company}")
        if not company:
            print(f"[DEBUG] No company on document {doc.name}")
            return

        # Aggregate commission amounts by supplier
        supplier_commissions = {}
        for idx, item in enumerate(doc.items or []):
            try:
                if not item.item_code:
                    print(f"[DEBUG] Skipping empty item line {idx} on {doc.name}")
                    continue

                # Try to fetch the Item doc for the invoice line
                try:
                    item_doc = frappe.get_doc("Item", item.item_code)
                except Exception as e:
                    print(f"[DEBUG] Could not fetch Item {getattr(item,'item_code',None)} on {doc.name}: {str(e)}")
                    item_doc = None

                # If the invoice line references a service item (rental service), map back to the original physical item
                # The original Item stores the link in the field `rental_service_item`.
                if item_doc and not bool(item_doc.get("is_third_party_item")):
                    # Heuristic: service items are non-stock or have codes ending with '-RENTAL'
                    is_service_like = (not bool(item_doc.get("is_stock_item"))) or (str(item.item_code).upper().endswith("-RENTAL"))
                    if is_service_like:
                        parent_item_code = frappe.db.get_value("Item", {"rental_service_item": item.item_code}, "name")
                        if parent_item_code:
                            try:
                                parent_item_doc = frappe.get_doc("Item", parent_item_code)
                                print(f"[DEBUG] Mapped service item {item.item_code} to parent item {parent_item_code} for booking {doc.name}")
                                item_doc = parent_item_doc
                            except Exception as e:
                                print(f"[DEBUG] Failed to fetch parent Item {parent_item_code}: {str(e)}")

                # If still no item_doc, skip
                if not item_doc:
                    print(f"[DEBUG] No Item doc resolved for line {idx} ({getattr(item,'item_code',None)}) on {doc.name}")
                    continue

                is_third = bool(item_doc.get("is_third_party_item"))
                third_party_owner = item_doc.get("third_party_owner")
                commission_pct = flt(item_doc.get("owner_commission_percent") or 0)
                commission_fixed = flt(item_doc.get("owner_commission_fixed") or 0)
                line_amount = flt(item.amount or 0)

                print(f"[DEBUG] Line {idx} - item: {item.item_code}, resolved_item: {item_doc.name}, is_third: {is_third}, owner: {third_party_owner}, commission_pct: {commission_pct}, commission_fixed: {commission_fixed}, line_amount: {line_amount}")

                if is_third and third_party_owner:
                    comm_amount = 0
                    if commission_fixed > 0:
                        # Fixed commission: Flat amount per item (multiplied only by qty, NOT by days)
                        qty = flt(item.get("qty") or 1)
                        comm_amount = commission_fixed * qty
                        print(f"[DEBUG] Using fixed commission: {commission_fixed} * qty={qty} = {comm_amount}")
                    elif commission_pct and line_amount:
                        comm_amount = (line_amount * commission_pct) / 100.0
                    
                    if comm_amount:
                        supplier_commissions[third_party_owner] = supplier_commissions.get(third_party_owner, 0.0) + comm_amount
                        print(f"[DEBUG] Accumulated commission for {third_party_owner}: {supplier_commissions[third_party_owner]}")

            except Exception as e:
                print(f"[DEBUG] Error processing line {idx} on {doc.name}: {str(e)}")
                import traceback
                traceback.print_exc()

        print(f"[DEBUG] owner_commissions computed: {supplier_commissions}")

        if not supplier_commissions:
            print(f"[DEBUG] No owner commissions to process for {doc.name}")
            return

        company_abbr = frappe.get_value("Company", company, "abbr")

        # Resolve accounts
        payable_account = frappe.db.get_value("Account", {"account_type": "Payable", "company": company}, "name")
        print(f"[DEBUG] initial payable_account lookup result: {payable_account}")
        if not payable_account:
            # Fallback to caution deposit parent (Current Liabilities) if exists
            payable_account = f"Current Liabilities - {company_abbr}"
            print(f"[DEBUG] fallback payable_account: {payable_account}")
            if not frappe.db.exists("Account", payable_account):
                try:
                    parent = None
                    if frappe.db.exists("Account", f"Current Liabilities - {company_abbr}"):
                        parent = f"Current Liabilities - {company_abbr}"
                    else:
                        parent = frappe.get_value("Account", {"is_group": 1, "company": company}, "name") or None
                    acct = frappe.get_doc({
                        "doctype": "Account",
                        "account_name": "Owner Commission Payable",
                        "parent_account": parent or "Current Liabilities",
                        "company": company,
                        "is_group": 0
                    })
                    acct.insert(ignore_permissions=True)
                    payable_account = acct.name
                    print(f"[DEBUG] Created payable_account: {payable_account}")
                except Exception as e:
                    print(f"[ERROR] Failed to create payable account for {company}: {str(e)}\n{frappe.get_traceback()}")
                    raise

        # Find or create commission expense account
        commission_expense_account = None
        preferred_name = f"Owner Commission Expense - {company_abbr}"
        if frappe.db.exists("Account", preferred_name):
            commission_expense_account = preferred_name
        else:
            commission_expense_account = frappe.db.get_value("Account", {"account_type": "Expense", "company": company}, "name")
            print(f"[DEBUG] initial commission_expense_account lookup result: {commission_expense_account}")
            if not commission_expense_account:
                try:
                    parent_expense = None
                    for candidate in [f"Direct Expenses - {company_abbr}", f"Expenses - {company_abbr}", f"Profit and Loss - {company_abbr}"]:
                        if frappe.db.exists("Account", candidate):
                            parent_expense = candidate
                            break
                    if not parent_expense:
                        parent_expense = frappe.get_value("Account", {"company": company, "is_group": 1}, "name")
                    acct = frappe.get_doc({
                        "doctype": "Account",
                        "account_name": "Owner Commission Expense",
                        "parent_account": parent_expense or "Direct Expenses",
                        "company": company,
                        "is_group": 0
                    })
                    acct.insert(ignore_permissions=True)
                    commission_expense_account = acct.name
                    print(f"[DEBUG] Created commission_expense_account: {commission_expense_account}")
                except Exception as e:
                    print(f"[ERROR] Failed to create commission expense account for {company}: {str(e)}\n{frappe.get_traceback()}")
                    raise

        print(f"[DEBUG] Using payable_account: {payable_account}, commission_expense_account: {commission_expense_account}")

        # For each third party owner create a Journal Entry to book the liability
        commissions_created = False
        for owner_name, amount in supplier_commissions.items():
            try:
                if flt(amount) <= 0:
                    print(f"[DEBUG] Skipping zero/negative commission for {owner_name}: {amount}")
                    continue

                # Get the owner's dedicated commission account and supplier link
                owner_commission_account = get_owner_commission_account(owner_name, company)
                
                if not owner_commission_account:
                    print(f"[ERROR] No commission account found for owner {owner_name}")
                    continue

                # Get the supplier link from Third Party Owner for party details
                owner_doc = frappe.get_doc("Third Party Owner", owner_name)
                supplier_link = owner_doc.supplier_link
                
                if not supplier_link:
                    print(f"[ERROR] No supplier link found for owner {owner_name}")
                    continue

                je = frappe.get_doc({
                    "doctype": "Journal Entry",
                    "voucher_type": "Journal Entry",
                    "posting_date": doc.posting_date or frappe.utils.nowdate(),
                    "company": company,
                    "user_remark": f"Owner commission for booking {doc.name} - Owner {owner_name}",
                    "accounts": [
                        {
                            "account": commission_expense_account,
                            "debit_in_account_currency": flt(amount),
                            "credit_in_account_currency": 0
                        },
                        {
                            "account": owner_commission_account,
                            "debit_in_account_currency": 0,
                            "credit_in_account_currency": flt(amount),
                            "party_type": "Supplier",
                            "party": supplier_link
                        }
                    ]
                })

                print(f"[DEBUG] Inserting JE for owner {owner_name} amount {amount}")
                je.insert(ignore_permissions=True)
                print(f"[DEBUG] JE inserted: {je.name}")
                try:
                    je.submit()
                    print(f"[DEBUG] JE submitted: {je.name}")
                    commissions_created = True
                except Exception as sub_e:
                    print(f"[ERROR] JE submit failed for {je.name}: {str(sub_e)}\n{frappe.get_traceback()}")
            except Exception as e:
                print(f"[ERROR] Failed to create owner commission JE for booking {doc.name}, owner {owner_name}: {str(e)}\n{frappe.get_traceback()}")
        
        # Mark commission as created on the booking if any commissions were successfully created
        if commissions_created:
            try:
                doc.db_set('owner_commission_created', 1)
                print(f"[DEBUG] Set owner_commission_created flag for booking {doc.name}")
            except Exception as e:
                print(f"[ERROR] Failed to set owner_commission_created flag for {doc.name}: {str(e)}")

    except Exception as e:
        print(f"[FATAL] create_owner_commission_liabilities failed for {getattr(doc,'name',None)}: {str(e)}\n{frappe.get_traceback()}")
        # Do not re-raise to avoid blocking booking submission
        return

def create_advance_payment_entry(doc):
    """Create journal entry for advance payment received"""
    try:
        company_abbr = frappe.get_value("Company", doc.company, "abbr")
        
        # Create advance payment liability account if it doesn't exist
        advance_payment_account = create_advance_payment_account(doc.company)
        
        # Get default cash account
        cash_account = frappe.get_value("Company", doc.company, "default_cash_account")
        if not cash_account:
            cash_account = frappe.db.get_value("Account", 
                                             {"account_type": "Cash", "company": doc.company}, 
                                             "name")
        
        if not cash_account:
            print(f"No cash account found for company {doc.company}")
            return
        
        # Create journal entry for advance payment
        je = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "posting_date": doc.posting_date,
            "company": doc.company,
            "user_remark": f"Advance payment received for booking {doc.name}",
            "accounts": [
                {
                    "account": cash_account,
                    "debit_in_account_currency": flt(doc.advance_amount),
                    "credit_in_account_currency": 0
                },
                {
                    "account": advance_payment_account,
                    "debit_in_account_currency": 0,
                    "credit_in_account_currency": flt(doc.advance_amount),
                    "party_type": "Customer",
                    "party": doc.customer
                }
            ]
        })
        
        # Insert and submit the journal entry
        je.insert(ignore_permissions=True)
        
        try:
            je.submit()
            frappe.msgprint(f"Advance payment journal entry {je.name} created successfully", alert=True)
        except Exception as submit_error:
            frappe.msgprint(f"Advance payment journal entry created but submission failed: {str(submit_error)}", alert=True)
        
    except Exception as e:
        # Don't fail the booking if journal entry fails, just log it
        frappe.msgprint(f"Advance payment journal entry could not be created: {str(e)}", alert=True)
        print(f"Error creating advance payment entry for {doc.name}: {str(e)}", "Rental Management")

def create_advance_payment_account(company):
    """Create advance payment liability account if it doesn't exist"""
    company_abbr = frappe.get_value("Company", company, "abbr")
    account_name = f"Customer Advance Payments - {company_abbr}"
    
    if not frappe.db.exists("Account", account_name):
        # Get parent account - use Current Liabilities
        parent_account = f"Current Liabilities - {company_abbr}"
        
        # Create the advance payment liability account
        account = frappe.get_doc({
            "doctype": "Account",
            "account_name": "Customer Advance Payments",
            "parent_account": parent_account,
            "company": company,
            "is_group": 0,
            "account_currency": frappe.get_value("Company", company, "default_currency")
        })
        account.insert(ignore_permissions=True)
        return account.name
    
    return account_name

def calculate_pending_amount(doc):
    """Calculate pending amount after advance payment and caution deposit"""
    if not doc.is_rental_booking:
        return
    
    # Get total invoice amount
    total_amount = flt(doc.grand_total or doc.total or 0)
    
    # Get advance payment and caution deposit amounts
    advance_amount = flt(doc.advance_amount or 0)
    caution_deposit = flt(doc.caution_deposit_amount or 0)
    
    # Calculate pending amount (total - advance - caution deposit)
    # Both advance and caution deposit are money already received from customer
    pending_amount = total_amount - advance_amount - caution_deposit
    
    # Set the outstanding amount to pending amount
    doc.outstanding_amount = pending_amount
    
    # Add a custom field to track this for reporting
    if hasattr(doc, 'pending_payment_amount'):
        doc.pending_payment_amount = pending_amount
    
    return pending_amount

@frappe.whitelist()
def create_payment_with_advance_allocation(sales_invoice_name, payment_amount, payment_mode="Cash"):
    """Create payment entry considering advance payment allocation"""
    try:
        si_doc = frappe.get_doc("Sales Invoice", sales_invoice_name)
        
        if not si_doc.is_rental_booking:
            frappe.throw(_("This is not a rental booking"))
        
        # Calculate amounts
        total_amount = flt(si_doc.grand_total)
        advance_amount = flt(si_doc.advance_amount or 0)
        payment_amount = flt(payment_amount)
        
        # The payment should only be for remaining balance
        remaining_balance = total_amount - advance_amount
        
        if payment_amount > remaining_balance:
            frappe.throw(_("Payment amount cannot exceed remaining balance of {0}").format(remaining_balance))
        
        # Create payment entry for the actual payment
        if payment_amount > 0:
            payment_entry = frappe.get_doc({
                "doctype": "Payment Entry",
                "payment_type": "Receive",
                "party_type": "Customer", 
                "party": si_doc.customer,
                "company": si_doc.company,
                "posting_date": frappe.utils.nowdate(),
                "paid_amount": payment_amount,
                "received_amount": payment_amount,
                "references": [{
                    "reference_doctype": "Sales Invoice",
                    "reference_name": sales_invoice_name,
                    "allocated_amount": payment_amount
                }]
            })
            
            payment_entry.insert(ignore_permissions=True)
            payment_entry.submit()
        
        return {
            "status": "success",
            "remaining_balance": remaining_balance - payment_amount
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_pending_amount(sales_invoice_name):
    """Get pending amount for a rental booking after advance payments"""
    try:
        si_doc = frappe.get_doc("Sales Invoice", sales_invoice_name)
        
        if not si_doc.is_rental_booking:
            return {"error": "Not a rental booking"}
        
        total_amount = flt(si_doc.grand_total)
        advance_amount = flt(si_doc.advance_amount or 0)
        caution_deposit = flt(si_doc.caution_deposit_amount or 0)
        
        # Calculate pending amount (total - advance - caution deposit)
        # Both advance and caution deposit are money already received from customer
        pending_amount = total_amount - advance_amount - caution_deposit
        
        return {
            "total_amount": total_amount,
            "advance_amount": advance_amount,
            "caution_deposit": caution_deposit,
            "pending_amount": pending_amount,
            "outstanding_amount": si_doc.outstanding_amount
        }
        
    except Exception as e:
        return {"error": str(e)}
