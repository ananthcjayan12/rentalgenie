# Blush & Glow Desk Customization Guide

This guide explains how to customize the ERPNext desk for the Blush & Glow Rental Management system.

## 🎨 What Gets Customized

### 1. **Logo Replacement**
- ERPNext logo → Blush & Glow logo
- Applied to: Navbar, Login page, Website header, Favicon

### 2. **Module Visibility**
Hidden modules (not relevant for rental business):
- CRM, Projects, Support, Quality
- Manufacturing, Buying (traditional), Selling (traditional)
- HR, Payroll, Assets
- Loan Management, Healthcare, Education, Agriculture
- Non Profit, Hospitality

Visible modules (rental-related only):
- **Home** - Dashboard
- **Accounting** - Invoices, Payments, Reports
- **Stock** - Inventory management
- **Rental Management** - Custom rental features
- **Items** - Rental item catalog
- **Customers** - Customer management

### 3. **Theme Colors**
- Primary: #7B2CBF (Purple)
- Secondary: #D4A574 (Gold)
- Accent: #4A4063 (Dark Purple)

### 4. **Key Reports Shown**
- General Ledger
- Profit and Loss Statement
- Balance Sheet
- Cash Flow
- Trial Balance
- Stock Balance
- Stock Ledger

## 📦 Installation Steps

### Step 1: Install the Logo

```bash
# Option 1: Using the install script
chmod +x install_logo.sh
./install_logo.sh

# Option 2: Manual installation
mkdir -p rental_management/public/images
cp /path/to/blush_glow_logo.png rental_management/public/images/
```

**Logo Requirements:**
- Format: PNG (with transparency recommended)
- Recommended size: 200x60 px (or similar aspect ratio)
- Max height will be 40px in navbar

### Step 2: Apply Desk Customizations

The customizations are automatically applied when you install the app. If you've already installed the app, run:

```bash
# From frappe-bench directory
cd frappe-bench

# Clear cache
bench --site your-site-name clear-cache

# Build assets
bench build --app rental_management

# Restart
bench restart
```

### Step 3: Verify Installation

1. **Login to desk**
   - Navigate to: http://your-site:8000/app
   
2. **Check navbar**
   - Top left should show Blush & Glow logo
   - Navbar should be purple (#7B2CBF)

3. **Check sidebar**
   - Only rental-related modules should be visible
   - Hidden: CRM, Projects, HR, Manufacturing, etc.
   - Visible: Home, Accounting, Stock, Items, Customers

4. **Check workspace**
   - "Rental Management" workspace should be available
   - Contains quick links to Items, Customers, Sales Invoice, etc.

## 🎯 Customized Features

### Navbar
- **Logo**: Blush & Glow branding
- **Color**: Purple (#7B2CBF)
- **Hidden items**: Marketplace, unnecessary settings

### Sidebar
- **Only rental modules** shown
- **Hidden modules** via CSS and database settings
- **Custom icons** for rental features

### Buttons & UI
- **Primary buttons**: Purple (#7B2CBF)
- **Success actions**: Green (#10b981)
- **Warning actions**: Orange (#f59e0b)
- **Hover effects**: Darker purple (#6B21A8)

### Reports Section
Accounting reports:
- ✅ General Ledger
- ✅ Profit and Loss Statement
- ✅ Balance Sheet
- ✅ Cash Flow
- ✅ Trial Balance

Stock reports:
- ✅ Stock Balance
- ✅ Stock Ledger
- ✅ Warehouse Summary

## 🔧 Manual Customization

### To Show/Hide Additional Modules

Edit `rental_management/public/js/rental_desk.js`:

```javascript
const modulesToHide = [
    // Add or remove module names here
    'ModuleName',
];
```

### To Change Theme Colors

Edit `rental_management/public/css/rental_theme.css`:

```css
:root {
    --rental-primary: #7B2CBF;    /* Change this */
    --rental-secondary: #D4A574;  /* And this */
    --rental-accent: #4A4063;     /* And this */
}
```

### To Customize Workspace

Run in Frappe console:

```python
# List all workspaces
frappe.get_all("Workspace", fields=["name", "title"])

# Edit Rental Management workspace
workspace = frappe.get_doc("Workspace", "Rental Management")
# Make your changes
workspace.save()
```

## 📋 Files Modified/Created

### New Files
- `rental_management/public/js/rental_desk.js` - Desk customization logic
- `rental_management/public/css/rental_theme.css` - Theme styling
- `rental_management/public/images/blush_glow_logo.png` - Logo file (you provide)

### Modified Files
- `rental_management/hooks.py` - Added CSS/JS includes, logo config
- `rental_management/setup/install.py` - Added desk setup functions

## 🐛 Troubleshooting

### Logo Not Showing
1. Check file exists: `ls rental_management/public/images/blush_glow_logo.png`
2. Clear cache: `bench clear-cache`
3. Build assets: `bench build --app rental_management`
4. Hard refresh browser: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)

### Modules Still Visible
1. Check JavaScript loaded: Open browser console, look for "Desk Customizations Loaded"
2. Clear browser cache
3. Try in incognito/private window
4. Check `rental_desk.js` is included in page source

### Theme Colors Not Applied
1. Check CSS file loaded: View page source, search for `rental_theme.css`
2. Clear cache: `bench clear-cache && bench build`
3. Check browser developer tools for CSS conflicts

### Workspace Not Appearing
1. Check if created: `bench console` → `frappe.db.exists("Workspace", "Rental Management")`
2. Recreate: Run `setup_desk_customization()` from console
3. Clear cache and refresh

## 🚀 Quick Commands

```bash
# Complete setup (after logo is in place)
bench --site your-site clear-cache
bench build --app rental_management
bench restart

# Check customization status
bench console
>>> from rental_management.setup.install import *
>>> setup_desk_customization()
>>> hide_unwanted_modules()

# Reinstall app (caution: resets data)
bench --site your-site reinstall-app rental_management
```

## 📞 Support

If you encounter issues:
1. Check the console for JavaScript errors
2. Verify all files are in place
3. Check Frappe error logs: `bench console` → `frappe.get_error_log()`
4. Review this guide for missed steps

## ✅ Expected Result

After successful installation:
- 🎨 Purple-themed desk with Blush & Glow branding
- 📊 Only rental-related modules visible
- 🔍 Clean, focused interface for rental management
- 📈 Essential accounting and stock reports accessible
- 🚀 Streamlined user experience for staff

---

**Blush & Glow - Premium Bridal Destination** 💍
