# Implementation Steps for Item Approval in ERPNext Desk

## Quick Answer: Where to Approve Items

**The simplest way to approve rental items is:**

1. **Login to ERPNext Desk** (your admin interface)
2. **Go to Stock → Item** (or use the search bar and type "Item List")
3. **Filter the list** by adding these filters:
   - Is Rental Item = Yes
   - Approval Status = Pending Approval
4. **Click on any item** to open it
5. **Scroll to the "Rental Details" section**
6. **Change "Approval Status"** from "Pending Approval" to "Approved"
7. **Set "Current Rental Status"** to "Available"
8. **Click Save**

That's it! The item is now approved and will appear on your customer portal.

---

## Advanced Implementation (Optional)

If you want to enhance the approval experience with custom buttons and workflows, follow these steps:

### Step 1: Add Custom Hooks

Add this to your `rental_management/hooks.py` file:

```python
# Add to existing hooks.py
doc_events = {
    "Item": {
        "on_load": "rental_management.utils.item_hooks.add_approval_buttons"
    }
}
```

### Step 2: Enable Custom JavaScript

1. Go to **Customize Form** in ERPNext
2. Search for and select **Item**
3. Scroll down to **Custom Script** section
4. Add this JavaScript code:

```javascript
frappe.ui.form.on('Item', {
    refresh: function(frm) {
        if (frm.doc.is_rental_item && frm.doc.approval_status === 'Pending Approval') {
            // Add quick approve button
            frm.add_custom_button(__('Quick Approve'), function() {
                frappe.confirm(
                    __('Approve this item for rental?'),
                    function() {
                        frm.set_value('approval_status', 'Approved');
                        frm.set_value('current_rental_status', 'Available');
                        frm.save();
                        frappe.show_alert({
                            message: __('Item approved successfully!'),
                            indicator: 'green'
                        });
                    }
                );
            }).addClass('btn-success');
        }
        
        // Show pending approval count
        if (frm.doc.is_rental_item) {
            frappe.db.count('Item', {
                is_rental_item: 1,
                approval_status: 'Pending Approval'
            }).then(count => {
                if (count > 0) {
                    frm.dashboard.add_indicator(__('Pending Approvals: {0}', [count]), 'orange');
                }
            });
        }
    }
});
```

4. **Save** the customization

### Step 3: Create an Approval Dashboard (Optional)

1. Go to **Dashboard** in ERPNext
2. Create a new dashboard called "Rental Management"
3. Add these charts:
   - **Pending Approvals**: Count of items with status "Pending Approval"
   - **Approved Items**: Count of approved rental items
   - **Revenue This Month**: Total rental revenue

### Step 4: Create Custom Report (Optional)

1. Go to **Report Builder**
2. Create a new **Script Report**
3. Name it "Rental Items Approval Queue"
4. Use this code:

```python
import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "rental_rate_per_day", "label": "Rate/Day", "fieldtype": "Currency", "width": 100},
        {"fieldname": "creation", "label": "Submitted On", "fieldtype": "Date", "width": 120},
        {"fieldname": "owner", "label": "Submitted By", "fieldtype": "Data", "width": 150}
    ]
    
    data = frappe.db.sql("""
        SELECT 
            item_code,
            item_name,
            rental_rate_per_day,
            DATE(creation) as creation,
            owner
        FROM `tabItem`
        WHERE is_rental_item = 1
        AND approval_status = 'Pending Approval'
        ORDER BY creation DESC
    """, as_dict=True)
    
    return columns, data
```

---

## Testing the Approval Process

### 1. Create a Test Item
1. Go to **Stock → Item** 
2. Click **New**
3. Fill in basic details (Item Code, Item Name)
4. Check **"Is Rental Item"**
5. Set **"Approval Status"** to "Pending Approval"
6. Fill rental details (rate, type, etc.)
7. **Save**

### 2. Test Approval
1. Navigate back to the item
2. Change **"Approval Status"** to "Approved"
3. Set **"Current Rental Status"** to "Available"
4. **Save**
5. Check that the item now appears on your customer portal

### 3. Verify Portal Visibility
1. Open your customer portal URL
2. Browse categories or search for your test item
3. Confirm it appears in the available items

---

## Common Issues and Solutions

### Issue: Custom fields not visible
**Solution**: Ensure you've run the custom fields installation:
```bash
bench execute rental_management.custom_fields.customer_fields.install_custom_fields
```

### Issue: Permission denied when approving
**Solution**: Ensure your user has the "Stock Manager" role or equivalent permissions for the Item doctype.

### Issue: Items not appearing on portal after approval
**Solution**: 
1. Check that **approval_status** = "Approved"
2. Check that **current_rental_status** = "Available" 
3. Verify the item has proper **rental_rate_per_day** set
4. Clear your browser cache and refresh the portal

### Issue: Approval Status field missing
**Solution**: The field should be created automatically. If missing, add it manually:
1. Go to **Customize Form**
2. Select **Item** doctype
3. Add new field:
   - Field Type: Select
   - Field Name: approval_status
   - Label: Approval Status
   - Options: Pending Approval\nApproved\nRejected

---

## Next Steps

Once you have the basic approval working:

1. **Set up user permissions** for different approval levels
2. **Create approval workflows** for different item categories
3. **Add notification emails** when items are approved/rejected
4. **Set up automated approval** for trusted suppliers
5. **Create approval reports** for tracking and analytics

The basic manual approval through the Item form is sufficient to get started, and you can add the advanced features as your rental business grows!
