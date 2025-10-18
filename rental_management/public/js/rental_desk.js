/**
 * Blush & Glow - Rental Management Desk Customizations
 * Handles logo and branding customizations only
 * Module hiding is handled by install.py
 */

frappe.provide('rental_management');

// Initialize customizations after frappe is ready
frappe.ready(function() {
    console.log('🎨 Initializing Blush & Glow Branding...');
    
    // Apply customizations with delay to ensure DOM is ready
    setTimeout(function() {
        try {
            customizeLogo();
            updateBranding();
            console.log('✅ Branding applied successfully');
        } catch (error) {
            console.error('❌ Error applying branding:', error);
        }
    }, 1000);
});

// Also update branding on route changes
if (frappe.router) {
    frappe.router.on('change', function() {
        setTimeout(function() {
            try {
                customizeLogo();
                updateBranding();
            } catch (error) {
                console.error('❌ Error on route change:', error);
            }
        }, 300);
    });
}

function customizeLogo() {
    try {
        // Replace ERPNext logo with Blush & Glow logo
        const logoUrl = '/assets/rental_management/images/blush_glow_logo.png';
        
        // Check if logo exists before applying
        const img = new Image();
        img.onload = function() {
            try {
                // Logo exists, update all logo instances
                $('.navbar-brand img, .app-logo img').attr('src', logoUrl);
                $('.sidebar-brand img').attr('src', logoUrl);
                $('link[rel="icon"]').attr('href', logoUrl);
                $('link[rel="shortcut icon"]').attr('href', logoUrl);
                console.log('✅ Blush & Glow logo applied');
            } catch (e) {
                console.error('Error applying logo:', e);
            }
        };
        img.onerror = function() {
            console.log('⚠️ Logo not found. Please upload to: rental_management/public/images/blush_glow_logo.png');
        };
        img.src = logoUrl;
    } catch (error) {
        console.error('❌ Error customizing logo:', error);
    }
}

function updateBranding() {
    try {
        // Update page title
        if (document.title && document.title.includes('ERPNext')) {
            document.title = document.title.replace('ERPNext', 'Blush & Glow');
        }
        
        // Update brand text in navbar
        if ($('.navbar-brand .navbar-brand-text').length) {
            $('.navbar-brand .navbar-brand-text').text('Blush & Glow');
        }
        
        // Update app name in sidebar
        if ($('.app-name').length) {
            $('.app-name').text('Blush & Glow');
        }
    } catch (error) {
        console.error('❌ Error updating branding:', error);
    }
}

// Custom desk shortcuts for rental (can be used by other modules)
rental_management.setup_shortcuts = function() {
    return [
        {
            label: 'New Rental Item',
            type: 'Item',
            icon: 'fa fa-tag'
        },
        {
            label: 'New Customer',
            type: 'Customer',
            icon: 'fa fa-user'
        },
        {
            label: 'Create Invoice',
            type: 'Sales Invoice',
            icon: 'fa fa-file-invoice'
        },
        {
            label: 'Payment Entry',
            type: 'Payment Entry',
            icon: 'fa fa-money-bill'
        },
        {
            label: 'Portal Management',
            url: '/app/portal-banner',
            icon: 'fa fa-image'
        },
        {
            label: 'Customer Portal',
            url: '/portal',
            icon: 'fa fa-globe'
        }
    ];
};

console.log('✅ Blush & Glow Rental Management Branding Loaded');
