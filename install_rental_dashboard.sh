#!/bin/bash

echo "🚀 Installing Rental Management Dashboard & Workspace"
echo "====================================================="

cd /workspace/development/frappe-bench

echo ""
echo "Step 1: Clear all caches..."
bench --site dev.localhost clear-cache
bench --site dev.localhost clear-website-cache

echo ""
echo "Step 2: Build assets..."
bench build --app rental_management

echo ""
echo "Step 3: Run migration (this will install workspace from JSON)..."
bench --site dev.localhost migrate

echo ""  
echo "Step 4: Setup test user and roles..."
bench --site dev.localhost execute rental_management.setup.install.setup_rental_roles_and_users

echo ""
echo "Step 5: Restart bench..."
bench restart

echo ""
echo "✅ Installation Complete!"
echo ""
echo "🎯 What's been set up:"
echo "  ✅ Rental Management workspace with dashboard"
echo "  ✅ Quick access shortcuts (Item, Sales Invoice, Customer, etc.)"
echo "  ✅ Organized cards (Item Management, Customer Management, etc.)"
echo "  ✅ Module hiding (only Stock, Accounting, Rental Management visible)"
echo "  ✅ Test user: rental.manager@example.com / rental123"
echo ""
echo "📋 Next Steps:"
echo "1. Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)" 
echo "2. Look for 'Rental Management' in the left sidebar"
echo "3. Click it to see your dashboard with:"
echo "   - Quick Access: Item, Sales Invoice, Customer, Payment Entry, etc."
echo "   - Masters & Reports: Item Management, Customer Management, etc."
echo ""
echo "🔍 If Rental Management workspace doesn't appear:"
echo "   - Try logging out and back in"
echo "   - Or login as test user: rental.manager@example.com / rental123"
echo "   - The workspace should be visible in the sidebar"