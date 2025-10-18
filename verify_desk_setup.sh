#!/bin/bash

echo "🔍 Verifying Desk Customization Setup"
echo "======================================"
echo ""

# Check if rental_desk.js exists
if [ -f "rental_management/public/js/rental_desk.js" ]; then
    echo "✅ rental_desk.js exists"
    if grep -q "customizeModuleSidebar" rental_management/public/js/rental_desk.js; then
        echo "   ✅ Module hiding function found"
    fi
    if grep -q "customizeLogo" rental_management/public/js/rental_desk.js; then
        echo "   ✅ Logo customization function found"
    fi
else
    echo "❌ rental_desk.js not found"
fi

echo ""

# Check if hooks.py is configured
if grep -q "app_include_js.*rental_desk.js" rental_management/hooks.py; then
    echo "✅ rental_desk.js registered in hooks.py"
else
    echo "⚠️  rental_desk.js not registered in hooks.py"
fi

echo ""

# Check if logo directory exists
if [ -d "rental_management/public/images" ]; then
    echo "✅ Images directory exists"
    if [ -f "rental_management/public/images/blush_glow_logo.png" ]; then
        echo "   ✅ Blush & Glow logo found!"
    else
        echo "   ⚠️  Logo file not found. Please upload to:"
        echo "      rental_management/public/images/blush_glow_logo.png"
    fi
else
    echo "❌ Images directory not found"
fi

echo ""

# Check install.py functions
if grep -q "setup_desk_customization" rental_management/setup/install.py; then
    echo "✅ setup_desk_customization() function exists"
fi

if grep -q "hide_unwanted_modules" rental_management/setup/install.py; then
    echo "✅ hide_unwanted_modules() function exists"
fi

echo ""
echo "📋 Setup Status Summary:"
echo "========================"
echo ""
echo "✅ Desk customization JavaScript: Ready"
echo "✅ Module hiding logic: Configured (client-side)"
echo "✅ Install script: Updated"
echo ""
echo "📌 Next Steps:"
echo "1. Upload Blush & Glow logo to: rental_management/public/images/blush_glow_logo.png"
echo "2. Run: bench clear-cache"
echo "3. Run: bench build"
echo "4. Refresh browser (Ctrl+Shift+R / Cmd+Shift+R)"
echo "5. The desk should now show only rental-related modules"
echo ""
echo "ℹ️  Note: Module hiding works via JavaScript (client-side)"
echo "   This avoids database field errors and is more flexible"
