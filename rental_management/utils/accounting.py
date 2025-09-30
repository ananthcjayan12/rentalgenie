import frappe
from frappe.utils import flt, today, now_datetime
from rental_management.setup.install import get_rental_accounts

def create_advance_revenue_journal_entry(booking_id, advance_amount, company=None):
    """Create journal entry for advance payment - directly to revenue"""
    try:
        accounts = get_rental_accounts(company)
        advance_amount = flt(advance_amount)
        
        if advance_amount <= 0:
            return None
        
        # Get the Sales Invoice to get customer details
        sales_invoice = frappe.get_doc("Sales Invoice", booking_id)
        customer_id = sales_invoice.customer
        
        # Since we want direct cash to revenue (not through customer receivable),
        # we cannot reference the Sales Invoice as ERPNext validates party matching.
        # We'll create a simple journal entry with a descriptive remark for audit trail.
        
        journal_entry = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "company": accounts["company"],
            "posting_date": today(),
            "accounts": [
                {
                    "account": accounts["cash_account"],
                    "debit_in_account_currency": advance_amount
                },
                {
                    "account": accounts["rental_revenue"],
                    "credit_in_account_currency": advance_amount
                }
            ],
            "user_remark": f"Advance payment for rental booking {booking_id} from customer {customer_id}",
            "cheque_no": f"ADV-{booking_id}",
            "cheque_date": today()
        })
        
        journal_entry.insert()
        journal_entry.submit()
        print(f"✅ Created advance revenue entry: {journal_entry.name}")
        
        return journal_entry.name
        
    except Exception as e:
        print(f"❌ Error creating advance journal entry: {str(e)}")
        print(f"❌ Full error details: {frappe.get_traceback()}")
        frappe.log_error(f"Advance journal entry error for {booking_id}: {str(e)}")
        return None

def create_balance_payment_entry(booking_id, balance_amount, customer_id, company=None):
    """Create payment entry for balance collection against AR"""
    try:
        accounts = get_rental_accounts(company)
        balance_amount = flt(balance_amount)
        
        if balance_amount <= 0:
            return None
            
        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "party_type": "Customer",
            "party": customer_id,
            "company": accounts["company"],
            "posting_date": today(),
            "paid_amount": balance_amount,
            "received_amount": balance_amount,
            "paid_to": accounts["cash_account"],
            "reference_no": f"BAL-{booking_id}",
            "reference_date": today(),
            "references": [{
                "reference_doctype": "Sales Invoice",
                "reference_name": booking_id,
                "allocated_amount": balance_amount
            }]
        })
        
        payment_entry.insert()
        payment_entry.submit()
        print(f"✅ Created balance payment entry: {payment_entry.name}")
        return payment_entry.name
        
    except Exception as e:
        print(f"❌ Error creating balance payment entry: {str(e)}")
        frappe.log_error(f"Balance payment entry error for {booking_id}: {str(e)}")
        return None

def create_caution_deposit_journal_entry(booking_id, caution_amount, company=None):
    """Create journal entry for caution deposit collection"""
    try:
        accounts = get_rental_accounts(company)
        caution_amount = flt(caution_amount)
        
        if caution_amount <= 0:
            return None
            
        journal_entry = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "company": accounts["company"],
            "posting_date": today(),
            "accounts": [
                {
                    "account": accounts["cash_account"],
                    "debit_in_account_currency": caution_amount
                },
                {
                    "account": accounts["caution_deposit_payable"],
                    "credit_in_account_currency": caution_amount
                }
            ],
            "user_remark": f"Caution deposit collected for booking {booking_id}",
            "cheque_no": f"CAU-{booking_id}",
            "cheque_date": today()
        })
        
        journal_entry.insert()
        journal_entry.submit()
        print(f"✅ Created caution deposit entry: {journal_entry.name}")
        return journal_entry.name
        
    except Exception as e:
        print(f"❌ Error creating caution deposit entry: {str(e)}")
        frappe.log_error(f"Caution deposit entry error for {booking_id}: {str(e)}")
        return None

def create_owner_commission_journal_entry(booking_id, commission_amount, owner_id=None, company=None):
    """Create journal entry for owner commission liability"""
    try:
        accounts = get_rental_accounts(company)
        commission_amount = flt(commission_amount)
        
        if commission_amount <= 0:
            return None
            
        credit_account = {
            "account": accounts["owner_commission_payable"],
            "credit_in_account_currency": commission_amount
        }
        
        # Add party details if owner_id is provided
        if owner_id:
            # Check if owner is a Customer or Supplier
            if frappe.db.exists("Customer", owner_id):
                credit_account["party_type"] = "Customer"
                credit_account["party"] = owner_id
            elif frappe.db.exists("Supplier", owner_id):
                credit_account["party_type"] = "Supplier" 
                credit_account["party"] = owner_id
            
        journal_entry = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "company": accounts["company"],
            "posting_date": today(),
            "accounts": [
                {
                    "account": accounts["owner_commission_expense"],
                    "debit_in_account_currency": commission_amount
                },
                credit_account
            ],
            "user_remark": f"Owner commission for booking {booking_id}",
            "cheque_no": f"COM-{booking_id}",
            "cheque_date": today()
        })
        
        journal_entry.insert()
        journal_entry.submit()
        print(f"✅ Created owner commission entry: {journal_entry.name}")
        return journal_entry.name
        
    except Exception as e:
        print(f"❌ Error creating commission entry: {str(e)}")
        frappe.log_error(f"Commission entry error for {booking_id}: {str(e)}")
        return None

def create_caution_refund_journal_entry(booking_id, refund_amount, deduction_amount=0, company=None):
    """Create journal entry for caution deposit refund"""
    try:
        accounts = get_rental_accounts(company)
        refund_amount = flt(refund_amount)
        deduction_amount = flt(deduction_amount)
        total_caution = refund_amount + deduction_amount
        
        if total_caution <= 0:
            return None
            
        # Get customer details for party reference in liability account
        sales_invoice = frappe.get_doc("Sales Invoice", booking_id)
        customer_id = sales_invoice.customer
        
        journal_accounts = [
            {
                "account": accounts["caution_deposit_payable"],
                "party_type": "Customer",
                "party": customer_id,
                "debit_in_account_currency": total_caution
            }
        ]
        
        # Add cash refund if any
        if refund_amount > 0:
            journal_accounts.append({
                "account": accounts["cash_account"],
                "credit_in_account_currency": refund_amount
            })
        
        # Add damage deduction income if any
        if deduction_amount > 0:
            journal_accounts.append({
                "account": accounts["damage_deduction_income"],
                "credit_in_account_currency": deduction_amount
            })
        
        journal_entry = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "company": accounts["company"],
            "posting_date": today(),
            "accounts": journal_accounts,
            "user_remark": f"Caution deposit refund for booking {booking_id}",
            "cheque_no": f"REF-{booking_id}",
            "cheque_date": today()
        })
        
        journal_entry.insert()
        journal_entry.submit()
        print(f"✅ Created caution refund entry: {journal_entry.name}")
        return journal_entry.name
        
    except Exception as e:
        print(f"❌ Error creating refund entry: {str(e)}")
        frappe.log_error(f"Refund entry error for {booking_id}: {str(e)}")
        return None

def calculate_owner_commission(booking_items, commission_rate=0.1):
    """Calculate owner commission for third-party items"""
    total_commission = 0
    commission_details = []
    
    for item in booking_items:
        # Check if item is third-party
        item_doc = frappe.get_doc("Item", item.get("item_code"))
        if hasattr(item_doc, 'is_third_party_item') and item_doc.is_third_party_item:
            item_amount = flt(item.get("amount", 0))
            commission = item_amount * flt(commission_rate)
            total_commission += commission
            
            commission_details.append({
                "item_code": item.get("item_code"),
                "item_amount": item_amount,
                "commission_rate": commission_rate,
                "commission_amount": commission,
                "owner_id": getattr(item_doc, 'item_owner', None)
            })
    
    return total_commission, commission_details
