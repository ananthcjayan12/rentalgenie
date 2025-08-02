# ERPNext Doctype Mapping & Implementation Strategy

## 🎯 Core Philosophy: Use ERPNext, Don't Reinvent

This document maps your rental business requirements to existing ERPNext doctypes, showing how to achieve 90%+ functionality through customization rather than new doctype creation.

---

## 📊 Business Requirement → ERPNext Doctype Mapping

### 1. Store Management
| Requirement | ERPNext Doctype | Customization Needed |
|-------------|-----------------|---------------------|
| Multiple Stores | **Company** | None - use as-is |
| Store-wise P&L | **Company** + Accounting | Configure chart of accounts per company |
| Store Admin Access | **User** + **Role** | Custom role with company restrictions |

### 2. Item Management
| Requirement | ERPNext Doctype | Implementation |
|-------------|-----------------|----------------|
| Rental Items | **Item** | Add custom fields for rental rates, deposit |
| Item Images | **Item** (existing field) | Use existing attachment functionality |
| Third-party Items | **Item** + **Supplier** | Custom fields + auto-create supplier |
| Item Status Tracking | **Item** | Custom field for rental status |
| Item Approval | **Item** | Custom field + workflow |

### 3. Customer & Booking
| Requirement | ERPNext Doctype | Implementation |
|-------------|-----------------|----------------|
| Customer Details | **Customer** | Add mobile field, unique validation |
| Rental Booking | **Sales Invoice** | Custom fields for rental details |
| Booking Calendar | **Sales Invoice** | Custom report based on rental dates |
| Advance Payment | **Payment Entry** | Link to sales invoice |

### 4. Financial Management
| Requirement | ERPNext Doctype | Implementation |
|-------------|-----------------|----------------|
| Caution Deposit | **Journal Entry** | Auto-create liability entry |
| Owner Commission | **Journal Entry** | Auto-calculate and book liability |
| Rental Income | **Sales Invoice** | Use existing income booking |
| Owner Payments | **Payment Entry** | Regular supplier payments |

---

## 🛠️ Detailed Implementation Strategy

### Phase 1: Item Enhancement Strategy

#### 1.1 Extend Item Doctype (No New Doctype)
```python
# Custom fields to add to existing Item doctype
ITEM_CUSTOM_FIELDS = [
    # Rental Section
    {
        "fieldname": "rental_section",
        "label": "Rental Configuration", 
        "fieldtype": "Section Break",
        "insert_after": "image"
    },
    {
        "fieldname": "is_rental_item",
        "label": "Enable Rental",
        "fieldtype": "Check",
        "default": 0,
        "insert_after": "rental_section"
    },
    {
        "fieldname": "rental_rate_per_day", 
        "label": "Rental Rate (₹/day)",
        "fieldtype": "Currency",
        "depends_on": "is_rental_item",
        "mandatory_depends_on": "is_rental_item"
    },
    {
        "fieldname": "caution_deposit_rate",
        "label": "Caution Deposit (₹)",
        "fieldtype": "Currency", 
        "depends_on": "is_rental_item"
    },
    {
        "fieldname": "item_category_rental",
        "label": "Category",
        "fieldtype": "Select",
        "options": "\nDress\nOrnament\nAccessory",
        "depends_on": "is_rental_item"
    },
    
    # Third Party Section
    {
        "fieldname": "third_party_section",
        "label": "Third Party Owner Details",
        "fieldtype": "Section Break",
        "depends_on": "is_rental_item",
        "collapsible": 1
    },
    {
        "fieldname": "is_third_party_item", 
        "label": "Third Party Owned",
        "fieldtype": "Check",
        "depends_on": "is_rental_item"
    },
    {
        "fieldname": "owner_commission_percent",
        "label": "Owner Commission %",
        "fieldtype": "Percent",
        "depends_on": "is_third_party_item",
        "default": 30
    },
    {
        "fieldname": "third_party_supplier",
        "label": "Owner (Supplier)",
        "fieldtype": "Link",
        "options": "Supplier",
        "depends_on": "is_third_party_item"
    },
    {
        "fieldname": "owner_purchase_paid",
        "label": "Owner Payment Made",
        "fieldtype": "Check",
        "depends_on": "is_third_party_item",
        "default": 0
    },
    
    # Status Section  
    {
        "fieldname": "status_section",
        "label": "Status & Approval",
        "fieldtype": "Section Break"
    },
    {
        "fieldname": "approval_status",
        "label": "Approval Status", 
        "fieldtype": "Select",
        "options": "Pending Approval\nApproved\nRejected",
        "default": "Pending Approval",
        "read_only": 1
    },
    {
        "fieldname": "current_rental_status",
        "label": "Current Status",
        "fieldtype": "Select", 
        "options": "Available\nBooked\nOut for Rental\nUnder Dry Wash\nMaintenance",
        "default": "Available",
        "depends_on": "is_rental_item"
    }
]
```

#### 1.2 Item Automation Hooks
```python
# In hooks.py
doc_events = {
    "Item": {
        "before_save": "rental_management.automations.item_automation.before_item_save",
        "after_insert": "rental_management.automations.item_automation.after_item_insert"
    }
}

# In item_automation.py
def before_item_save(doc, method):
    """Validate rental item before saving"""
    if doc.is_rental_item:
        # Set default UOM to "Nos"
        if not doc.stock_uom:
            doc.stock_uom = "Nos"
        
        # Ensure maintain stock is enabled
        doc.is_stock_item = 1
        
        # Ensure it's not a fixed asset
        doc.is_fixed_asset = 0

def after_item_insert(doc, method):
    """Auto-create related records after item creation"""
    if doc.is_rental_item:
        # 1. Auto-create rental service item
        create_rental_service_item(doc)
        
        # 2. If third party, create/link supplier
        if doc.is_third_party_item:
            handle_third_party_supplier(doc)
            
        # 3. Create purchase entry if needed
        if doc.is_third_party_item and not doc.owner_purchase_paid:
            create_purchase_entry(doc)

def create_rental_service_item(item_doc):
    """Create corresponding service item for rental"""
    service_item = frappe.new_doc("Item")
    service_item.item_code = f"{item_doc.item_code}-RENTAL"
    service_item.item_name = f"{item_doc.item_name} - Rental Service"
    service_item.item_group = "Services" 
    service_item.is_stock_item = 0  # Service item
    service_item.include_item_in_manufacturing = 0
    service_item.insert()
    
    # Link back to original item
    item_doc.db_set("rental_service_item", service_item.name)
```

### Phase 2: Customer Enhancement

#### 2.1 Customer Doctype Enhancement
```python
CUSTOMER_CUSTOM_FIELDS = [
    {
        "fieldname": "mobile_number",
        "label": "Mobile Number", 
        "fieldtype": "Data",
        "insert_after": "customer_name",
        "reqd": 1,
        "unique": 0  # We'll handle uniqueness with naming
    },
    {
        "fieldname": "customer_unique_key",
        "label": "Unique Customer ID",
        "fieldtype": "Data",
        "read_only": 1,
        "insert_after": "mobile_number"
    }
]

# Customer automation
def before_customer_save(doc, method):
    """Generate unique customer key"""
    if not doc.customer_unique_key:
        # Create unique key: First 3 chars of name + mobile
        name_part = ''.join(doc.customer_name.split()[:2])[:6].upper()
        mobile_part = doc.mobile_number[-4:] if doc.mobile_number else "0000"
        doc.customer_unique_key = f"{name_part}{mobile_part}"
        
    # Validate uniqueness
    if frappe.db.exists("Customer", {"customer_unique_key": doc.customer_unique_key, "name": ["!=", doc.name]}):
        frappe.throw(f"Customer with mobile {doc.mobile_number} already exists")
```

### Phase 3: Booking System via Sales Invoice

#### 3.1 Sales Invoice Enhancement for Rentals
```python
SALES_INVOICE_CUSTOM_FIELDS = [
    # Rental Details Section
    {
        "fieldname": "rental_booking_section",
        "label": "Rental Booking Details",
        "fieldtype": "Section Break",
        "insert_after": "customer"
    },
    {
        "fieldname": "is_rental_booking",
        "label": "Rental Booking",
        "fieldtype": "Check",
        "insert_after": "rental_booking_section"
    },
    {
        "fieldname": "function_date",
        "label": "Function/Event Date", 
        "fieldtype": "Date",
        "depends_on": "is_rental_booking",
        "mandatory_depends_on": "is_rental_booking"
    },
    {
        "fieldname": "rental_start_date",
        "label": "Rental Start Date",
        "fieldtype": "Date", 
        "depends_on": "is_rental_booking"
    },
    {
        "fieldname": "rental_end_date", 
        "label": "Rental End Date",
        "fieldtype": "Date",
        "depends_on": "is_rental_booking"
    },
    {
        "fieldname": "rental_duration_days",
        "label": "Duration (Days)",
        "fieldtype": "Int",
        "default": 3,
        "depends_on": "is_rental_booking"
    },
    
    # Financial Section
    {
        "fieldname": "payment_details_section", 
        "label": "Payment Breakdown",
        "fieldtype": "Section Break",
        "depends_on": "is_rental_booking"
    },
    {
        "fieldname": "total_rental_amount",
        "label": "Total Rental Charges",
        "fieldtype": "Currency",
        "read_only": 1,
        "depends_on": "is_rental_booking"
    },
    {
        "fieldname": "caution_deposit_amount",
        "label": "Caution Deposit", 
        "fieldtype": "Currency",
        "depends_on": "is_rental_booking"
    },
    {
        "fieldname": "advance_received",
        "label": "Advance Received",
        "fieldtype": "Currency",
        "depends_on": "is_rental_booking"
    },
    {
        "fieldname": "balance_due_on_delivery",
        "label": "Balance Due on Delivery",
        "fieldtype": "Currency", 
        "read_only": 1,
        "depends_on": "is_rental_booking"
    },
    
    # Status Section
    {
        "fieldname": "booking_status_section",
        "label": "Booking Status", 
        "fieldtype": "Section Break",
        "depends_on": "is_rental_booking"
    },
    {
        "fieldname": "booking_status",
        "label": "Status",
        "fieldtype": "Select",
        "options": "Booked\nOut for Rental\nReturned\nExchanged",
        "default": "Booked",
        "depends_on": "is_rental_booking"
    },
    {
        "fieldname": "is_exchange_booking",
        "label": "Exchange Booking",
        "fieldtype": "Check",
        "depends_on": "is_rental_booking"
    },
    {
        "fieldname": "original_booking_ref",
        "label": "Original Booking Reference",
        "fieldtype": "Link",
        "options": "Sales Invoice", 
        "depends_on": "is_exchange_booking"
    }
]
```

#### 3.2 Booking Validation & Automation
```python
def validate_sales_invoice(doc, method):
    """Validate rental booking conflicts"""
    if doc.is_rental_booking:
        # Calculate rental dates based on function date
        if doc.function_date and doc.rental_duration_days:
            doc.rental_start_date = add_days(doc.function_date, -2)  # 2 days before function
            doc.rental_end_date = add_days(doc.function_date, doc.rental_duration_days - 2)
        
        # Check for booking conflicts
        check_item_availability(doc)
        
        # Calculate amounts
        calculate_rental_amounts(doc)

def check_item_availability(doc):
    """Check if items are available for rental period"""
    for item in doc.items:
        if is_item_booked_in_period(item.item_code, doc.rental_start_date, doc.rental_end_date):
            frappe.throw(f"Item {item.item_name} is not available for the selected dates")

def calculate_rental_amounts(doc):
    """Auto-calculate rental amounts"""
    total_rental = 0
    total_deposit = 0
    
    for item in doc.items:
        item_master = frappe.get_doc("Item", item.item_code)
        if item_master.is_rental_item:
            daily_rate = item_master.rental_rate_per_day or 0
            duration = doc.rental_duration_days or 1
            
            item.rate = daily_rate * duration
            item.amount = item.rate * item.qty
            
            total_rental += item.amount
            total_deposit += (item_master.caution_deposit_rate or 0) * item.qty
    
    doc.total_rental_amount = total_rental
    doc.caution_deposit_amount = total_deposit
    doc.balance_due_on_delivery = doc.grand_total - doc.advance_received
```

### Phase 4: Financial Integration

#### 4.1 Automatic Journal Entries
```python
def on_submit_sales_invoice(doc, method):
    """Create automatic journal entries for rental bookings"""
    if doc.is_rental_booking:
        # 1. Book caution deposit as liability
        if doc.caution_deposit_amount:
            create_caution_deposit_entry(doc)
        
        # 2. Calculate and book owner commission
        if has_third_party_items(doc):
            create_owner_commission_entries(doc)

def create_caution_deposit_entry(invoice_doc):
    """Create journal entry for caution deposit"""
    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.posting_date = invoice_doc.posting_date
    je.company = invoice_doc.company
    je.user_remark = f"Caution Deposit for Invoice {invoice_doc.name}"
    
    # Debit: Customer Account (Receivable)
    je.append("accounts", {
        "account": invoice_doc.debit_to,
        "debit_in_account_currency": invoice_doc.caution_deposit_amount,
        "party_type": "Customer",
        "party": invoice_doc.customer
    })
    
    # Credit: Caution Deposit Liability Account
    caution_deposit_account = get_caution_deposit_account(invoice_doc.company)
    je.append("accounts", {
        "account": caution_deposit_account,
        "credit_in_account_currency": invoice_doc.caution_deposit_amount
    })
    
    je.submit()

def create_owner_commission_entries(invoice_doc):
    """Create commission liability entries for third-party items"""
    for item in invoice_doc.items:
        item_master = frappe.get_doc("Item", item.item_code)
        if item_master.is_third_party_item and item_master.owner_commission_percent:
            commission_amount = item.amount * (item_master.owner_commission_percent / 100)
            
            # Create journal entry for commission liability
            je = frappe.new_doc("Journal Entry") 
            je.voucher_type = "Journal Entry"
            je.posting_date = invoice_doc.posting_date
            je.company = invoice_doc.company
            
            # Debit: Rental Income (reduce income)
            rental_income_account = get_rental_income_account(invoice_doc.company)
            je.append("accounts", {
                "account": rental_income_account,
                "debit_in_account_currency": commission_amount
            })
            
            # Credit: Owner Commission Payable
            commission_payable_account = get_commission_payable_account(invoice_doc.company)
            je.append("accounts", {
                "account": commission_payable_account, 
                "credit_in_account_currency": commission_amount,
                "party_type": "Supplier",
                "party": item_master.third_party_supplier
            })
            
            je.submit()
```

---

## 🔧 Key Implementation Files

### 1. App Structure
```
rental_management/
├── hooks.py                    # All ERPNext hooks
├── rental_management/
│   ├── custom_fields/          # Custom field definitions
│   ├── automations/            # Business logic automations  
│   ├── validations/            # Validation functions
│   ├── reports/                # Custom reports
│   └── utils/                  # Helper utilities
```

### 2. Main Hooks File
```python
# hooks.py
app_name = "rental_management"
app_title = "Rental Management"
app_publisher = "Your Company"
app_description = "Rental business management on ERPNext"
app_version = "1.0.0"

# Document Events
doc_events = {
    "Item": {
        "before_save": "rental_management.automations.item_automation.before_item_save",
        "after_insert": "rental_management.automations.item_automation.after_item_insert"
    },
    "Customer": {
        "before_save": "rental_management.automations.customer_automation.before_customer_save"
    },
    "Sales Invoice": {
        "validate": "rental_management.automations.booking_automation.validate_sales_invoice",
        "on_submit": "rental_management.automations.booking_automation.on_submit_sales_invoice"
    }
}

# Custom Fields
custom_fields = {
    "Item": [
        # Rental fields as defined above
    ],
    "Customer": [
        # Customer fields as defined above  
    ],
    "Sales Invoice": [
        # Sales Invoice fields as defined above
    ]
}

# Fixtures (Master data to be installed)
fixtures = [
    {"dt": "Custom Field", "filters": {"module": "Rental Management"}},
    {"dt": "Property Setter", "filters": {"module": "Rental Management"}},
]
```

---

## ✅ Why This Approach Works

### 1. **Leverages ERPNext Strengths**
- Full accounting integration (GL entries, P&L, Balance Sheet)
- Existing user management and permissions
- Built-in reporting and dashboard capabilities
- Mobile responsiveness

### 2. **Minimal Customization**
- No new doctypes created
- Only custom fields and business logic added
- Easy to upgrade ERPNext versions
- Maintains standard ERPNext workflows

### 3. **Business Requirements Met**
- ✅ Multi-store management (Company doctype)
- ✅ Item rental tracking (Item + custom fields)
- ✅ Booking calendar (Sales Invoice + custom fields)
- ✅ Financial tracking (Journal Entries + Payment Entries)
- ✅ Commission management (Supplier + automated calculations)
- ✅ Approval workflows (Custom fields + automations)

### 4. **Scalability & Maintenance**
- Uses ERPNext's proven architecture
- Easy to add new features
- Standard backup/restore procedures
- Community support available

This approach gives you a complete rental management system while staying true to ERPNext's architecture and your requirement of not reinventing anything!
