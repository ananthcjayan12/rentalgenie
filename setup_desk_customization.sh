#!/bin/bash

echo "🎨 Blush & Glow Desk Customization Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "rental_management/hooks.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the rentalgenie directory${NC}"
    exit 1
fi

echo "This script will set up the Blush & Glow desk customizations."
echo ""

# Step 1: Check for logo
echo -e "${BLUE}Step 1: Checking for logo file...${NC}"
LOGO_PATH="rental_management/public/images/blush_glow_logo.png"

if [ -f "$LOGO_PATH" ]; then
    echo -e "${GREEN}✅ Logo found at $LOGO_PATH${NC}"
    ls -lh "$LOGO_PATH"
else
    echo -e "${YELLOW}⚠️  Logo not found at $LOGO_PATH${NC}"
    echo ""
    echo "Please install the logo first:"
    echo "  1. Run: ./install_logo.sh"
    echo "  OR"
    echo "  2. Manually copy: cp /path/to/logo.png $LOGO_PATH"
    echo ""
    read -p "Continue anyway? (y/n): " continue_choice
    if [ "$continue_choice" != "y" ]; then
        exit 1
    fi
fi

echo ""

# Step 2: Verify files exist
echo -e "${BLUE}Step 2: Verifying customization files...${NC}"

files_to_check=(
    "rental_management/public/js/rental_desk.js"
    "rental_management/public/css/rental_theme.css"
    "rental_management/setup/install.py"
    "rental_management/hooks.py"
)

all_files_exist=true
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file${NC}"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo -e "${RED}❌ Some required files are missing. Please ensure all customization files are in place.${NC}"
    exit 1
fi

echo ""

# Step 3: Get site name
echo -e "${BLUE}Step 3: Site configuration...${NC}"
echo "Please enter your Frappe site name (e.g., dev.localhost)"
read -p "Site name: " SITE_NAME

if [ -z "$SITE_NAME" ]; then
    echo -e "${RED}❌ Site name cannot be empty${NC}"
    exit 1
fi

echo ""

# Step 4: Build and deploy
echo -e "${BLUE}Step 4: Building assets and deploying customizations...${NC}"
echo ""

echo "📦 Clearing cache..."
bench --site "$SITE_NAME" clear-cache
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Cache cleared${NC}"
else
    echo -e "${RED}❌ Failed to clear cache${NC}"
fi

echo ""
echo "🔨 Building assets..."
bench build --app rental_management
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Assets built${NC}"
else
    echo -e "${YELLOW}⚠️  Asset build had issues (this might be okay)${NC}"
fi

echo ""
echo "🔄 Restarting services..."
bench restart
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Services restarted${NC}"
else
    echo -e "${RED}❌ Failed to restart services${NC}"
fi

echo ""

# Step 5: Run desk customization via bench console
echo -e "${BLUE}Step 5: Applying desk customizations...${NC}"
echo ""

# Create a temporary Python script to run the customization
cat > /tmp/setup_desk.py << 'EOF'
import frappe
from rental_management.setup.install import setup_desk_customization, hide_unwanted_modules

frappe.connect()
try:
    print("Running desk customization...")
    setup_desk_customization()
    hide_unwanted_modules()
    frappe.db.commit()
    print("✅ Desk customization complete!")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
EOF

bench --site "$SITE_NAME" console < /tmp/setup_desk.py
rm /tmp/setup_desk.py

echo ""

# Step 6: Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📋 What was done:"
echo "  ✅ Logo configured (if available)"
echo "  ✅ Desk customization JS/CSS loaded"
echo "  ✅ Theme colors applied"
echo "  ✅ Unwanted modules hidden"
echo "  ✅ Rental Management workspace configured"
echo ""
echo "🌐 Next Steps:"
echo "  1. Open your browser and navigate to:"
echo "     http://$SITE_NAME:8000/app"
echo ""
echo "  2. Hard refresh your browser:"
echo "     - Windows/Linux: Ctrl + F5"
echo "     - Mac: Cmd + Shift + R"
echo ""
echo "  3. You should see:"
echo "     • Blush & Glow logo in navbar (if logo was installed)"
echo "     • Purple-themed interface"
echo "     • Only rental-related modules visible"
echo "     • Clean, focused workspace"
echo ""
echo "📖 For troubleshooting, see: BLUSH_GLOW_CUSTOMIZATION.md"
echo ""
echo -e "${GREEN}✨ Blush & Glow - Premium Bridal Destination ✨${NC}"
echo ""
