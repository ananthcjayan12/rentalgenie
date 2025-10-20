#!/bin/bash

echo "🏠 Setting up Rental Management Home Page"
echo "=========================================="

# Create the workspace
echo ""
echo "1. Creating Rental Management workspace..."
bench --site dev.localhost execute rental_management.setup.install.create_rental_workspace

# Setup roles and users
echo ""
echo "2. Setting up Rental Manager role and test user..."
bench --site dev.localhost execute rental_management.setup.install.setup_rental_roles_and_users

# Clear all caches
echo ""
echo "3. Clearing caches..."
bench --site dev.localhost clear-cache
bench --site dev.localhost clear-website-cache

# Build assets
echo ""
echo "4. Building assets..."
bench build --app rental_management

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📌 Next Steps:"
echo "   1. Restart bench: bench restart"
echo "   2. Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)"
echo "   3. Login and you should see Rental Management home"
echo ""
echo "🧪 Test User Credentials:"
echo "   Email: rental.manager@example.com"
echo "   Password: rental123"
echo ""
echo "🎯 What you'll see:"
echo "   - Only Stock and Accounting modules in sidebar"
echo "   - Rental Management as default home page"
echo "   - Quick access to Items, Invoices, Customers, Portal"
echo "   - No unnecessary modules or clutter"
echo ""
