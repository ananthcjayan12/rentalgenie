#!/bin/bash

echo "🏠 Setting Portal as Home Page"
echo "=============================="

cd /workspace/development/frappe-bench

echo ""
echo "Step 1: Clear all caches..."
bench --site dev.localhost clear-cache
bench --site dev.localhost clear-website-cache

echo ""
echo "Step 2: Restart bench to apply home page changes..."
bench restart

echo ""
echo "✅ Done!"
echo ""
echo "📌 Now test the URLs:"
echo "1. Root URL: http://dev.localhost:8800/ → Should redirect to portal"
echo "2. Desk URL: http://dev.localhost:8800/app → Should show workspaces/desk"
echo "3. Direct Portal: http://dev.localhost:8800/portal → Should show portal directly"
echo ""
echo "If you want desk users to login, they can still access:"
echo "  - http://dev.localhost:8800/app"
echo "  - Or click 'Login' from the portal header"