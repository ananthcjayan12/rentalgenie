# Rental Management - Simplified Module Hiding Implementation

## Overview
This document explains the simplified approach to hiding unwanted modules in the Rental Management app.

## Approach: Database-Level Module Disabling

Instead of using CSS or complex JavaScript, we simply set the `disabled` field on Module Def documents.

### How It Works

1. **Module Def Disabled Field**
   ```python
   frappe.db.set_value("Module Def", "CRM", "disabled", 1)
   ```
   This marks the module as disabled at the database level.

2. **Frappe Handles the Rest**
   - Disabled modules don't appear in sidebar
   - Disabled modules don't show in module selector
   - Disabled modules don't appear on home page
   - Works for ALL users (including System Manager)

3. **Standard Roles for Permissions**
   Instead of creating custom DocPerms, we assign standard Frappe roles:
   - Item Manager → Full Item access
   - Stock Manager → Full Stock access
   - Accounts Manager → Full Accounting access
   - Sales Manager → Full Sales access

## Files Modified

### 1. `/rental_management/setup/install.py`
- `hide_unwanted_modules()` - Sets Module Def.disabled = 1
- `setup_rental_roles_and_users()` - Creates test user with standard roles

### 2. `/rental_management/setup/boot.py`
- Simplified to just `pass` - not needed anymore

### 3. `/rental_management/public/css/rental_theme.css`
- Removed all module hiding CSS
- Kept only logo customization

### 4. `/rental_management/public/js/rental_desk.js`
- Only handles logo customization
- No module hiding code

## Setup Instructions

### Initial Setup
```bash
# Make the script executable
chmod +x setup_rental_desk_simple.sh

# Run the setup
./setup_rental_desk_simple.sh

# Restart bench
bench restart
```

### Manual Setup
```bash
# 1. Hide modules
bench --site dev.localhost execute rental_management.setup.install.hide_unwanted_modules

# 2. Create test user
bench --site dev.localhost execute rental_management.setup.install.setup_rental_roles_and_users

# 3. Clear cache
bench --site dev.localhost clear-cache

# 4. Restart
bench restart
```

## Test User Credentials

**Email:** rental.manager@example.com  
**Password:** rental123

**Roles:**
- Rental Manager (custom)
- Item Manager
- Stock Manager
- Accounts Manager
- Sales Manager
- Sales User
- Stock User
- Accounts User

## Modules Configuration

### ✅ Visible Modules
- Home
- Stock
- Accounting/Accounts
- Rental Management
- Setup
- Website
- Tools
- Build

### ❌ Hidden Modules
- CRM
- Projects
- Support
- Quality
- Manufacturing
- Buying
- Selling
- HR
- Payroll
- Assets
- Loan Management
- Healthcare
- Education
- Agriculture
- Non Profit
- Hospitality
- Utilities

## Advantages of This Approach

1. **✅ Simple** - Just one database field update
2. **✅ Clean** - No CSS hacks or complex JavaScript
3. **✅ Works Everywhere** - Sidebar, home page, module selector
4. **✅ Works for All Users** - System Manager also affected
5. **✅ Standard Frappe Way** - Uses built-in module management
6. **✅ Maintainable** - Easy to add/remove modules
7. **✅ No Cache Issues** - Changes persist in database

## Re-enabling Modules

If you need to re-enable a module:

```bash
bench --site dev.localhost console
```

```python
frappe.db.set_value("Module Def", "CRM", "disabled", 0)
frappe.db.commit()
```

## Logo Customization

Place your logo at:
```
rental_management/public/images/blush_glow_logo.png
```

The logo will automatically appear in:
- Navbar
- Sidebar
- Login page (favicon)

## Troubleshooting

### Modules still showing?
```bash
# Clear cache completely
bench --site dev.localhost clear-cache
bench --site dev.localhost clear-website-cache

# Rebuild
bench build --app rental_management

# Hard restart
bench restart
```

### User can't access items?
Check roles are assigned:
```python
user = frappe.get_doc("User", "rental.manager@example.com")
print([r.role for r in user.roles])
```

Should include: Item Manager, Stock Manager, Accounts Manager

## Summary

This simplified approach:
- ✅ Disables modules at Module Def level
- ✅ Uses standard Frappe roles for permissions
- ✅ Clean, maintainable code
- ✅ No CSS/JavaScript hacks
- ✅ Works perfectly for all users

**Result:** A clean desk showing only rental-related modules! 🎯
