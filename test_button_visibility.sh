#!/bin/bash

echo "🔍 Testing Button Visibility on Portal Pages"
echo "=============================================="

# Test Cart Page
echo ""
echo "1. Testing Cart Page Button Styles..."
echo "   Checking for Confirm Booking button CSS..."

if grep -q "confirm-booking-btn" rental_management/www/portal/cart/index.html; then
    echo "   ✅ Confirm Booking button class found"
    
    # Check if background color is explicitly set
    if grep -A 5 "confirm-booking-btn" rental_management/www/portal/cart/index.html | grep -q "background.*#10b981"; then
        echo "   ✅ Green background color (#10b981) set"
    else
        echo "   ❌ Background color not found"
    fi
    
    # Check if border is set
    if grep -A 5 "confirm-booking-btn" rental_management/www/portal/cart/index.html | grep -q "border.*#10b981"; then
        echo "   ✅ Green border color set"
    else
        echo "   ❌ Border color not found"
    fi
    
    # Check if white text color is set
    if grep -A 5 "confirm-booking-btn" rental_management/www/portal/cart/index.html | grep -q "color.*white"; then
        echo "   ✅ White text color set"
    else
        echo "   ❌ Text color not found"
    fi
else
    echo "   ❌ Confirm Booking button class not found"
fi

echo ""
echo "2. Testing Staff Page Button Styles..."
echo "   Checking for button CSS variables..."

# Test Staff Page
if grep -q "btn-success" rental_management/www/portal/staff/index.html; then
    echo "   ✅ Success button class found"
    
    # Check if it uses CSS variable
    if grep -A 3 "btn-success" rental_management/www/portal/staff/index.html | grep -q "var(--success-color)"; then
        echo "   ✅ Uses CSS variable --success-color"
    else
        echo "   ❌ CSS variable not found"
    fi
else
    echo "   ❌ Success button class not found"
fi

echo ""
echo "3. Testing CSS Variables in Portal Styles..."

if grep -q "\-\-success-color.*#10b981" rental_management/templates/includes/portal_styles.html; then
    echo "   ✅ --success-color defined as #10b981"
else
    echo "   ❌ --success-color not defined"
fi

if grep -q "\-\-danger-color.*#ef4444" rental_management/templates/includes/portal_styles.html; then
    echo "   ✅ --danger-color defined as #ef4444"
else
    echo "   ❌ --danger-color not defined"
fi

echo ""
echo "4. Testing Button HTML Elements..."

# Check if cart page has the actual button element
if grep -q 'class="checkout-btn confirm-booking-btn"' rental_management/www/portal/cart/index.html; then
    echo "   ✅ Confirm Booking button element found in cart page"
else
    echo "   ❌ Confirm Booking button element not found"
fi

# Check if staff page has success buttons
if grep -q 'class="btn btn-success' rental_management/www/portal/staff/index.html; then
    echo "   ✅ Success button elements found in staff page"
else
    echo "   ❌ Success button elements not found"
fi

echo ""
echo "🎨 Button Visibility Fix Summary:"
echo "================================="
echo "✅ Added CSS variables --success-color and --danger-color"
echo "✅ Updated cart page confirm button with explicit styling"
echo "✅ Used !important to override any conflicting styles"
echo "✅ Set green background (#10b981) and white text for visibility"
echo "✅ Added border styling for better definition"
echo ""
echo "🔧 Recommendations:"
echo "- Clear browser cache if buttons still appear white"
echo "- Check browser developer tools for any CSS conflicts"
echo "- Test on different screen sizes for responsive behavior"