#!/bin/bash

echo "🎨 Setting up Blush & Glow Desk Customization"
echo "=============================================="

# Step 1: Setup roles and test user
echo ""
echo "📝 Step 1: Setting up Rental Manager role and test user..."
bench --site dev.localhost execute rental_management.setup.install.setup_rental_roles_and_users

# Step 2: Clear all caches
echo ""
echo "🧹 Step 2: Clearing caches..."
bench --site dev.localhost clear-cache
bench --site dev.localhost clear-website-cache

# Step 3: Build assets
echo ""
echo "🔨 Step 3: Building assets..."
bench build --app rental_management

# Step 4: Restart bench
echo ""
echo "🔄 Step 4: Restarting bench..."
bench restart

echo ""
echo "="*60
echo "✅ Setup Complete!"
echo "="*60
echo ""
echo "📌 IMPORTANT: Clear your browser cache!"
echo "   Chrome/Edge: Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)"
echo "   Firefox: Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)"
echo "   Or use Incognito/Private mode"
echo ""
echo "🔐 Test User Credentials:"
echo "   Email: rental.manager@example.com"
echo "   Password: rental123"
echo ""
echo "✅ Visible Modules (via CSS hiding):"
echo "   - Home"
echo "   - Accounting/Accounts"
echo "   - Stock"
echo "   - Rental Management"
echo "   - Build"
echo "   - Tools"
echo "   - Setup"
echo "   - Website"
echo ""
echo "🚫 Hidden Modules:"
echo "   - CRM, Projects, Support, Manufacturing"
echo "   - Buying, Selling, HR, Payroll, Assets"
echo "   - And other non-rental modules"
echo ""
echo "="*60
