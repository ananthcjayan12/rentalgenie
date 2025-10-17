#!/bin/bash

# Update Portal Pages to Use Shared Components

echo "🔄 Updating Portal Pages to Use Shared Components"
echo "=================================================="

PORTAL_DIR="/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/www/portal"

# Function to backup and update a portal page
update_portal_page() {
    local page_path="$1"
    local page_name="$2"
    local current_page_value="$3"
    
    if [ -f "$page_path" ]; then
        echo "📝 Updating $page_name..."
        
        # Create backup
        cp "$page_path" "${page_path}.backup"
        
        # Add shared styles include if not present
        if ! grep -q "portal_styles.html" "$page_path"; then
            # Find the head_include block and add shared styles
            sed -i '' '/{% block head_include %}/,/{% endblock %}/ {
                /script defer src.*alpinejs/a\
\
{% include "templates/includes/portal_styles.html" %}
            }' "$page_path"
            echo "  ✅ Added shared styles include"
        else
            echo "  ℹ️  Shared styles already included"
        fi
        
        # Update bottom navigation if present
        if grep -q "bottom-nav" "$page_path"; then
            # Replace bottom navigation with shared component
            perl -i -pe 'BEGIN{undef $/;} s/<nav class="bottom-nav">.*?<\/nav>/{% include "templates\/includes\/bottom_nav.html" %}/smg' "$page_path"
            echo "  ✅ Updated bottom navigation to use shared component"
        fi
        
        # Add currentPage variable to JavaScript if AlpineJS is used
        if grep -q "x-data=" "$page_path" && ! grep -q "currentPage:" "$page_path"; then
            sed -i '' "s/return {/return {\n        currentPage: '$current_page_value',/" "$page_path"
            echo "  ✅ Added currentPage variable"
        fi
        
        echo "  ✅ $page_name updated successfully"
    else
        echo "  ❌ $page_name not found at $page_path"
    fi
    echo ""
}

# Update each portal page
echo "1. Updating Category Page..."
update_portal_page "$PORTAL_DIR/category/index.html" "Category Page" "browse"

echo "2. Updating Cart Page..."
update_portal_page "$PORTAL_DIR/cart/index.html" "Cart Page" "cart"

echo "3. Updating Staff Page..."
update_portal_page "$PORTAL_DIR/staff/index.html" "Staff Page" "bookings"

echo "4. Updating Profile Page..."
update_portal_page "$PORTAL_DIR/profile/index.html" "Profile Page" "profile"

echo "5. Updating Item Page..."
update_portal_page "$PORTAL_DIR/item/index.html" "Item Page" "browse"

echo "6. Updating Checkout Page..."
update_portal_page "$PORTAL_DIR/checkout/index.html" "Checkout Page" "cart"

echo "7. Updating Bookings Page..."
update_portal_page "$PORTAL_DIR/bookings/index.html" "Bookings Page" "bookings"

echo "🎉 Portal Pages Update Complete!"
echo ""
echo "📋 Summary of Changes:"
echo "- Added shared portal_styles.html include to all pages"
echo "- Replaced bottom navigation with shared component"
echo "- Added currentPage variable for navigation active states"
echo "- Created backup files for all modified pages"
echo ""
echo "✨ Next Steps:"
echo "1. Test each portal page to ensure styling works correctly"
echo "2. Verify navigation active states are working"
echo "3. Remove backup files once testing is complete"
echo "4. Consider updating headers to shared component where appropriate"