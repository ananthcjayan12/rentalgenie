#!/bin/bash

echo "🎨 Blush & Glow Logo Installation"
echo "=================================="
echo ""

# Define paths
LOGO_SOURCE="$HOME/Desktop/blush_glow_logo.png"
LOGO_DEST="rental_management/public/images/blush_glow_logo.png"
LOGO_URL="https://imgur.com/your-uploaded-logo.png"

echo "This script will help you install the Blush & Glow logo for the desk."
echo ""
echo "Options:"
echo "1. Copy from Desktop (if you have the logo at ~/Desktop/blush_glow_logo.png)"
echo "2. Download from URL"
echo "3. Manual instructions"
echo ""

read -p "Select option (1-3): " choice

case $choice in
    1)
        if [ -f "$LOGO_SOURCE" ]; then
            echo "📁 Copying logo from Desktop..."
            mkdir -p rental_management/public/images
            cp "$LOGO_SOURCE" "$LOGO_DEST"
            echo "✅ Logo copied successfully!"
        else
            echo "❌ Logo not found at $LOGO_SOURCE"
            echo "Please place your logo file at ~/Desktop/blush_glow_logo.png and try again"
        fi
        ;;
    2)
        echo "📥 Downloading logo from URL..."
        read -p "Enter the logo URL: " url
        mkdir -p rental_management/public/images
        curl -L "$url" -o "$LOGO_DEST"
        if [ $? -eq 0 ]; then
            echo "✅ Logo downloaded successfully!"
        else
            echo "❌ Failed to download logo"
        fi
        ;;
    3)
        echo ""
        echo "📝 Manual Installation Instructions:"
        echo "===================================="
        echo ""
        echo "1. Save your Blush & Glow logo as a PNG file"
        echo "2. Copy it to: $LOGO_DEST"
        echo ""
        echo "Commands:"
        echo "  mkdir -p rental_management/public/images"
        echo "  cp /path/to/your/logo.png $LOGO_DEST"
        echo ""
        ;;
    *)
        echo "Invalid option selected"
        exit 1
        ;;
esac

echo ""
echo "📋 Next Steps After Logo Installation:"
echo "======================================"
echo "1. Restart your Frappe bench:"
echo "   bench restart"
echo ""
echo "2. Clear cache:"
echo "   bench clear-cache"
echo ""
echo "3. Build assets:"
echo "   bench build --app rental_management"
echo ""
echo "4. Refresh your browser (Ctrl+F5 or Cmd+Shift+R)"
echo ""
echo "The logo will appear in:"
echo "  - Navbar (top left)"
echo "  - Login page"
echo "  - Website header"
echo ""

# Check if logo exists
if [ -f "$LOGO_DEST" ]; then
    echo "✅ Logo file exists at: $LOGO_DEST"
    echo "📊 File info:"
    ls -lh "$LOGO_DEST"
    
    # Get image dimensions if imagemagick is installed
    if command -v identify &> /dev/null; then
        echo "📐 Image dimensions:"
        identify "$LOGO_DEST" | awk '{print $3}'
    fi
else
    echo "⚠️  Logo file not found at: $LOGO_DEST"
    echo "Please complete the installation steps above"
fi
