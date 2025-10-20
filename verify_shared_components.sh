#!/bin/bash

# Verify Portal Shared Components Implementation

echo "🔍 Verifying Portal Shared Components Implementation"
echo "===================================================="

PORTAL_DIR="/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/www/portal"

# Function to check a portal page
check_portal_page() {
    local page_path="$1"
    local page_name="$2"
    local expected_current_page="$3"
    
    if [ -f "$page_path" ]; then
        echo "📄 Checking $page_name..."
        
        # Check if shared styles are included
        if grep -q "portal_styles.html" "$page_path"; then
            echo "  ✅ Includes shared styles"
        else
            echo "  ❌ Missing shared styles include"
        fi
        
        # Check if shared bottom nav is used
        if grep -q "{% include \"templates/includes/bottom_nav.html\" %}" "$page_path"; then
            echo "  ✅ Uses shared bottom navigation"
        elif grep -q "bottom-nav" "$page_path"; then
            echo "  ⚠️  Has bottom navigation but not using shared component"
        else
            echo "  ℹ️  No bottom navigation found"
        fi
        
        # Check if currentPage variable exists
        if grep -q "currentPage:" "$page_path"; then
            echo "  ✅ Has currentPage variable"
        else
            echo "  ⚠️  Missing currentPage variable"
        fi
        
        # Check for duplicate CSS (portal-header styles)
        if grep -q ".portal-header {" "$page_path"; then
            echo "  ⚠️  Contains duplicate portal-header styles"
        else
            echo "  ✅ No duplicate portal-header styles"
        fi
        
    else
        echo "  ❌ $page_name not found"
    fi
    echo ""
}

echo "1. Index Page (Home)..."
if [ -f "$PORTAL_DIR/index.html" ]; then
    if grep -q "portal_styles.html" "$PORTAL_DIR/index.html"; then
        echo "  ✅ Includes shared styles"
    else
        echo "  ❌ Missing shared styles include"
    fi
    
    if grep -q "{% include \"templates/includes/bottom_nav.html\" %}" "$PORTAL_DIR/index.html"; then
        echo "  ✅ Uses shared bottom navigation"
    else
        echo "  ❌ Not using shared bottom navigation"
    fi
    
    if grep -q "currentPage: 'home'" "$PORTAL_DIR/index.html"; then
        echo "  ✅ Has currentPage variable set to 'home'"
    else
        echo "  ⚠️  Missing or incorrect currentPage variable"
    fi
else
    echo "  ❌ Index page not found"
fi
echo ""

# Check other portal pages
check_portal_page "$PORTAL_DIR/category/index.html" "Category Page" "browse"
check_portal_page "$PORTAL_DIR/cart/index.html" "Cart Page" "cart"
check_portal_page "$PORTAL_DIR/staff/index.html" "Staff Page" "bookings"
check_portal_page "$PORTAL_DIR/profile/index.html" "Profile Page" "profile"

echo "🎯 Summary:"
echo "- ✅ = Implemented correctly"
echo "- ⚠️  = Partially implemented or needs attention"
echo "- ❌ = Missing or not implemented"
echo "- ℹ️  = Informational"
echo ""
echo "🔧 Recommendation:"
echo "Focus on pages with ✅ for shared styles and navigation for full DRY implementation"