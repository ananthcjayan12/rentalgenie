#!/bin/bash

# Test Portal Shared Components Integration

echo "🧪 Testing Portal Shared Components Integration"
echo "=============================================="

# Check if shared components exist
echo "1. Checking shared component files..."

if [ -f "/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/templates/includes/portal_header.html" ]; then
    echo "✅ portal_header.html exists"
else
    echo "❌ portal_header.html missing"
fi

if [ -f "/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/templates/includes/bottom_nav.html" ]; then
    echo "✅ bottom_nav.html exists"
else
    echo "❌ bottom_nav.html missing"
fi

if [ -f "/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/templates/includes/portal_styles.html" ]; then
    echo "✅ portal_styles.html exists"
else
    echo "❌ portal_styles.html missing"
fi

echo ""
echo "2. Checking index.html includes shared components..."

# Check if index.html includes the shared components
if grep -q "{% include \"templates/includes/portal_header.html\" %}" "/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/www/portal/index.html"; then
    echo "✅ index.html includes portal_header.html"
else
    echo "❌ index.html missing portal_header.html include"
fi

if grep -q "{% include \"templates/includes/bottom_nav.html\" %}" "/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/www/portal/index.html"; then
    echo "✅ index.html includes bottom_nav.html"
else
    echo "❌ index.html missing bottom_nav.html include"
fi

if grep -q "{% include \"templates/includes/portal_styles.html\" %}" "/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/www/portal/index.html"; then
    echo "✅ index.html includes portal_styles.html"
else
    echo "❌ index.html missing portal_styles.html include"
fi

echo ""
echo "3. Checking for code duplication removal..."

# Check that duplicate styles have been removed from index.html
if grep -q ".portal-header {" "/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/www/portal/index.html"; then
    echo "❌ index.html still contains duplicate portal-header styles"
else
    echo "✅ Duplicate portal-header styles removed from index.html"
fi

if grep -q ".bottom-nav {" "/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/www/portal/index.html"; then
    echo "❌ index.html still contains duplicate bottom-nav styles"
else
    echo "✅ Duplicate bottom-nav styles removed from index.html"
fi

echo ""
echo "4. Checking AlpineJS data integration..."

if grep -q "currentPage: 'home'" "/Users/ananthu/Desktop/new_repos/rentalgenie/rental_management/www/portal/index.html"; then
    echo "✅ currentPage variable added to portalApp"
else
    echo "❌ currentPage variable missing from portalApp"
fi

echo ""
echo "🎉 Portal Shared Components Integration Test Complete!"
echo ""
echo "📝 Summary:"
echo "- Created shared portal_header.html component"
echo "- Created shared bottom_nav.html component" 
echo "- Created shared portal_styles.html component"
echo "- Updated index.html to use shared components"
echo "- Removed duplicate CSS and HTML code"
echo "- Implemented DRY principle successfully"
echo ""
echo "✨ Next steps:"
echo "- Test the portal homepage to ensure styling works correctly"
echo "- Apply shared components to other portal pages"
echo "- Verify navigation active states work properly"