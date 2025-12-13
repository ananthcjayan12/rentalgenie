# Portal Image Upload Setup Guide

## 📁 **Where to Upload Images**

Your portal now supports two types of images:

### 1. **Banner Images** 
- **Location**: Go to `Portal Banner` DocType in your ERPNext
- **URL**: `/app/portal-banner`
- **Purpose**: Main carousel banners on homepage

### 2. **Category Images**
- **Location**: Go to `Item Group` DocType in your ERPNext  
- **URL**: `/app/item-group`
- **Purpose**: Circular category images below banners

## 🚀 **Installation Steps**

### **Method 1: Automatic (Recommended)**
The portal fields are now automatically installed when you install the Rental Management app:

```bash
# When installing the app
bench --site [your-site] install-app rental_management
```

### **Method 2: Manual Installation**
If you need to run the portal setup separately:

```bash
# Via console
bench --site [your-site] console
```
```python
# Run the portal installation
exec(open('/Users/ananthu/Desktop/new_repos/rentalgenie/install_portal_images.py').read())
```

### **Method 3: Update Existing Installation**
If you already have the app installed, run:

```bash
bench --site [your-site] console
```
```python
from rental_management.custom_fields.item_group_fields import create_item_group_custom_fields, update_existing_item_groups
from rental_management.setup.install import setup_portal_banners

# Install the new fields
create_item_group_custom_fields()
update_existing_item_groups()
setup_portal_banners()
```

## 📋 **Integration with Main Installation**

The portal functionality is now fully integrated into the main app installation via `install.py`:

- ✅ **Item Group portal fields** added via `create_item_group_custom_fields()`
- ✅ **Portal Banner DocType** installed automatically
- ✅ **Existing Item Groups** updated with portal settings
- ✅ **Sample banner** created for demonstration

## � **How to Upload Images**

### **Banner Images**:
1. Go to **Portal Banner** (`/app/portal-banner`)
2. Click **New**
3. Fill in:
   - **Title**: Banner heading text
   - **Banner Image**: Upload your banner image (recommended: 1200x400px)
   - **Subtitle**: Description text
   - **Button Text**: CTA button text (optional)
   - **Button Link**: Where button leads (optional)
   - **Is Active**: ✅ Check to show
   - **Display Order**: 1, 2, 3... (controls sequence)

### **Category Images**:
1. Go to **Item Group** (`/app/item-group`)
2. Select a category (e.g., "Dresses", "Ornaments", "Accessories")
3. Scroll to **Portal Settings** section
4. Fill in:
   - **Portal Category Image**: Upload circular category image (recommended: 300x300px)
   - **Portal Icon Class**: Font Awesome icon (e.g., `fa-gem`, `fa-dress`)
   - **Show in Portal**: ✅ Check to display
   - **Portal Display Order**: 1, 2, 3... (controls sequence)
   - **Portal Description**: Brief category description

## 🎨 **Image Requirements**

### **Banners**:
- **Size**: 1200x400px (3:1 ratio)
- **Format**: JPG, PNG, WebP
- **Style**: High-quality lifestyle/fashion images
- **Text**: Keep minimal (use overlay text fields instead)

### **Categories**:
- **Size**: 300x300px (1:1 ratio)  
- **Format**: JPG, PNG, WebP
- **Style**: Product-focused, clean background
- **Shape**: Will be displayed as circles

## 🔧 **Why Item Group Instead of Portal Category?**

We use ERPNext's built-in **Item Group** with custom portal fields because:

✅ **No Data Duplication** - Reuses existing category structure  
✅ **Maintains Consistency** - Categories already linked to items  
✅ **Follows ERPNext Standards** - Uses built-in DocType  
✅ **Simplified Management** - One place for all category settings  
✅ **Better Integration** - Works with existing item management  

## 🎯 **Features**

- **Auto-rotating banners** (5-second intervals)
- **Responsive design** (mobile-friendly)
- **SEO-friendly** image optimization
- **Date-based scheduling** for banners
- **Icon fallbacks** for categories without images
- **Circular category display** (matches modern design)
- **Integrated installation** (no separate scripts needed)

## 🔍 **File Structure**

```
rental_management/
├── setup/
│   └── install.py (Main installation - includes portal setup)
├── custom_fields/
│   ├── item_fields.py
│   ├── item_group_fields.py (Portal category fields)
│   ├── customer_fields.py
│   └── sales_invoice_fields.py
├── doctype/
│   └── portal_banner/ (Banner management DocType)
├── api/
│   └── customer_portal.py (Banner & category APIs)
└── www/portal/
    ├── index.html (Frontend template)
    └── index.py (Backend context)
```

Your portal image upload functionality is now fully integrated! 🎉