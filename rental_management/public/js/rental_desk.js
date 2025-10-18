/**
 * Rental Management Desk Customizations
 * Hides unnecessary modules and shows only rental-related items
 */

frappe.provide('rental_management');

// Customize workspace/desk after page load
$(document).ready(function() {
    // Hide unwanted modules from the sidebar
    setTimeout(function() {
        customizeModuleSidebar();
        customizeLogo();
    }, 1000);
});

// Also run on page change
frappe.router.on('change', function() {
    setTimeout(function() {
        customizeModuleSidebar();
    }, 500);
});

function customizeModuleSidebar() {
    // List of modules/doctypes to HIDE
    const modulesToHide = [
        // Core modules to hide
        'CRM',
        'Projects',
        'Support',
        'Quality',
        'Manufacturing',
        'Buying',
        'Selling',
        'HR',
        'Payroll',
        'Assets',
        'Loan Management',
        'Healthcare',
        'Education',
        'Agriculture',
        'Non Profit',
        'Hospitality',
        'Utilities',
        'Email',
        'Website',
        'Integrations',
        'Customize',
        'Settings',
        
        // Specific doctypes to hide from sidebar
        'Lead',
        'Opportunity',
        'Quotation',
        'Sales Order',
        'Delivery Note',
        'Purchase Order',
        'Purchase Receipt',
        'Supplier',
        'Supplier Quotation',
        'Material Request',
        'Stock Entry',
        'Employee',
        'Salary Slip',
        'Leave Application',
        'Attendance',
        'Asset',
        'Task',
        'Project',
        'Issue',
        'Timesheet',
        'Contract'
    ];
    
    // Hide modules from sidebar
    modulesToHide.forEach(function(module) {
        // Try different selectors for modules
        $(`.standard-sidebar-item:contains("${module}")`).hide();
        $(`.desk-sidebar-item:contains("${module}")`).hide();
        $(`.module-link:contains("${module}")`).hide();
        $(`a[data-name="${module}"]`).closest('li').hide();
        $(`a[href*="${module.toLowerCase().replace(' ', '-')}"]`).closest('li').hide();
    });
    
    // Show only rental-related modules
    showOnlyRentalModules();
}

function showOnlyRentalModules() {
    // List of modules/doctypes to SHOW (rental-related)
    const modulesToShow = [
        // Core rental modules
        'Home',
        'Accounting',
        'Stock',
        
        // Rental-specific
        'Item',
        'Item Group',
        'Customer',
        'Sales Invoice',
        'Payment Entry',
        'Journal Entry',
        'Rental Cart',
        'Rental Cart Item',
        'Portal Banner',
        'Portal Category',
        'Third Party Owner',
        
        // Accounting reports
        'Accounts',
        'General Ledger',
        'Profit and Loss Statement',
        'Balance Sheet',
        'Cash Flow',
        'Trial Balance',
        
        // Stock reports
        'Stock Balance',
        'Stock Ledger',
        'Warehouse',
        
        // System
        'User',
        'Role',
        'Print Format',
        'Dashboard'
    ];
    
    // This is handled by hiding unwanted modules above
    // The remaining visible items will be the rental-related ones
}

function customizeLogo() {
    // Replace ERPNext logo with Blush & Glow logo
    const logoUrl = '/assets/rental_management/images/blush_glow_logo.png';
    
    // Update navbar brand logo
    $('.navbar-brand img, .app-logo img').attr('src', logoUrl);
    
    // Update sidebar logo if exists
    $('.sidebar-brand img').attr('src', logoUrl);
    
    // Update favicon
    $('link[rel="icon"]').attr('href', logoUrl);
    $('link[rel="shortcut icon"]').attr('href', logoUrl);
    
    // Update page title
    if (document.title.includes('ERPNext')) {
        document.title = document.title.replace('ERPNext', 'Blush & Glow - Rental Management');
    }
}

// Override default workspace/module cards to show only rental modules
frappe.provide('frappe.boot');

// Customize workspace page
frappe.pages['Workspaces'].on_page_load = function(wrapper) {
    const rentalWorkspaces = [
        'Home',
        'Rental Management',
        'Accounting',
        'Stock',
        'Inventory'
    ];
    
    // Filter workspace cards
    setTimeout(function() {
        $('.workspace-card').each(function() {
            const workspaceName = $(this).find('.workspace-card-title').text().trim();
            if (!rentalWorkspaces.includes(workspaceName)) {
                $(this).hide();
            }
        });
    }, 500);
};

// Custom desk shortcuts for rental
rental_management.setup_shortcuts = function() {
    const shortcuts = [
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
    
    return shortcuts;
};

// Hide unnecessary menu items from navbar
frappe.ui.toolbar.Toolbar = class extends frappe.ui.toolbar.Toolbar {
    make() {
        super.make();
        this.hide_unwanted_menu_items();
    }
    
    hide_unwanted_menu_items() {
        // Hide items from the navbar dropdown menus
        const itemsToHide = [
            'Marketplace',
            'ERPNext Settings',
            'Setup',
            'Integrations'
        ];
        
        itemsToHide.forEach(function(item) {
            $(`.dropdown-item:contains("${item}")`).hide();
        });
    }
};

console.log('✅ Blush & Glow Rental Management Desk Customizations Loaded');
