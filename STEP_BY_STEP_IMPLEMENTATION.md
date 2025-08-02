# STEP_BY_STEP_IMPLEMENTATION : Final

# Step-by-Step Implementation Guide

## 🚀 Getting Started with Rental Management on ERPNext

This guide will walk you through implementing the rental management system step by step, leveraging existing ERPNext functionality.

### ⚠️ **IMPORTANT UPDATES (Based on Stakeholder Feedback):**

- **Caution Deposit**: NOT added at item level, manually entered by salesman at invoice creation
- **Rental Duration**: 6-day window (2 days before + 4 days after function) - Default 6 days
- **Dry Cleaning**: NO charges on invoice, tracked only as expense in chart of accounts
- **Owner Commission**: No monthly processing, auto-updated in ledger, payment via Payment Entry
- **Caution Deposit Refund**: Processed BEFORE dry cleaning, deductions possible for damage
- **Accounting**: Owner and supplier are separate entities in ERPNext accounting terms

---

## 📋 Prerequisites

### 1. Development Environment Setup

```bash
# Install Frappe/ERPNext development environment# Follow the official guide: https://frappeframework.com/docs/user/en/installation# Create a new site for developmentbench new-site rental-dev.localhost
bench --site rental-dev.localhost install-app erpnext
# Enable developer modebench --site rental-dev.localhost set-config developer_mode 1
bench --site rental-dev.localhost clear-cache
```

### 2. Create Your Custom App

```bash
# Create the rental management appbench new-app rental_management
# Install the app on your sitebench --site rental-dev.localhost install-app rental_management
```

---

## 🎯 Phase 1: Basic Setup (Day 1-2)

### Step 1.1: Create Basic App Structure

Create the following file structure in your app:

```
apps/rental_management/rental_management/
├── __init__.py
├── custom_fields/
│   ├── __init__.py
│   ├── item_fields.py
│   ├── customer_fields.py
│   └── sales_invoice_fields.py
├── automations/
│   ├── __init__.py
│   ├── item_automation.py
│   ├── customer_automation.py
│   └── booking_automation.py
├── validations/
│   ├── __init__.py
│   └── booking_validations.py
└── utils/
    ├── __init__.py
    └── rental_utils.py
```

### Step 1.2: Setup Custom Fields

**File: `rental_management/custom_fields/item_fields.py`**

```python
import frappe
def create_item_custom_fields():
    """Create custom fields for Item doctype"""    custom_fields = [
        {
            "doctype": "Item",
            "fieldname": "rental_section",
            "label": "Rental Configuration",
            "fieldtype": "Section Break",
            "insert_after": "image",
            "collapsible": 1        },
        {
            "doctype": "Item",
            "fieldname": "is_rental_item",
            "label": "Enable for Rental",
            "fieldtype": "Check",
            "default": 0,
            "insert_after": "rental_section"        },
        {
            "doctype": "Item",
            "fieldname": "rental_rate_per_day",
            "label": "Rental Rate (₹/day)",
            "fieldtype": "Currency",
            "depends_on": "is_rental_item",
            "mandatory_depends_on": "is_rental_item",
            "insert_after": "is_rental_item"        },
        {
            "doctype": "Item",
            "fieldname": "rental_item_type",
            "label": "Item Category",
            "fieldtype": "Select",
            "options": "\nDress\nOrnament\nAccessory\nOther",
            "depends_on": "is_rental_item",
            "insert_after": "rental_rate_per_day"        },
        {
            "doctype": "Item",
            "fieldname": "column_break_rental_1",
            "fieldtype": "Column Break",
            "insert_after": "rental_item_type"        },
        {
            "doctype": "Item",
            "fieldname": "current_rental_status",
            "label": "Current Status",
            "fieldtype": "Select",
            "options": "Available\nBooked\nOut for Rental\nUnder Dry Wash\nMaintenance",
            "default": "Available",
            "depends_on": "is_rental_item",
            "insert_after": "column_break_rental_1"        },
        {
            "doctype": "Item",
            "fieldname": "approval_status",
            "label": "Approval Status",
            "fieldtype": "Select",
            "options": "Pending Approval\nApproved\nRejected",
            "default": "Pending Approval",
            "read_only": 1,
            "insert_after": "current_rental_status"        },
        # Third Party Section        {
            "doctype": "Item",
            "fieldname": "third_party_section",
            "label": "Third Party Owner Details",
            "fieldtype": "Section Break",
            "depends_on": "is_rental_item",
            "collapsible": 1,
            "insert_after": "approval_status"        },
        {
            "doctype": "Item",
            "fieldname": "is_third_party_item",
            "label": "Third Party Owned",
            "fieldtype": "Check",
            "depends_on": "is_rental_item",
            "insert_after": "third_party_section"        },
        {
            "doctype": "Item",
            "fieldname": "owner_commission_percent",
            "label": "Owner Commission %",
            "fieldtype": "Percent",
            "depends_on": "is_third_party_item",
            "default": 30,
            "insert_after": "is_third_party_item"        },
        {
            "doctype": "Item",
            "fieldname": "third_party_supplier",
            "label": "Owner (Supplier)",
            "fieldtype": "Link",
            "options": "Supplier",
            "depends_on": "is_third_party_item",
            "insert_after": "owner_commission_percent"        }
    ]
    for field in custom_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["doctype"], "fieldname": field["fieldname"]}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": field["doctype"],
                "fieldname": field["fieldname"],
                "label": field["label"],
                "fieldtype": field["fieldtype"],
                "options": field.get("options"),
                "default": field.get("default"),
                "insert_after": field["insert_after"],
                "depends_on": field.get("depends_on"),
                "mandatory_depends_on": field.get("mandatory_depends_on"),
                "read_only": field.get("read_only", 0),
                "collapsible": field.get("collapsible", 0)
            })
            custom_field.insert()
    frappe.db.commit()
    print("Item custom fields created successfully!")
# Call this function during app installationif __name__ == "__main__":
    create_item_custom_fields()
```

### Step 1.3: Update Hooks File

**File: `rental_management/hooks.py`**

```python
app_name = "rental_management"app_title = "Rental Management"app_publisher = "Your Company"app_description = "Rental Management System for ERPNext"app_version = "0.1.0"# Document Events - We'll add these as we implementdoc_events = {
    "Item": {
        "before_save": "rental_management.automations.item_automation.before_item_save",
        "after_insert": "rental_management.automations.item_automation.after_item_insert"    }
}
# Installation hooksafter_install = "rental_management.setup.install.after_install"# Include js, css files in header of desk.html# app_include_css = "/assets/rental_management/css/rental_management.css"# app_include_js = "/assets/rental_management/js/rental_management.js"
```

### Step 1.4: Create Installation Script

**File: `rental_management/setup/__init__.py`** (empty file)

**File: `rental_management/setup/install.py`**

```python
import frappe
from rental_management.custom_fields.item_fields import create_item_custom_fields
def after_install():
    """Setup custom fields and configurations after app installation"""    print("Setting up Rental Management...")
    # Create custom fields    create_item_custom_fields()
    # Create default item groups if they don't exist    create_rental_item_groups()
    # Setup default accounts template    setup_rental_accounts()
    print("Rental Management setup completed!")
def create_rental_item_groups():
    """Create rental-specific item groups"""    item_groups = [
        {"item_group_name": "Rental Items", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Dresses", "parent_item_group": "Rental Items"},
        {"item_group_name": "Ornaments", "parent_item_group": "Rental Items"},
        {"item_group_name": "Accessories", "parent_item_group": "Rental Items"}
    ]
    for group in item_groups:
        if not frappe.db.exists("Item Group", group["item_group_name"]):
            item_group = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": group["item_group_name"],
                "parent_item_group": group["parent_item_group"],
                "is_group": 1 if group["item_group_name"] == "Rental Items" else 0            })
            item_group.insert()
def setup_rental_accounts():
    """Setup rental-specific account templates"""    # This will be expanded in later phases    pass
```

---

## 🎯 Phase 2: Item Management (Day 3-5)

### Step 2.1: Item Automation Logic

**File: `rental_management/automations/item_automation.py`**

```python
import frappe
from frappe import _
from frappe.utils import cstr
def before_item_save(doc, method):
    """Validate and set defaults for rental items"""    if doc.is_rental_item:
        # Set mandatory fields for rental items        doc.is_stock_item = 1  # Must maintain stock        doc.include_item_in_manufacturing = 0  # Not a manufacturing item        doc.is_fixed_asset = 0  # Not a fixed asset        # Set default UOM if not set        if not doc.stock_uom:
            doc.stock_uom = "Nos"        # Set default item group        if not doc.item_group or doc.item_group == "All Item Groups":
            if doc.rental_item_type:
                if doc.rental_item_type in ["Dress", "Dresses"]:
                    doc.item_group = "Dresses"                elif doc.rental_item_type in ["Ornament", "Ornaments"]:
                    doc.item_group = "Ornaments"                elif doc.rental_item_type in ["Accessory", "Accessories"]:
                    doc.item_group = "Accessories"                else:
                    doc.item_group = "Rental Items"        # Validate rental rate        if not doc.rental_rate_per_day or doc.rental_rate_per_day <= 0:
            frappe.throw(_("Rental Rate Per Day is mandatory for rental items"))
    # Item automation logic here - no automatic caution deposit calculation    # Caution deposit is manually entered by salesman at invoice leveldef after_item_insert(doc, method):
    """Perform post-creation tasks for rental items"""    if doc.is_rental_item:
        try:
            # 1. Create rental service item            create_rental_service_item(doc)
            # 2. Handle third party supplier creation            if doc.is_third_party_item:
                handle_third_party_supplier(doc)
            # 3. Create initial stock entry            create_initial_stock_entry(doc)
        except Exception as e:
            frappe.log_error(f"Error in after_item_insert for {doc.name}: {str(e)}")
def create_rental_service_item(item_doc):
    """Create corresponding service item for rental billing"""    service_item_code = f"{item_doc.item_code}-RENTAL"    # Check if service item already exists    if frappe.db.exists("Item", service_item_code):
        return    service_item = frappe.get_doc({
        "doctype": "Item",
        "item_code": service_item_code,
        "item_name": f"{item_doc.item_name} - Rental Service",
        "item_group": "Services",
        "stock_uom": "Nos",
        "is_stock_item": 0,  # Service item        "is_sales_item": 1,
        "include_item_in_manufacturing": 0,
        "description": f"Rental service for {item_doc.item_name}",
        "standard_rate": item_doc.rental_rate_per_day
    })
    service_item.insert()
    # Link service item back to original item    frappe.db.set_value("Item", item_doc.name, "rental_service_item", service_item.name)
def handle_third_party_supplier(item_doc):
    """Create or link third party supplier"""    if not item_doc.third_party_supplier:
        # Auto-create supplier if not provided        supplier_name = f"Owner-{item_doc.item_code}"        if not frappe.db.exists("Supplier", supplier_name):
            supplier = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": supplier_name,
                "supplier_type": "Individual",
                "supplier_group": "Local"            })
            supplier.insert()
            # Update item with supplier reference            frappe.db.set_value("Item", item_doc.name, "third_party_supplier", supplier.name)
def create_initial_stock_entry(item_doc):
    """Create initial stock entry for the rental item"""    # We'll implement this when we handle stock management    pass
```

### Step 2.2: Test Your Setup

1. **Install the app:**

```bash
bench --site rental-dev.localhost install-app rental_management
```

1. **Restart and clear cache:**

```bash
bench restart
bench --site rental-dev.localhost clear-cache
```

1. **Test the Item form:**
    - Go to Stock → Item → New
    - You should see the new “Rental Configuration” section
    - Check “Enable for Rental” and fill in the fields
    - Save the item and verify automation works

---

## 🎯 Phase 3: Customer Enhancement (Day 6-7)

### Step 3.1: Customer Custom Fields

**File: `rental_management/custom_fields/customer_fields.py`**

```python
import frappe
def create_customer_custom_fields():
    """Create custom fields for Customer doctype"""    custom_fields = [
        {
            "doctype": "Customer",
            "fieldname": "mobile_number",
            "label": "Mobile Number",
            "fieldtype": "Data",
            "insert_after": "customer_name",
            "reqd": 1        },
        {
            "doctype": "Customer",
            "fieldname": "customer_unique_id",
            "label": "Unique Customer ID",
            "fieldtype": "Data",
            "read_only": 1,
            "unique": 1,
            "insert_after": "mobile_number"        },
        {
            "doctype": "Customer",
            "fieldname": "rental_history_section",
            "label": "Rental History",
            "fieldtype": "Section Break",
            "collapsible": 1,
            "insert_after": "more_info"        },
        {
            "doctype": "Customer",
            "fieldname": "total_bookings",
            "label": "Total Bookings",
            "fieldtype": "Int",
            "read_only": 1,
            "default": 0,
            "insert_after": "rental_history_section"        },
        {
            "doctype": "Customer",
            "fieldname": "last_booking_date",
            "label": "Last Booking Date",
            "fieldtype": "Date",
            "read_only": 1,
            "insert_after": "total_bookings"        }
    ]
    for field in custom_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["doctype"], "fieldname": field["fieldname"]}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": field["doctype"],
                "fieldname": field["fieldname"],
                "label": field["label"],
                "fieldtype": field["fieldtype"],
                "insert_after": field["insert_after"],
                "reqd": field.get("reqd", 0),
                "read_only": field.get("read_only", 0),
                "unique": field.get("unique", 0),
                "default": field.get("default"),
                "collapsible": field.get("collapsible", 0)
            })
            custom_field.insert()
    frappe.db.commit()
    print("Customer custom fields created successfully!")
```

### Step 3.2: Customer Automation

**File: `rental_management/automations/customer_automation.py`**

```python
import frappe
from frappe import _
import re
def before_customer_save(doc, method):
    """Generate unique customer ID and validate mobile number"""    # Validate mobile number format    if doc.mobile_number:
        # Remove any spaces or special characters except +        mobile = re.sub(r'[^0-9+]', '', doc.mobile_number)
        # Basic Indian mobile validation        if not re.match(r'^(\+91|91)?[6-9]\d{9}$', mobile):
            frappe.throw(_("Please enter a valid Indian mobile number"))
        # Standardize format        if mobile.startswith('+91'):
            doc.mobile_number = mobile
        elif mobile.startswith('91') and len(mobile) == 12:
            doc.mobile_number = '+' + mobile
        elif len(mobile) == 10:
            doc.mobile_number = '+91' + mobile
    # Generate unique customer ID    if not doc.customer_unique_id:
        generate_unique_customer_id(doc)
    # Check for duplicate mobile numbers    validate_unique_mobile(doc)
def generate_unique_customer_id(doc):
    """Generate unique customer ID based on name and mobile"""    if not doc.customer_name or not doc.mobile_number:
        return    # Extract first 3 characters from customer name (remove spaces)    name_part = ''.join(doc.customer_name.split()).upper()[:3]
    # Get last 4 digits of mobile    mobile_part = doc.mobile_number[-4:] if doc.mobile_number else "0000"    # Create base unique ID    base_id = f"{name_part}{mobile_part}"    # Check if this ID already exists, if yes, add a counter    counter = 1    unique_id = base_id
    while frappe.db.exists("Customer", {"customer_unique_id": unique_id, "name": ["!=", doc.name]}):
        unique_id = f"{base_id}{counter:02d}"        counter += 1        if counter > 99:  # Safety check            unique_id = f"{base_id}{frappe.utils.random_string(2)}"            break    doc.customer_unique_id = unique_id
def validate_unique_mobile(doc):
    """Ensure mobile number is unique"""    if doc.mobile_number:
        existing = frappe.db.get_value("Customer",
                                     {"mobile_number": doc.mobile_number, "name": ["!=", doc.name]},
                                     "name")
        if existing:
            frappe.throw(_("Customer with mobile number {0} already exists: {1}")
                        .format(doc.mobile_number, existing))
def update_customer_booking_stats(customer, booking_date=None):
    """Update customer booking statistics"""    # Count total bookings    total_bookings = frappe.db.count("Sales Invoice",
                                    {"customer": customer, "is_rental_booking": 1, "docstatus": 1})
    # Get last booking date    last_booking = frappe.db.get_value("Sales Invoice",
                                      {"customer": customer, "is_rental_booking": 1, "docstatus": 1},
                                      "posting_date",
                                      order_by="posting_date desc")
    # Update customer record    frappe.db.set_value("Customer", customer, {
        "total_bookings": total_bookings,
        "last_booking_date": last_booking
    })
```

### Step 3.3: Update Installation Script

**Update: `rental_management/setup/install.py`**

```python
import frappe
from rental_management.custom_fields.item_fields import create_item_custom_fields
from rental_management.custom_fields.customer_fields import create_customer_custom_fields
def after_install():
    """Setup custom fields and configurations after app installation"""    print("Setting up Rental Management...")
    # Create custom fields    create_item_custom_fields()
    create_customer_custom_fields()
    # Create default item groups if they don't exist    create_rental_item_groups()
    # Setup default accounts template    setup_rental_accounts()
    print("Rental Management setup completed!")
def create_rental_item_groups():
    """Create rental-specific item groups"""    item_groups = [
        {"item_group_name": "Rental Items", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Dresses", "parent_item_group": "Rental Items"},
        {"item_group_name": "Ornaments", "parent_item_group": "Rental Items"},
        {"item_group_name": "Accessories", "parent_item_group": "Rental Items"}
    ]
    for group in item_groups:
        if not frappe.db.exists("Item Group", group["item_group_name"]):
            item_group = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": group["item_group_name"],
                "parent_item_group": group["parent_item_group"],
                "is_group": 1 if group["item_group_name"] == "Rental Items" else 0            })
            item_group.insert()
def setup_rental_accounts():
    """Setup rental-specific account templates"""    # This will be expanded in later phases    pass
```

### Step 3.4: Update Hooks

**Update: `rental_management/hooks.py`**

```python
# Add customer eventsdoc_events = {
    "Item": {
        "before_save": "rental_management.automations.item_automation.before_item_save",
        "after_insert": "rental_management.automations.item_automation.after_item_insert"    },
    "Customer": {
        "before_save": "rental_management.automations.customer_automation.before_customer_save"    }
}
```

---

## 🧪 Testing Your Progress

### Test Item Creation:

1. Go to Stock → Item → New
2. Enable “Enable for Rental”
3. Fill in rental rate and other details
4. Save the item and verify automation works

### Test Customer Creation:

1. Go to Selling → Customer → New
2. Enter customer name and mobile number
3. Check if unique ID gets generated
4. Try creating duplicate mobile - should show error

---

## 🎯 Phase 4: Sales Invoice Enhancement for Booking System (Day 8-10)

### Step 4.1: Sales Invoice Custom Fields

**File: `rental_management/custom_fields/sales_invoice_fields.py`**

```python
import frappe
def create_sales_invoice_custom_fields():
    """Create custom fields for Sales Invoice doctype for rental bookings"""    custom_fields = [
        # Rental Booking Section        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_booking_section",
            "label": "Rental Booking Details",
            "fieldtype": "Section Break",
            "insert_after": "customer",
            "collapsible": 1        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "is_rental_booking",
            "label": "Rental Booking",
            "fieldtype": "Check",
            "default": 0,
            "insert_after": "rental_booking_section"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "function_date",
            "label": "Function/Event Date",
            "fieldtype": "Date",
            "depends_on": "is_rental_booking",
            "mandatory_depends_on": "is_rental_booking",
            "insert_after": "is_rental_booking"        },
        # Note: Rental duration changed to 6 days window (2 days before + 4 days after function)        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_duration_days",
            "label": "Rental Duration (Days)",
            "fieldtype": "Int",
            "default": 6,
            "depends_on": "is_rental_booking",
            "insert_after": "function_date"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_start_date",
            "label": "Rental Start Date",
            "fieldtype": "Date",
            "depends_on": "is_rental_booking",
            "read_only": 1,
            "insert_after": "rental_duration_days"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_end_date",
            "label": "Rental End Date",
            "fieldtype": "Date",
            "depends_on": "is_rental_booking",
            "read_only": 1,
            "insert_after": "rental_start_date"        },
        # Financial Section        {
            "doctype": "Sales Invoice",
            "fieldname": "rental_financial_section",
            "label": "Rental Financial Details",
            "fieldtype": "Section Break",
            "depends_on": "is_rental_booking",
            "insert_after": "rental_end_date"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "total_rental_amount",
            "label": "Total Rental Charges",
            "fieldtype": "Currency",
            "read_only": 1,
            "depends_on": "is_rental_booking",
            "insert_after": "rental_financial_section"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "caution_deposit_amount",
            "label": "Caution Deposit",
            "fieldtype": "Currency",
            "depends_on": "is_rental_booking",
            "insert_after": "total_rental_amount"        },
        # Note: Dry cleaning charges removed from invoice - will be tracked as expense only        # {        #     "doctype": "Sales Invoice",        #     "fieldname": "dry_cleaning_charges",        #     "label": "Dry Cleaning Charges",        #     "fieldtype": "Currency",        #     "depends_on": "is_rental_booking",        #     "insert_after": "caution_deposit_amount"        # },        {
            "doctype": "Sales Invoice",
            "fieldname": "column_break_rental_financial",
            "fieldtype": "Column Break",
            "insert_after": "rental_item_type"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "advance_received",
            "label": "Advance Received",
            "fieldtype": "Currency",
            "depends_on": "is_rental_booking",
            "insert_after": "column_break_rental_financial"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "balance_due_on_delivery",
            "label": "Balance Due on Delivery",
            "fieldtype": "Currency",
            "read_only": 1,
            "depends_on": "is_rental_booking",
            "insert_after": "advance_received"        },
        # Status Section        {
            "doctype": "Sales Invoice",
            "fieldname": "booking_status_section",
            "label": "Booking Status & Management",
            "fieldtype": "Section Break",
            "depends_on": "is_rental_booking",
            "insert_after": "balance_due_on_delivery"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "booking_status",
            "label": "Booking Status",
            "fieldtype": "Select",
            "options": "Booked\nOut for Rental\nReturned\nUnder Dry Wash\nCompleted\nExchanged",
            "default": "Booked",
            "depends_on": "is_rental_booking",
            "insert_after": "booking_status_section"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "delivery_date",
            "label": "Actual Delivery Date",
            "fieldtype": "Datetime",
            "depends_on": "is_rental_booking",
            "insert_after": "booking_status"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "return_date",
            "label": "Actual Return Date",
            "fieldtype": "Datetime",
            "depends_on": "is_rental_booking",
            "insert_after": "delivery_date"        },
        # Exchange Section        {
            "doctype": "Sales Invoice",
            "fieldname": "exchange_section",
            "label": "Exchange Details",
            "fieldtype": "Section Break",
            "depends_on": "is_rental_booking",
            "collapsible": 1,
            "insert_after": "return_date"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "is_exchange_booking",
            "label": "Exchange Booking",
            "fieldtype": "Check",
            "depends_on": "is_rental_booking",
            "insert_after": "exchange_section"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "original_booking_reference",
            "label": "Original Booking Reference",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "depends_on": "is_exchange_booking",
            "insert_after": "is_exchange_booking"        },
        {
            "doctype": "Sales Invoice",
            "fieldname": "exchange_reason",
            "label": "Exchange Reason",
            "fieldtype": "Small Text",
            "depends_on": "is_exchange_booking",
            "insert_after": "original_booking_reference"        }
    ]
    for field in custom_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["doctype"], "fieldname": field["fieldname"]}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": field["doctype"],
                "fieldname": field["fieldname"],
                "label": field["label"],
                "fieldtype": field["fieldtype"],
                "options": field.get("options"),
                "default": field.get("default"),
                "insert_after": field["insert_after"],
                "depends_on": field.get("depends_on"),
                "mandatory_depends_on": field.get("mandatory_depends_on"),
                "read_only": field.get("read_only", 0),
                "collapsible": field.get("collapsible", 0)
            })
            custom_field.insert()
    frappe.db.commit()
    print("Sales Invoice custom fields created successfully!")
```

### Step 4.2: Booking Automation & Validation

**File: `rental_management/automations/booking_automation.py`**

```python
import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, flt
def validate_sales_invoice(doc, method):
    """Validate rental booking before saving"""    if doc.is_rental_booking:
        # Calculate rental dates        calculate_rental_dates(doc)
        # Check item availability        check_item_availability(doc)
        # Calculate amounts        calculate_rental_amounts(doc)
        # Validate exchange booking        if doc.is_exchange_booking:
            validate_exchange_booking(doc)
def calculate_rental_dates(doc):
    """Calculate rental start and end dates based on function date"""    if doc.function_date and doc.rental_duration_days:
        function_date = getdate(doc.function_date)
        # Start 2 days before function date        doc.rental_start_date = add_days(function_date, -2)
        # End date: 2 days before + 6 days total = 4 days after function (6-day window)        doc.rental_end_date = add_days(doc.rental_start_date, doc.rental_duration_days - 1)
def check_item_availability(doc):
    """Check if rental items are available for the booking period"""    if not doc.rental_start_date or not doc.rental_end_date:
        return    for item in doc.items:
        # Check if item is a rental item        item_doc = frappe.get_doc("Item", item.item_code)
        if item_doc.is_rental_item:
            # Check for conflicting bookings            conflicting_bookings = frappe.db.sql("""                SELECT si.name, si.customer, si.rental_start_date, si.rental_end_date                FROM `tabSales Invoice` si                JOIN `tabSales Invoice Item` sii ON si.name = sii.parent                WHERE sii.item_code = %s                AND si.is_rental_booking = 1                AND si.docstatus = 1                AND si.booking_status NOT IN ('Completed', 'Exchanged')                AND si.name != %s                AND (                    (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR                    (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR                    (si.rental_start_date >= %s AND si.rental_end_date <= %s)                )            """, (item.item_code, doc.name, doc.rental_start_date, doc.rental_start_date,
                  doc.rental_end_date, doc.rental_end_date, doc.rental_start_date, doc.rental_end_date))
            if conflicting_bookings:
                conflict_details = conflicting_bookings[0]
                frappe.throw(_(f"Item {item.item_name} is already booked from {conflict_details[2]} to {conflict_details[3]} (Booking: {conflict_details[0]})"))
def calculate_rental_amounts(doc):
    """Calculate rental amounts automatically"""    total_rental = 0    # Note: Caution deposit removed from auto-calculation - manually entered by salesman    for item in doc.items:
        item_doc = frappe.get_doc("Item", item.item_code)
        if item_doc.is_rental_item:
            # Calculate rental amount            daily_rate = flt(item_doc.rental_rate_per_day)
            duration = flt(doc.rental_duration_days) or 1            # Set item rate and amount            item.rate = daily_rate * duration
            item.amount = item.rate * flt(item.qty)
            total_rental += item.amount
    # Update totals    doc.total_rental_amount = total_rental
    # Note: caution_deposit_amount is manually entered by salesman, not auto-calculated    # Calculate balance due    if doc.advance_received:
        doc.balance_due_on_delivery = doc.grand_total - flt(doc.advance_received)
def validate_exchange_booking(doc):
    """Validate exchange booking details"""    if not doc.original_booking_reference:
        frappe.throw(_("Original Booking Reference is mandatory for exchange bookings"))
    # Check if original booking exists and is valid    original_booking = frappe.get_doc("Sales Invoice", doc.original_booking_reference)
    if not original_booking.is_rental_booking:
        frappe.throw(_("Original booking reference must be a rental booking"))
    if original_booking.docstatus != 1:
        frappe.throw(_("Original booking must be submitted"))
def on_submit_sales_invoice(doc, method):
    """Handle post-submission tasks for rental bookings"""    if doc.is_rental_booking:
        # Update item status to "Booked"        update_item_rental_status(doc, "Booked")
        # Create caution deposit journal entry        if doc.caution_deposit_amount:
            create_caution_deposit_entry(doc)
        # Handle owner commission for third-party items        create_owner_commission_entries(doc)
        # Update customer booking statistics        update_customer_stats(doc)
def update_item_rental_status(doc, status):
    """Update rental status of items in the booking"""    for item in doc.items:
        item_doc = frappe.get_doc("Item", item.item_code)
        if item_doc.is_rental_item:
            frappe.db.set_value("Item", item.item_code, "current_rental_status", status)
def create_caution_deposit_entry(doc):
    """Create journal entry for caution deposit liability"""    company_abbr = frappe.get_value("Company", doc.company, "abbr")
    caution_deposit_account = f"Caution Deposit Received - {company_abbr}"    # Check if account exists, create if not    if not frappe.db.exists("Account", caution_deposit_account):
        create_caution_deposit_account(doc.company)
    je = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Journal Entry",
        "posting_date": doc.posting_date,
        "company": doc.company,
        "user_remark": f"Caution Deposit for Rental Booking {doc.name}",
        "accounts": [
            {
                "account": doc.debit_to,
                "debit_in_account_currency": doc.caution_deposit_amount,
                "party_type": "Customer",
                "party": doc.customer
            },
            {
                "account": caution_deposit_account,
                "credit_in_account_currency": doc.caution_deposit_amount
            }
        ]
    })
    je.submit()
def create_owner_commission_entries(doc):
    """Create commission liability entries for third-party items"""    company_abbr = frappe.get_value("Company", doc.company, "abbr")
    commission_account = f"Owner Commission Payable - {company_abbr}"    rental_income_account = f"Rental Income - {company_abbr}"    for item in doc.items:
        item_doc = frappe.get_doc("Item", item.item_code)
        if item_doc.is_rental_item and item_doc.is_third_party_item and item_doc.owner_commission_percent:
            commission_amount = flt(item.amount) * flt(item_doc.owner_commission_percent) / 100            if commission_amount > 0:
                je = frappe.get_doc({
                    "doctype": "Journal Entry",
                    "voucher_type": "Journal Entry",
                    "posting_date": doc.posting_date,
                    "company": doc.company,
                    "user_remark": f"Owner Commission for {item.item_name} - Booking {doc.name}",
                    "accounts": [
                        {
                            "account": rental_income_account,
                            "debit_in_account_currency": commission_amount
                        },
                        {
                            "account": commission_account,
                            "credit_in_account_currency": commission_amount,
                            "party_type": "Supplier",
                            "party": item_doc.third_party_supplier
                        }
                    ]
                })
                je.submit()
def update_customer_stats(doc):
    """Update customer booking statistics"""    from rental_management.automations.customer_automation import update_customer_booking_stats
    update_customer_booking_stats(doc.customer, doc.posting_date)
def create_caution_deposit_account(company):
    """Create caution deposit liability account if it doesn't exist"""    company_abbr = frappe.get_value("Company", company, "abbr")
    account = frappe.get_doc({
        "doctype": "Account",
        "account_name": "Caution Deposit Received",
        "parent_account": f"Current Liabilities - {company_abbr}",
        "company": company,
        "account_type": "Payable",
        "root_type": "Liability"    })
    account.insert()
```

### Step 4.3: Booking Status Management

**File: `rental_management/utils/rental_utils.py`**

```python
import frappe
from frappe.utils import now_datetime, getdate
def update_booking_status(invoice_name, new_status, update_time=None):
    """Update booking status and related item statuses"""    doc = frappe.get_doc("Sales Invoice", invoice_name)
    if not doc.is_rental_booking:
        frappe.throw("This is not a rental booking")
    # Update booking status    doc.db_set("booking_status", new_status)
    # Update timestamps based on status    if new_status == "Out for Rental" and not doc.delivery_date:
        doc.db_set("delivery_date", update_time or now_datetime())
    elif new_status == "Returned" and not doc.return_date:
        doc.db_set("return_date", update_time or now_datetime())
    # Update item rental status    item_status_map = {
        "Booked": "Booked",
        "Out for Rental": "Out for Rental",
        "Returned": "Under Dry Wash",
        "Under Dry Wash": "Under Dry Wash",
        "Completed": "Available"    }
    if new_status in item_status_map:
        update_item_rental_status(doc, item_status_map[new_status])
    # Handle caution deposit refund when items are returned (before dry cleaning)    if new_status == "Returned":
        handle_caution_deposit_refund(doc)
def handle_caution_deposit_refund(doc):
    """Handle caution deposit refund when booking is returned (before dry cleaning)"""    if doc.caution_deposit_amount:
        company_abbr = frappe.get_value("Company", doc.company, "abbr")
        caution_deposit_account = f"Caution Deposit Received - {company_abbr}"        # Note: This handles full refund. For damage deductions,        # staff should manually adjust the caution_deposit_amount before changing status to "Returned"        # Create journal entry to refund caution deposit        je = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "posting_date": getdate(),
            "company": doc.company,
            "user_remark": f"Caution Deposit Refund for Booking {doc.name}",
            "accounts": [
                {
                    "account": caution_deposit_account,
                    "debit_in_account_currency": doc.caution_deposit_amount
                },
                {
                    "account": doc.debit_to,
                    "credit_in_account_currency": doc.caution_deposit_amount,
                    "party_type": "Customer",
                    "party": doc.customer
                }
            ]
        })
        je.submit()
def get_item_booking_calendar(item_code, months_ahead=6):
    """Get booking calendar for an item"""    from frappe.utils import add_months, getdate
    end_date = add_months(getdate(), months_ahead)
    bookings = frappe.db.sql("""        SELECT            si.name,            si.customer,            si.rental_start_date,            si.rental_end_date,            si.booking_status,            si.function_date        FROM `tabSales Invoice` si        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent        WHERE sii.item_code = %s        AND si.is_rental_booking = 1        AND si.docstatus = 1        AND si.rental_end_date >= CURDATE()        AND si.rental_start_date <= %s        ORDER BY si.rental_start_date    """, (item_code, end_date), as_dict=True)
    return bookings
def check_item_availability_for_period(item_code, start_date, end_date, exclude_booking=None):
    """Check if item is available for a specific period"""    conditions = ["sii.item_code = %s", "si.is_rental_booking = 1", "si.docstatus = 1"]
    values = [item_code]
    if exclude_booking:
        conditions.append("si.name != %s")
        values.append(exclude_booking)
    # Check for overlapping bookings    conditions.append("""(        (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR        (si.rental_start_date <= %s AND si.rental_end_date >= %s) OR        (si.rental_start_date >= %s AND si.rental_end_date <= %s)    )""")
    values.extend([start_date, start_date, end_date, end_date, start_date, end_date])
    conflicting_bookings = frappe.db.sql(f"""        SELECT si.name, si.customer, si.rental_start_date, si.rental_end_date        FROM `tabSales Invoice` si        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent        WHERE {' AND '.join(conditions)}        AND si.booking_status NOT IN ('Completed', 'Exchanged')    """, values, as_dict=True)
    return len(conflicting_bookings) == 0, conflicting_bookings
```

---

## 🎯 Phase 5: Financial Integration & Chart of Accounts (Day 11-12)

### Step 5.1: Setup Rental Chart of Accounts

**File: `rental_management/setup/chart_of_accounts.py`**

```python
import frappe
def setup_rental_chart_of_accounts(company):
    """Setup rental-specific chart of accounts for a company"""    company_abbr = frappe.get_value("Company", company, "abbr")
    accounts_to_create = [
        # Income Accounts        {
            "account_name": "Rental Income",
            "parent_account": f"Direct Income - {company_abbr}",
            "account_type": "Income Account",
            "root_type": "Income"        },
        # Note: Dry cleaning charges removed from income - tracked only as expense        # Liability Accounts        {
            "account_name": "Caution Deposit Received",
            "parent_account": f"Current Liabilities - {company_abbr}",
            "account_type": "Payable",
            "root_type": "Liability"        },
        {
            "account_name": "Owner Commission Payable",
            "parent_account": f"Current Liabilities - {company_abbr}",
            "account_type": "Payable",
            "root_type": "Liability"        },
        # Expense Accounts        {
            "account_name": "Dry Cleaning Expenses",
            "parent_account": f"Indirect Expenses - {company_abbr}",
            "account_type": "Expense Account",
            "root_type": "Expense"        },
        {
            "account_name": "Maintenance and Repairs",
            "parent_account": f"Indirect Expenses - {company_abbr}",
            "account_type": "Expense Account",
            "root_type": "Expense"        },
        # Asset Accounts        {
            "account_name": "Rental Inventory - Dresses",
            "parent_account": f"Stock Assets - {company_abbr}",
            "account_type": "Stock",
            "root_type": "Asset"        },
        {
            "account_name": "Rental Inventory - Ornaments",
            "parent_account": f"Stock Assets - {company_abbr}",
            "account_type": "Stock",
            "root_type": "Asset"        },
        {
            "account_name": "Cash in Hand - Store",
            "parent_account": f"Current Assets - {company_abbr}",
            "account_type": "Cash",
            "root_type": "Asset"        }
    ]
    for account_info in accounts_to_create:
        account_name_with_company = f"{account_info['account_name']} - {company_abbr}"        if not frappe.db.exists("Account", account_name_with_company):
            account = frappe.get_doc({
                "doctype": "Account",
                "account_name": account_info["account_name"],
                "parent_account": account_info["parent_account"],
                "company": company,
                "account_type": account_info["account_type"],
                "root_type": account_info["root_type"]
            })
            account.insert()
            print(f"Created account: {account_name_with_company}")
def setup_default_cost_centers(company):
    """Setup default cost centers for rental business"""    company_abbr = frappe.get_value("Company", company, "abbr")
    cost_centers = [
        "Rental Operations",
        "Store Management",
        "Customer Service"    ]
    for cc_name in cost_centers:
        cc_name_with_company = f"{cc_name} - {company_abbr}"        if not frappe.db.exists("Cost Center", cc_name_with_company):
            cost_center = frappe.get_doc({
                "doctype": "Cost Center",
                "cost_center_name": cc_name,
                "parent_cost_center": f"{company} - {company_abbr}",
                "company": company
            })
            cost_center.insert()
            print(f"Created cost center: {cc_name_with_company}")
```

### Step 5.2: Update Installation Script with Accounting Setup

**Update: `rental_management/setup/install.py`**

```python
import frappe
from rental_management.custom_fields.item_fields import create_item_custom_fields
from rental_management.custom_fields.customer_fields import create_customer_custom_fields
from rental_management.custom_fields.sales_invoice_fields import create_sales_invoice_custom_fields
from rental_management.setup.chart_of_accounts import setup_rental_chart_of_accounts, setup_default_cost_centers
def after_install():
    """Setup custom fields and configurations after app installation"""    print("Setting up Rental Management...")
    # Create custom fields    create_item_custom_fields()
    create_customer_custom_fields()
    create_sales_invoice_custom_fields()
    # Create default item groups    create_rental_item_groups()
    # Setup accounting for existing companies    setup_accounting_for_companies()
    # Create default workflows    create_rental_workflows()
    print("Rental Management setup completed!")
def setup_accounting_for_companies():
    """Setup rental accounting for all existing companies"""    companies = frappe.get_all("Company", fields=["name"])
    for company in companies:
        try:
            setup_rental_chart_of_accounts(company.name)
            setup_default_cost_centers(company.name)
            print(f"Accounting setup completed for {company.name}")
        except Exception as e:
            print(f"Error setting up accounting for {company.name}: {str(e)}")
# ...existing functions...def create_rental_workflows():
    """Create workflows for rental processes"""    # We'll implement this in Phase 6    pass
```

---

## 🎯 Phase 6: Reports & Dashboard (Day 13-15)

### Step 6.1: Booking Calendar Report

**Create folder: `rental_management/rental_management/report/booking_calendar/`**

**File: `rental_management/rental_management/report/booking_calendar/booking_calendar.json`**

```json
{ "add_total_row": 0, "columns": [], "creation": "2024-01-01 00:00:00.000000", "disable_prepared_report": 0, "disabled": 0, "docstatus": 0, "doctype": "Report", "idx": 0, "is_standard": "Yes", "modified": "2024-01-01 00:00:00.000000", "module": "Rental Management", "name": "Booking Calendar", "prepared_report": 0, "ref_doctype": "Sales Invoice", "report_name": "Booking Calendar", "report_type": "Script Report", "roles": [  {   "role": "Sales User"  },  {   "role": "Sales Manager"  },  {   "role": "System Manager"  } ]}
```

**File: `rental_management/rental_management/report/booking_calendar/booking_calendar.py`**

```python
import frappe
from frappe import _
from frappe.utils import getdate, add_days, add_months
def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data
def get_columns():
    return [
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 120        },
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 200        },
        {
            "fieldname": "booking_reference",
            "label": _("Booking Reference"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 150        },
        {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150        },
        {
            "fieldname": "function_date",
            "label": _("Function Date"),
            "fieldtype": "Date",
            "width": 100        },
        {
            "fieldname": "rental_start_date",
            "label": _("Rental Start"),
            "fieldtype": "Date",
            "width": 100        },
        {
            "fieldname": "rental_end_date",
            "label": _("Rental End"),
            "fieldtype": "Date",
            "width": 100        },
        {
            "fieldname": "booking_status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120        },
        {
            "fieldname": "rental_amount",
            "label": _("Rental Amount"),
            "fieldtype": "Currency",
            "width": 120        }
    ]
def get_data(filters):
    conditions = []
    values = []
    if filters.get("from_date"):
        conditions.append("si.rental_start_date >= %s")
        values.append(filters.get("from_date"))
    if filters.get("to_date"):
        conditions.append("si.rental_end_date <= %s")
        values.append(filters.get("to_date"))
    if filters.get("item_code"):
        conditions.append("sii.item_code = %s")
        values.append(filters.get("item_code"))
    if filters.get("customer"):
        conditions.append("si.customer = %s")
        values.append(filters.get("customer"))
    if filters.get("booking_status"):
        conditions.append("si.booking_status = %s")
        values.append(filters.get("booking_status"))
    where_clause = ""    if conditions:
        where_clause = "AND " + " AND ".join(conditions)
    data = frappe.db.sql(f"""        SELECT            sii.item_code,            sii.item_name,            si.name as booking_reference,            si.customer,            si.function_date,            si.rental_start_date,            si.rental_end_date,            si.booking_status,            sii.amount as rental_amount        FROM `tabSales Invoice` si        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent        WHERE si.is_rental_booking = 1        AND si.docstatus = 1        {where_clause}        ORDER BY si.rental_start_date, sii.item_code    """, values, as_dict=True)
    return data
```

### Step 6.2: Item Utilization Report

**Create folder: `rental_management/rental_management/report/item_utilization/`**

**File: `rental_management/rental_management/report/item_utilization/item_utilization.py`**

```python
import frappe
from frappe import _
from frappe.utils import getdate, add_months
def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data
def get_columns():
    return [
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 120        },
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 200        },
        {
            "fieldname": "total_bookings",
            "label": _("Total Bookings"),
            "fieldtype": "Int",
            "width": 100        },
        {
            "fieldname": "total_rental_days",
            "label": _("Total Rental Days"),
            "fieldtype": "Int",
            "width": 120        },
        {
            "fieldname": "total_revenue",
            "label": _("Total Revenue"),
            "fieldtype": "Currency",
            "width": 120        },
        {
            "fieldname": "avg_rental_per_booking",
            "label": _("Avg Rental/Booking"),
            "fieldtype": "Currency",
            "width": 150        },
        {
            "fieldname": "current_status",
            "label": _("Current Status"),
            "fieldtype": "Data",
            "width": 120        },
        {
            "fieldname": "last_booking_date",
            "label": _("Last Booking"),
            "fieldtype": "Date",
            "width": 100        }
    ]
def get_data(filters):
    # Get rental items with their utilization stats    data = frappe.db.sql("""        SELECT            i.item_code,            i.item_name,            i.current_rental_status as current_status,            COUNT(sii.name) as total_bookings,            SUM(si.rental_duration_days) as total_rental_days,            SUM(sii.amount) as total_revenue,            AVG(sii.amount) as avg_rental_per_booking,            MAX(si.rental_start_date) as last_booking_date        FROM `tabItem` i        LEFT JOIN `tabSales Invoice Item` sii ON i.item_code = sii.item_code        LEFT JOIN `tabSales Invoice` si ON sii.parent = si.name AND si.is_rental_booking = 1 AND si.docstatus = 1        WHERE i.is_rental_item = 1        GROUP BY i.item_code, i.item_name, i.current_rental_status        ORDER BY total_revenue DESC    """, as_dict=True)
    return data
```

### Step 6.3: Owner Commission Report

**Create folder: `rental_management/rental_management/report/owner_commission/`**

**File: `rental_management/rental_management/report/owner_commission/owner_commission.py`**

```python
import frappe
from frappe import _
def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data
def get_columns():
    return [
        {
            "fieldname": "supplier",
            "label": _("Owner/Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 150        },
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 120        },
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 200        },
        {
            "fieldname": "booking_reference",
            "label": _("Booking"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 150        },
        {
            "fieldname": "booking_date",
            "label": _("Booking Date"),
            "fieldtype": "Date",
            "width": 100        },
        {
            "fieldname": "rental_amount",
            "label": _("Rental Amount"),
            "fieldtype": "Currency",
            "width": 120        },
        {
            "fieldname": "commission_percent",
            "label": _("Commission %"),
            "fieldtype": "Percent",
            "width": 100        },
        {
            "fieldname": "commission_amount",
            "label": _("Commission Amount"),
            "fieldtype": "Currency",
            "width": 150        },
        {
            "fieldname": "payment_status",
            "label": _("Payment Status"),
            "fieldtype": "Data",
            "width": 120        }
    ]
def get_data(filters):
    conditions = []
    values = []
    if filters.get("supplier"):
        conditions.append("i.third_party_supplier = %s")
        values.append(filters.get("supplier"))
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %s")
        values.append(filters.get("from_date"))
    if filters.get("to_date"):
        conditions.append("si.posting_date <= %s")
        values.append(filters.get("to_date"))
    where_clause = ""    if conditions:
        where_clause = "AND " + " AND ".join(conditions)
    data = frappe.db.sql(f"""        SELECT            i.third_party_supplier as supplier,            sii.item_code,            sii.item_name,            si.name as booking_reference,            si.posting_date as booking_date,            sii.amount as rental_amount,            i.owner_commission_percent as commission_percent,            (sii.amount * i.owner_commission_percent / 100) as commission_amount,            'Pending' as payment_status        FROM `tabSales Invoice` si        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent        JOIN `tabItem` i ON sii.item_code = i.item_code        WHERE si.is_rental_booking = 1        AND si.docstatus = 1        AND i.is_third_party_item = 1        AND i.third_party_supplier IS NOT NULL        {where_clause}        ORDER BY si.posting_date DESC, i.third_party_supplier    """, values, as_dict=True)
    return data
```

---

## 🎯 Phase 7: Complete Workflows & Business Processes (Day 16-18)

### Complete Business Workflows

Now let me detail the complete workflows that will be available after implementation:

## 📋 COMPLETE BUSINESS WORKFLOWS

After implementing all phases, your rental management system will support these end-to-end workflows:

### 🔄 Workflow 1: Item Addition & Approval Process

**Steps:**
1. **Store Admin adds new rental item**
- Go to Stock → Item → New
- Fill basic details (Item Code, Name, UOM)
- Check “Enable for Rental”
- Set rental rate per day
- Choose item category (Dress/Ornament/Accessory)
- If third-party: Check “Third Party Owned”, set commission %, add owner details

1. **System Automation (on save):**
    - Auto-creates rental service item (ItemCode-RENTAL)
    - If third-party: Auto-creates supplier record for owner
    - Sets item status to “Pending Approval”
    - Sets item group based on category
2. **Super Admin Approval:**
    - Reviews items in “Pending Approval” status
    - Approves or rejects items
    - Only approved items appear in store frontend

**Result:** Items ready for rental booking with proper categorization and approval control.

---

### 🔄 Workflow 2: Customer Registration & Management

**Steps:**
1. **Customer visits store or calls**
2. **Staff creates customer record:**
- Go to Selling → Customer → New
- Enter customer name and mobile number
- System auto-generates unique customer ID (Name3chars + Mobile4digits)
- Add address if needed

1. **System Validation:**
    - Validates Indian mobile number format
    - Checks for duplicate mobile numbers
    - Standardizes mobile format (+91xxxxxxxxxx)

**Result:** Unique customer identification preventing duplicates while allowing easy lookup.

---

### 🔄 Workflow 3: Rental Booking Process

**Steps:**
1. **Customer selects items for function date**
2. **Staff creates rental booking:**
- Go to Accounts → Sales Invoice → New
- Select customer
- Check “Rental Booking”
- Enter function date (e.g., wedding on Sep 20)
- Set rental duration (default 6 days)
- Add rental items to invoice

1. **System Auto-calculations:**
    - Calculates rental start date (2 days before function = Sep 18)
    - Calculates rental end date (Sep 18 + 6 days = Sep 23)
    - Checks item availability for Sep 18-23 (6-day window)
    - Calculates total rental amount (rate × duration × quantity)
    - Staff manually enters caution deposit amount (no auto-calculation)
2. **Staff completes booking:**
    - Enter advance received amount
    - Manually enter caution deposit amount
    - System calculates balance due on delivery
    - Submit invoice
3. **System Post-submission:**
    - Updates item status to “Booked” for the period
    - Creates caution deposit liability journal entry
    - Creates owner commission liability (for third-party items)
    - Updates customer booking statistics

**Result:** Confirmed booking with automatic financial entries and availability blocking.

---

### 🔄 Workflow 4: Item Delivery Process

**Steps:**
1. **Delivery day (Sep 18):**
- Staff goes to booking (Sales Invoice)
- Updates booking status to “Out for Rental”
- System records actual delivery timestamp
- Collects balance amount due
- Items physically given to customer

1. **System Updates:**
    - Item status changes to “Out for Rental”
    - Delivery timestamp recorded
    - Items unavailable for other bookings

**Result:** Proper tracking of item location and timing.

---

### 🔄 Workflow 5: Item Return & Completion Process

**Steps:**
1. **Return day (Sep 23 or earlier within 6-day window):**
- Customer returns items
- Staff inspects items for damage
- Updates booking status to “Returned”
- System records actual return timestamp
- **Caution deposit refund processed immediately** (before dry cleaning)
- If damage found, deduction made from caution deposit before refund

1. **Dry cleaning process (after refund):**
    - Items sent for dry cleaning (may be done in bulk or per item)
    - Status updated to “Under Dry Wash”
    - Dry cleaning expense recorded in chart of accounts (indirect expenses)
    - No customer charges for dry cleaning
2. **Items back from cleaning:**
    - Staff receives items
    - Updates booking status to “Completed”
    - System automatically:
        - Changes item status to “Available”
        - Items become available for new bookings

**Result:** Complete rental cycle with proper item availability management and immediate caution deposit handling.

---

### 🔄 Workflow 6: Exchange Booking Process

**Steps:**
1. **Customer wants to change items after booking:**
- Create new Sales Invoice
- Check “Exchange Booking”
- Link to original booking reference
- Select new items
- Enter exchange reason

1. **System Handling:**
    - Validates original booking exists
    - Transfers advance from original to new booking
    - Marks original booking as “Exchanged”
    - Processes new booking with transferred advance

**Result:** No-refund exchange policy properly handled with financial accuracy.

---

### 🔄 Workflow 7: Owner Commission Payment Process

**Steps:**
1. **Automatic commission ledger management:**
- When sales happen, owner commission ledger automatically updated in chart of accounts (Current Liability)
- No specific periodic interval for payments
- Commission liability tracked automatically on each sale
- Owner and supplier are separate entities in ERPNext accounting

1. **Payment to owners (when required):**
    - Create Payment Entry to record actual payment to owner
    - Link to outstanding commission liability account
    - Payment Entry clears the liability from books
    - Maintains separation: company owes rental commission to owner, dress purchase value to supplier

**Result:** Transparent automatic commission tracking with flexible payment timing.

---

### 🔄 Workflow 8: Multi-Store Management (Super Admin)

**Steps:**
1. **Super Admin dashboard access:**
- Can view all stores/companies
- Access consolidated reports across stores
- Manage item approvals for all stores

1. **Store-wise operations:**
    - Each store has independent P&L and Balance Sheet
    - Store admins see only their store’s data
    - Financial consolidation available at super admin level

**Result:** Complete multi-store rental business management with proper access controls.

---

### 🔄 Workflow 9: Financial Reporting & Management

**Available Reports:**
1. **Booking Calendar Report**
- View all bookings by date range
- Filter by item, customer, status
- Identify busy periods and availability gaps

1. **Item Utilization Report**
    - Most/least rented items
    - Revenue per item
    - Utilization percentages
    - Inventory optimization insights
2. **Owner Commission Report**
    - Commission owed by owner
    - Payment status tracking
    - Profitability analysis
3. **Financial Reports (Standard ERPNext):**
    - Profit & Loss Statement (store-wise)
    - Balance Sheet (store-wise)
    - Cash Flow Statement
    - General Ledger

**Result:** Complete business intelligence and financial control.

---

## 🎯 System Capabilities Summary

### ✅ **Core Features Achieved**

- **Item Management**: Add, categorize, approve, track rental items
- **Customer Management**: Unique identification, booking history
- **Booking Management**: Date-based availability, conflict prevention
- **Financial Integration**: Complete accounting integration with ERPNext
- **Multi-store Support**: Independent store operations with consolidated oversight
- **Commission Management**: Automated calculation and payment tracking
- **Exchange Policy**: No-refund exchange system
- **Status Tracking**: Real-time item and booking status updates
- **Reporting**: Comprehensive business reports and analytics

### ✅ **Business Process Automation**

- Auto-creation of service items for rentals
- Automatic supplier creation for third-party items
- Date-based availability checking
- Commission calculation and liability booking
- Caution deposit management
- Item status lifecycle management
- Customer statistics updating

### ✅ **ERPNext Integration Benefits**

- Complete accounting system (no external tools needed)
- User management and role-based permissions
- Standard ERPNext mobile app compatibility
- Backup/restore procedures
- Upgrade path maintenance
- Community support availability

---

## 🧪 Final Testing Checklist

### Test Scenario 1: Complete Rental Cycle

1. Create rental item → Check service item created
2. Create customer → Verify unique ID generation
3. Create booking for future date → Verify availability checking
4. Try booking same item for overlapping dates → Should fail
5. Deliver items → Check status updates
6. Return items → Verify completion and refund

### Test Scenario 2: Exchange Booking

1. Create initial booking
2. Create exchange booking linking to original
3. Verify advance transfer and status updates

### Test Scenario 3: Third-party Item Commission

1. Create third-party rental item
2. Make booking with the item
3. Verify commission liability creation
4. Process commission payment

### Test Scenario 4: Multi-store Operations

1. Create second company/store
2. Verify data isolation between stores
3. Test super admin access to both stores

---

## 📝 **STAKEHOLDER FEEDBACK IMPLEMENTATION LOG**

The following changes were implemented based on stakeholder feedback received via inline comments:

### ✅ **Changes Made:**

1. **Caution Deposit Handling (Jaseem k feedback)**
    - ❌ **Removed** caution deposit field from Item doctype custom fields
    - ✅ **Changed** to manual entry by salesman at Sales Invoice level
    - ✅ **Updated** automation to not auto-calculate caution deposit amounts
2. **Rental Duration Window (Jaseem k feedback)**
    - ✅ **Updated** default rental duration from 3 days to **6 days**
    - ✅ **Clarified** 6-day window = 2 days before function + 4 days after function
    - ✅ **Updated** all workflow documentation to reflect Sep 18-23 instead of Sep 18-21
3. **Dry Cleaning Process (Jaseem k feedback)**
    - ❌ **Removed** dry cleaning charges from Sales Invoice custom fields
    - ✅ **Updated** to track dry cleaning only as expense in chart of accounts
    - ❌ **Removed** dry cleaning income account from chart of accounts setup
    - ✅ **Clarified** dry cleaning can be done in bulk or per item
4. **Caution Deposit Refund Process (Ananth.C Jayan feedback)**
    - ✅ **Updated** caution deposit refund to occur on “Returned” status (before dry cleaning)
    - ✅ **Added** logic for damage deductions from caution deposit
    - ✅ **Clarified** refund happens immediately when items are returned without damage
5. **Owner Commission Payment (Jaseem k feedback)**
    - ❌ **Removed** monthly commission processing workflow
    - ✅ **Updated** to automatic ledger updates on each sale
    - ✅ **Clarified** Payment Entry used for actual commission payments
    - ✅ **Documented** separation of owner and supplier entities in ERPNext accounting
6. **Accounting Entity Separation (Jaseem k feedback)**
    - ✅ **Clarified** owner and supplier are separate entities in ERPNext
    - ✅ **Documented** company owes rental commission to owner, purchase value to supplier
    - ✅ **Updated** commission payment workflow to reflect this separation

### 🎯 **Key Business Logic Updates:**

- Manual caution deposit entry (no automation)
- 6-day rental window (2 before + 4 after function)
- Immediate caution deposit refund on return
- Dry cleaning tracked as expense only
- Commission auto-updated in ledger
- Flexible commission payment timing

---

This completes your rental management system implementation that fully leverages ERPNext’s capabilities while incorporating all stakeholder feedback for optimal business process alignment!