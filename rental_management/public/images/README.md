# Image Upload Guide for Rental Portal

## Banner Images
Upload banner images through:
**Rental Management > Portal Banner**

### Banner Image Requirements:
- **Dimensions**: 1920x400px (recommended)
- **Format**: JPG, PNG, WebP
- **Size**: Under 2MB
- **Aspect Ratio**: 16:9 or 21:9 for best results

### Banner Fields:
- **Title**: Main headline text
- **Image**: Banner background image
- **Subtitle**: Descriptive text below title
- **Button Text**: Call-to-action button label
- **Button Link**: URL to redirect when button clicked
- **Display Order**: Order of appearance in carousel
- **Show From/To**: Optional date range for display

## Category Images
Upload category images through:
**Rental Management > Portal Category**

### Category Image Requirements:
- **Dimensions**: 300x300px (square, recommended)
- **Format**: JPG, PNG, WebP
- **Size**: Under 1MB
- **Style**: Should work well in circular crop

### Category Fields:
- **Category Name**: Must match your rental item types
- **Image**: Category display image
- **Icon**: Font Awesome icon class (e.g., fa-gem)
- **Display Order**: Order of appearance on home page
- **Description**: Optional category description

## Item Images
Item images are managed through:
**Items > [Item Name] > Images section**

### Item Image Requirements:
- **Dimensions**: 800x800px minimum
- **Format**: JPG, PNG, WebP
- **Size**: Under 3MB per image
- **Multiple angles**: Upload 3-5 images per item

## File Storage
All uploaded images are stored in:
`/private/files/` and accessible via Frappe's file system

## Default Placeholders
Default placeholder images are located in:
`/assets/rental_management/images/`

---

## Quick Setup Steps:

1. **Create Portal Banners**:
   - Go to Rental Management > Portal Banner
   - Click New
   - Upload banner image and set title/subtitle
   - Set display order and activate

2. **Create Portal Categories**:
   - Go to Rental Management > Portal Category  
   - Click New
   - Enter category name (match your item types)
   - Upload category image
   - Set icon and display order

3. **Upload Item Images**:
   - Go to Items > Select your rental item
   - Scroll to Images section
   - Upload multiple product images

Your portal will automatically display these images in the banner carousel and category sections.
