# Item Approval Guide for ERPNext Desk

This guide explains how to approve rental items through the ERPNext Desk interface.

## Method 1: Using the Item Form (Recommended)

### Step 1: Navigate to Item List
1. Login to ERPNext Desk
2. Go to **Stock** module
3. Click on **Item** in the Masters section
4. This will open the Item List view

### Step 2: Filter for Pending Rental Items
1. In the Item List, add filters:
   - **Is Rental Item** = Yes
   - **Approval Status** = Pending Approval
2. This will show all rental items waiting for approval

### Step 3: Open and Approve Items
1. Click on any item from the filtered list
2. This opens the Item form
3. In the **Rental Details** section, you'll see:
   - Approval Status: "Pending Approval"
   - Current Rental Status: (empty or "Pending")
4. Change **Approval Status** to "Approved"
5. Set **Current Rental Status** to "Available"
6. Click **Save**

## Method 2: Using Custom Buttons (Advanced)

You can add custom buttons to the Item form for quick approval/rejection:

### Adding Custom Buttons
Add this code to your Item customization or hooks:

```python
# In hooks.py
doc_events = {
    "Item": {
        "on_load": "rental_management.utils.item_hooks.add_approval_buttons"
    }
}
```

```python
# rental_management/utils/item_hooks.py
import frappe

def add_approval_buttons(doc, handler=""):
    """Add approval buttons to Item form for rental items"""
    if doc.is_rental_item and doc.approval_status == "Pending Approval":
        # Add Approve button
        doc.add_custom_button(
            "Approve for Rental",
            lambda: approve_item_handler(doc.name),
            icon="fa fa-check"
        )
        
        # Add Reject button  
        doc.add_custom_button(
            "Reject",
            lambda: reject_item_handler(doc.name),
            icon="fa fa-times"
        )

def approve_item_handler(item_code):
    """Handle item approval"""
    from rental_management.utils.item_utils import approve_rental_item
    approve_rental_item(item_code)
    frappe.reload_doc("Stock", "doctype", "Item")

def reject_item_handler(item_code):
    """Handle item rejection"""
    # Prompt for rejection reason
    reason = frappe.get_dialog_value("rejection_reason")
    from rental_management.utils.item_utils import reject_rental_item
    reject_rental_item(item_code, reason)
    frappe.reload_doc("Stock", "doctype", "Item")
```

## Method 3: Using a Custom Report/Dashboard

### Create a Rental Items Approval Report
1. Go to **Reports** > **Report Builder**
2. Create a new report with:
   - **Report Type**: Script Report
   - **Module**: Stock
   - **Report Name**: "Rental Items Approval"

```python
# Rental Items Approval Report
import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 150},
        {"fieldname": "rental_rate_per_day", "label": "Rate/Day", "fieldtype": "Currency", "width": 100},
        {"fieldname": "rental_item_type", "label": "Type", "fieldtype": "Data", "width": 100},
        {"fieldname": "approval_status", "label": "Status", "fieldtype": "Data", "width": 120},
        {"fieldname": "owner", "label": "Created By", "fieldtype": "Data", "width": 120},
        {"fieldname": "creation", "label": "Created On", "fieldtype": "Datetime", "width": 140}
    ]
    
    data = frappe.db.sql("""
        SELECT 
            item_code,
            item_name,
            rental_rate_per_day,
            rental_item_type,
            approval_status,
            owner,
            creation
        FROM `tabItem`
        WHERE is_rental_item = 1
        AND approval_status = 'Pending Approval'
        ORDER BY creation DESC
    """, as_dict=True)
    
    return columns, data
```

## Method 4: Bulk Approval (For Multiple Items)

### Using Data Import Tool
1. Go to **Data Import Tool**
2. Select **Item** doctype
3. Download template with existing data
4. Filter for rental items with "Pending Approval" status
5. Update the **approval_status** column to "Approved"
6. Update the **current_rental_status** column to "Available"
7. Upload the file to update multiple items at once

### Using Server Script (Advanced)
Create a server script for bulk approval:

```python
# Server Script: Bulk Approve Rental Items
import frappe

def bulk_approve_rental_items():
    """Approve all pending rental items"""
    pending_items = frappe.get_all("Item", 
        filters={
            "is_rental_item": 1,
            "approval_status": "Pending Approval"
        },
        fields=["name"]
    )
    
    count = 0
    for item in pending_items:
        try:
            doc = frappe.get_doc("Item", item.name)
            doc.approval_status = "Approved"
            doc.current_rental_status = "Available"
            doc.save()
            count += 1
        except Exception as e:
            frappe.log_error(f"Error approving item {item.name}: {str(e)}")
    
    frappe.msgprint(f"Successfully approved {count} rental items")

# Run this in the console or create a custom button
bulk_approve_rental_items()
```

## Key Fields to Check During Approval

When reviewing items for approval, check these fields:

### Essential Information
- **Item Code** & **Item Name**: Clear identification
- **Item Group**: Proper categorization
- **Rental Rate Per Day**: Competitive pricing
- **Description**: Detailed item description
- **Image**: High-quality product images

### Rental-Specific Fields
- **Is Rental Item**: Must be checked
- **Rental Item Type**: Electronics, Furniture, etc.
- **Minimum Rental Days**: Reasonable minimum
- **Maximum Rental Days**: Appropriate maximum
- **Security Deposit**: If applicable

### Third-Party Items (if applicable)
- **Is Third Party Item**: If sourced externally
- **Owner Commission Percent**: Fair commission rate
- **Third Party Owner Details**: Contact information

### Quality & Compliance
- **Item Condition**: Should be "New" or "Good"
- **Compliance certificates**: If required for item type
- **Insurance details**: For high-value items

## Approval Workflow Best Practices

### 1. Review Process
- Check item images and descriptions
- Verify pricing against market rates
- Ensure all required fields are filled
- Validate item condition and availability

### 2. Rejection Reasons
Common reasons to reject items:
- Incomplete information
- Poor quality images
- Unrealistic pricing
- Items not suitable for rental
- Missing compliance certificates

### 3. Communication
- Use comments to communicate with item submitters
- Provide clear feedback for rejected items
- Set expectations for approval timelines

## Monitoring and Reports

### Track Approval Metrics
- Average approval time
- Rejection rates by category
- Most active item submitters
- Revenue potential of approved items

### Regular Reviews
- Weekly approval sessions
- Monthly category reviews
- Quarterly pricing updates
- Annual policy reviews

## Troubleshooting

### Common Issues
1. **Custom fields not visible**: Ensure custom fields are properly installed
2. **Permission errors**: Check user roles and permissions
3. **Save errors**: Validate all required fields are filled

### Error Messages
- "Only rental items can be approved": Item is not marked as rental item
- "Item is already approved": Item status already set to approved
- "Permission denied": User lacks necessary permissions

## Next Steps

After approval:
1. Items become visible on the customer portal
2. Available for booking by shopkeepers
3. Included in inventory reports
4. Can be managed through rental workflows

For technical issues or customizations, refer to the development team or system administrator.
