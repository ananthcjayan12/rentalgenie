#!/bin/bash

echo "🚀 Setting up Rental Management - Simplified Approach"
echo "======================================================"
echo ""

# Hide unwanted modules at database level
echo "1️⃣ Hiding unwanted modules..."
bench --site dev.localhost execute rental_management.setup.install.hide_unwanted_modules

echo ""
echo "2️⃣ Setting up Rental Manager role and test user..."
bench --site dev.localhost execute rental_management.setup.install.setup_rental_roles_and_users

echo ""
echo "3️⃣ Clearing cache..."
bench --site dev.localhost clear-cache
bench --site dev.localhost clear-website-cache

echo ""
echo "4️⃣ Building assets..."
bench build --app rental_management

echo ""
echo "======================================================"
echo "✅ Setup Complete!"
echo "======================================================"
echo ""
echo "📋 What was done:"
echo "   ✅ Disabled unwanted modules in Module Def"
echo "   ✅ Created Rental Manager role"
echo "   ✅ Created test user with full permissions"
echo "   ✅ Cleared all caches"
echo "   ✅ Rebuilt assets"
echo ""
echo "🔄 Next Steps:"
echo "   1. Restart bench: bench restart"
echo "   2. Logout from current user"
echo "   3. Login with: rental.manager@example.com / rental123"
echo "   4. You should see only rental-related modules!"
echo ""
echo "✨ Modules visible: Stock, Accounting, Rental Management,"
echo "   Setup, Website, Home, Tools, Build"
echo ""
echo "❌ Modules hidden: CRM, Projects, Buying, Selling, HR,"
echo "   Payroll, Manufacturing, Assets, etc."
echo ""
echo "======================================================"
