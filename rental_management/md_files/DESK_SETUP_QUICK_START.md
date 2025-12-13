# 🎨 Blush & Glow Desk Customization - Quick Start

## ✅ What's Been Set Up

### 1. Files Created
- ✅ `rental_management/public/js/rental_desk.js` - Hides unwanted modules
- ✅ `rental_management/public/css/rental_theme.css` - Purple theme styling
- ✅ `install_logo.sh` - Logo installation helper
- ✅ `setup_desk_customization.sh` - Complete setup automation
- ✅ `BLUSH_GLOW_CUSTOMIZATION.md` - Full documentation

### 2. Files Modified
- ✅ `rental_management/hooks.py` - Added CSS/JS includes, logo config
- ✅ `rental_management/setup/install.py` - Added desk setup functions

### 3. Features Implemented
- ✅ **Module Hiding**: Hides CRM, HR, Manufacturing, Buying, Selling, etc.
- ✅ **Module Display**: Shows only Accounting, Stock, Items, Customers, Rental features
- ✅ **Logo Integration**: Blush & Glow logo in navbar, login, website
- ✅ **Theme Colors**: Purple (#7B2CBF) and Gold (#D4A574) theme
- ✅ **Reports**: Shows only relevant reports (P&L, Balance Sheet, Stock, etc.)

## 🚀 Installation Steps

### Step 1: Install the Logo

```bash
# Place your Blush & Glow logo in the rental management images directory
mkdir -p rental_management/public/images
cp /path/to/your/blush_glow_logo.png rental_management/public/images/

# Verify
ls -lh rental_management/public/images/blush_glow_logo.png
```

**Logo Requirements:**
- Format: PNG (transparency recommended)
- Size: ~200x60px (will be scaled to 40px height)
- Filename: Must be exactly `blush_glow_logo.png`

### Step 2: Run the Setup Script

```bash
# From the rentalgenie directory
chmod +x setup_desk_customization.sh
./setup_desk_customization.sh

# Enter your site name when prompted (e.g., dev.localhost)
```

### Step 3: Verify the Changes

1. **Open desk**: http://your-site:8000/app
2. **Hard refresh browser**: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
3. **Check for**:
   - Purple navbar
   - Blush & Glow logo (if installed)
   - Only rental modules visible
   - Clean, focused interface

## 📋 Modules Shown vs Hidden

### ✅ SHOWN (Rental-Related)
- Home / Dashboard
- Accounting (Invoices, Payments, Journal Entries)
- Stock (Inventory, Warehouses)
- Items (Rental item catalog)
- Customers
- Reports (P&L, Balance Sheet, Stock Balance)
- Portal Management (Banners, Categories)
- Third Party Owner (if applicable)

### ❌ HIDDEN (Not Needed)
- CRM (Leads, Opportunities)
- Projects & Tasks
- Support & Issues
- Manufacturing & BOM
- Traditional Buying (POs, Suppliers)
- Traditional Selling (Sales Orders)
- HR & Payroll
- Assets Management
- Quality, Healthcare, Education, etc.

## 🎯 Key Reports Available

### Accounting Reports
- ✅ General Ledger
- ✅ Profit and Loss Statement
- ✅ Balance Sheet
- ✅ Cash Flow Statement
- ✅ Trial Balance
- ✅ Accounts Receivable
- ✅ Accounts Payable

### Stock Reports
- ✅ Stock Balance
- ✅ Stock Ledger
- ✅ Stock Summary
- ✅ Warehouse-wise Stock Balance

### Rental-Specific
- ✅ Sales Invoice List (Rental bookings)
- ✅ Payment Entry List
- ✅ Customer List
- ✅ Item List (Rental catalog)

## 🔧 Manual Application (if script fails)

```bash
cd /path/to/frappe-bench

# Clear cache
bench --site your-site clear-cache

# Build assets
bench build --app rental_management

# Restart
bench restart

# Apply customizations via console
bench --site your-site console

# In console:
from rental_management.setup.install import setup_desk_customization, hide_unwanted_modules
setup_desk_customization()
hide_unwanted_modules()
frappe.db.commit()
exit()
```

## 🐛 Troubleshooting

### Logo Not Showing
```bash
# Check file exists
ls rental_management/public/images/blush_glow_logo.png

# If missing, copy it there
cp /path/to/logo.png rental_management/public/images/blush_glow_logo.png

# Clear cache and rebuild
bench --site your-site clear-cache
bench build --app rental_management
bench restart
```

### Modules Still Visible
- Hard refresh browser (Ctrl+F5)
- Try incognito/private window
- Check browser console for JavaScript errors
- Verify `rental_desk.js` is loaded (view page source)

### Theme Not Applied
- Clear browser cache
- Check CSS file loaded: View source → search for `rental_theme.css`
- Run: `bench build --app rental_management`

## 📱 What Users Will See

### Before Customization
- ERPNext logo
- All default modules (50+ items in sidebar)
- Generic blue/white theme
- Overwhelming options

### After Customization
- Blush & Glow logo ✨
- Only 8-10 relevant modules
- Purple and gold theme (brand colors)
- Focused, clean interface
- Only rental-related features

## 🎨 Branding Details

### Colors Used
- **Primary**: #7B2CBF (Purple)
- **Secondary**: #D4A574 (Gold/Beige)
- **Accent**: #4A4063 (Dark Purple)
- **Success**: #10b981 (Green)
- **Warning**: #f59e0b (Orange)

### Typography
- Uses system fonts for performance
- Purple headings for brand consistency
- Clean, modern interface

## 📁 File Locations

```
rentalgenie/
├── rental_management/
│   ├── hooks.py (modified)
│   ├── setup/
│   │   └── install.py (modified)
│   └── public/
│       ├── js/
│       │   └── rental_desk.js (NEW)
│       ├── css/
│       │   └── rental_theme.css (NEW)
│       └── images/
│           ├── README.md (updated)
│           └── blush_glow_logo.png (YOU ADD THIS)
├── install_logo.sh (NEW)
├── setup_desk_customization.sh (NEW)
└── BLUSH_GLOW_CUSTOMIZATION.md (NEW)
```

## ✨ Next Steps

After successful installation:

1. **Upload Portal Images**
   - Navigate to: `/app/portal-banner`
   - Add promotional banners

2. **Configure Categories**
   - Navigate to: `/app/item-group`
   - Upload category images (Dresses, Ornaments, etc.)

3. **Test Portal**
   - Visit: `/portal`
   - Verify branding is consistent

4. **Train Staff**
   - Show them the simplified interface
   - Explain focused workflows

## 📞 Need Help?

- Full documentation: `BLUSH_GLOW_CUSTOMIZATION.md`
- Logo installation: `./install_logo.sh`
- Complete setup: `./setup_desk_customization.sh`

---

**Blush & Glow - Premium Bridal Destination** 💍

*Transforming ERPNext into a beautiful, focused rental management system*
