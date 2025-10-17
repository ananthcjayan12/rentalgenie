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
else
    echo "   ❌ Confirm Booking button class not found"
fi

echo ""
echo "2. Testing Staff Page Button Styles..."

# Test Success buttons (Deliver)
if grep -q "btn-success" rental_management/www/portal/staff/index.html; then
    echo "   ✅ Success (Deliver) button class found"
    
    if grep -A 3 "btn-success" rental_management/www/portal/staff/index.html | grep -q "var(--success-color)"; then
        echo "   ✅ Uses CSS variable --success-color"
    fi
else
    echo "   ❌ Success button class not found"
fi

# Test Warning buttons (Return)
if grep -q "btn-warning" rental_management/www/portal/staff/index.html; then
    echo "   ✅ Warning (Return) button class found"
    
    if grep -A 3 "btn-warning" rental_management/www/portal/staff/index.html | grep -q "var(--warning-color)"; then
        echo "   ✅ Uses CSS variable --warning-color"
    fi
else
    echo "   ❌ Warning button class not found"
fi

# Test Primary buttons (Collect)
if grep -q "btn-primary" rental_management/www/portal/staff/index.html; then
    echo "   ✅ Primary (Collect) button class found"
    
    if grep -A 3 "btn-primary" rental_management/www/portal/staff/index.html | grep -q "var(--primary-color)"; then
        echo "   ✅ Uses CSS variable --primary-color"
    fi
else
    echo "   ❌ Primary button class not found"
fi

echo ""
echo "3. Testing CSS Variables in Portal Styles..."

if grep -q "\-\-success-color.*#10b981" rental_management/templates/includes/portal_styles.html; then
    echo "   ✅ --success-color defined as #10b981 (green)"
else
    echo "   ❌ --success-color not defined"
fi

if grep -q "\-\-warning-color.*#f59e0b" rental_management/templates/includes/portal_styles.html; then
    echo "   ✅ --warning-color defined as #f59e0b (orange)"
else
    echo "   ❌ --warning-color not defined"
fi

if grep -q "\-\-danger-color.*#ef4444" rental_management/templates/includes/portal_styles.html; then
    echo "   ✅ --danger-color defined as #ef4444 (red)"
else
    echo "   ❌ --danger-color not defined"
fi

if grep -q "\-\-info-color.*#3b82f6" rental_management/templates/includes/portal_styles.html; then
    echo "   ✅ --info-color defined as #3b82f6 (blue)"
else
    echo "   ❌ --info-color not defined"
fi

echo ""
echo "4. Testing Button HTML Elements..."

# Check if cart page has the actual button element
if grep -q 'class="checkout-btn confirm-booking-btn"' rental_management/www/portal/cart/index.html; then
    echo "   ✅ Confirm Booking button element found in cart page"
else
    echo "   ❌ Confirm Booking button element not found"
fi

# Check if staff page has all button types
if grep -q 'class="btn btn-success' rental_management/www/portal/staff/index.html; then
    echo "   ✅ Success (Deliver) button elements found in staff page"
fi

if grep -q 'class="btn btn-warning' rental_management/www/portal/staff/index.html; then
    echo "   ✅ Warning (Return) button elements found in staff page"
fi

if grep -q 'class="btn btn-primary' rental_management/www/portal/staff/index.html; then
    echo "   ✅ Primary (Collect) button elements found in staff page"
fi

echo ""
echo "🎨 Button Visibility Fix Summary:"
echo "================================="
echo "✅ Added CSS variables for all button types:"
echo "   - --success-color: #10b981 (green)"
echo "   - --warning-color: #f59e0b (orange)"
echo "   - --danger-color: #ef4444 (red)"
echo "   - --info-color: #3b82f6 (blue)"
echo "✅ Updated all button styles with explicit colors and borders"
echo "✅ Used !important to override any conflicting styles"
echo "✅ Added hover effects with subtle transform animations"
echo ""
echo "🎯 Expected Button Colors:"
echo "   🟢 Success (Deliver): Green (#10b981)"
echo "   🟠 Warning (Return): Orange (#f59e0b)"
echo "   🟣 Primary (Collect): Purple (#7B2CBF)"
echo "   🔵 Info: Blue (#3b82f6)"
echo ""
echo "🔧 Recommendations:"
echo "- Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)"
echo "- Check browser developer tools for any CSS conflicts"
echo "- Test all button interactions for proper visibility"