#!/bin/bash

echo "🔧 Rebuilding Rental Management App..."
echo "======================================"

cd /workspace/development/frappe-bench

echo ""
echo "1️⃣ Clearing all caches..."
bench clear-cache
bench clear-website-cache

echo ""
echo "2️⃣ Building assets..."
bench build --app rental_management

echo ""
echo "3️⃣ Restarting bench..."
bench restart

echo ""
echo "✅ Rebuild complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)"
echo "2. Clear browser cache completely"
echo "3. Check that unwanted modules are hidden"
echo ""
echo "🔍 To verify module visibility:"
echo "   - Check sidebar - should only show: Stock, Accounting, Home, Setup, Website, Rental Management"
echo "   - Unwanted modules (CRM, Projects, etc.) should be hidden"
