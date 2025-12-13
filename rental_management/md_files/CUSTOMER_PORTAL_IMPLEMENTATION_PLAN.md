# Customer Portal Implementation Plan

## 📱 Overview
Implementation plan for customer-facing rental platform based on Figma designs. This will be a web-based portal that customers can access to browse, book, and manage rental items.

## 🎯 Architecture Approach

### **Option 1: Frappe Web Portal (Recommended)**
- Use Frappe's built-in web portal functionality
- Leverage existing ERPNext user management
- Server-side rendered pages with modern JS enhancements
- Direct integration with existing doctypes

### **Option 2: Separate Frontend (Alternative)**
- React/Vue.js frontend application
- REST API backend using Frappe's API framework
- More flexibility but requires additional infrastructure

**Recommendation: Go with Option 1 for faster development and better integration**

## 🔧 Technical Implementation

### **Phase 1: Backend API Enhancements (1-2 weeks)**

#### 1.1 Create Customer Portal APIs
```python
# Location: rental_management/api/customer_portal.py

@frappe.whitelist(allow_guest=True)
def get_rental_items(category=None, filters=None, page=1, limit=20):
    """Get rental items for customer portal"""
    
@frappe.whitelist()
def add_to_cart(item_code, rental_dates, customer=None):
    """Add item to customer's cart"""
    
@frappe.whitelist()
def get_cart_items(customer):
    """Get customer's cart items"""
    
@frappe.whitelist()
def create_booking_from_cart(customer, delivery_details):
    """Create booking and sales invoice from cart"""
    
@frappe.whitelist()
def get_customer_bookings(customer):
    """Get customer's booking history"""
    
@frappe.whitelist()
def check_item_availability(item_code, start_date, end_date):
    """Check if item is available for rental period"""
```

#### 1.2 Enhance Item Doctype for Portal
```python
# Add portal-specific fields to Item
portal_fields = [
    "portal_image_gallery",  # Multiple images
    "portal_description",    # Rich text for portal
    "size_chart",           # Size information
    "care_instructions",    # Care details
    "portal_tags",          # Searchable tags
    "portal_category",      # Portal-specific categorization
    "rental_policies",      # Terms and conditions
    "discount_percentage",  # Current discount
    "is_trending",          # Featured/trending flag
    "reviews_rating",       # Average rating
    "reviews_count"         # Number of reviews
]
```

#### 1.3 Create Cart Management System
```python
# Location: rental_management/doctype/rental_cart/rental_cart.py

class RentalCart(Document):
    """Shopping cart for rental items"""
    # Fields: customer, items (table), session_id, created_date
    
    def add_item(self, item_code, rental_start, rental_end, quantity=1):
        """Add item to cart with availability check"""
        
    def remove_item(self, item_code):
        """Remove item from cart"""
        
    def calculate_total(self):
        """Calculate cart total with discounts"""
        
    def convert_to_booking(self, delivery_details):
        """Convert cart to Sales Invoice"""
```

### **Phase 2: Frontend Portal Development (2-3 weeks)**

#### 2.1 Portal Structure
```
rental_management/
└── www/
    └── portal/
        ├── index.html          # Home page
        ├── category.html       # Category listing
        ├── item.html          # Item detail page
        ├── cart.html          # Shopping cart
        ├── checkout.html      # Booking creation
        ├── bookings.html      # Booking history
        ├── profile.html       # Customer profile
        └── assets/
            ├── css/
            ├── js/
            └── images/
```

#### 2.2 Modern Frontend Framework
```html
<!-- Use Frappe's web framework with modern enhancements -->
<!-- Base template: rental_management/www/portal/base.html -->

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blush & Glow - Rental Portal</title>
    
    <!-- Frappe CSS/JS -->
    {{ include_style("assets/frappe/css/web.css") }}
    
    <!-- Custom Portal CSS -->
    {{ include_style("assets/rental_management/css/portal.css") }}
    
    <!-- Modern Framework (Alpine.js for reactivity) -->
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body>
    {% include "rental_management/www/portal/includes/navbar.html" %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    {% include "rental_management/www/portal/includes/footer.html" %}
    
    {{ include_script("assets/rental_management/js/portal.js") }}
</body>
</html>
```

### **Phase 3: Screen-by-Screen Implementation**

#### 3.1 Home Screen (`/portal/`)
```python
# rental_management/www/portal/index.py
def get_context(context):
    context.categories = get_rental_categories()
    context.trending_items = get_trending_items(limit=6)
    context.featured_collections = get_featured_collections()
    context.discounts = get_current_discounts()
    return context
```

```html
<!-- rental_management/www/portal/index.html -->
{% extends "rental_management/www/portal/base.html" %}

{% block content %}
<div x-data="homePageData()">
    <!-- Hero Section -->
    <section class="hero-section">
        <div class="search-container">
            <input type="text" placeholder="Search for jewellery" 
                   x-model="searchQuery" @input="searchItems()">
        </div>
    </section>
    
    <!-- Categories -->
    <section class="categories">
        <div class="category-grid">
            {% for category in categories %}
            <div class="category-card" @click="goToCategory('{{ category.name }}')">
                <img src="{{ category.image }}" alt="{{ category.label }}">
                <h3>{{ category.label }}</h3>
            </div>
            {% endfor %}
        </div>
    </section>
    
    <!-- Trending Items -->
    <section class="trending-section">
        <h2>Trending Item</h2>
        <div class="items-grid">
            {% for item in trending_items %}
            {% include "rental_management/www/portal/includes/item_card.html" %}
            {% endfor %}
        </div>
    </section>
</div>
{% endblock %}
```

#### 3.2 Product Listing (`/portal/category/`)
```python
# rental_management/www/portal/category/index.py
def get_context(context):
    category = frappe.form_dict.get('category')
    filters = frappe.form_dict.get('filters', {})
    
    context.items = get_rental_items(
        category=category,
        filters=filters,
        page=frappe.form_dict.get('page', 1)
    )
    context.category = category
    context.filters = get_available_filters(category)
    return context
```

#### 3.3 Product Detail (`/portal/item/`)
```python
# rental_management/www/portal/item/index.py
def get_context(context):
    item_code = frappe.form_dict.get('item')
    context.item = frappe.get_doc("Item", item_code)
    context.related_items = get_related_items(item_code)
    context.reviews = get_item_reviews(item_code)
    context.size_chart = get_size_chart(item_code)
    return context
```

#### 3.4 Shopping Cart (`/portal/cart/`)
```javascript
// Alpine.js component for cart management
function cartData() {
    return {
        items: [],
        total: 0,
        
        async loadCart() {
            const response = await frappe.call({
                method: 'rental_management.api.customer_portal.get_cart_items',
                args: { customer: frappe.session.user }
            });
            this.items = response.message;
            this.calculateTotal();
        },
        
        async updateQuantity(itemCode, quantity) {
            await frappe.call({
                method: 'rental_management.api.customer_portal.update_cart_quantity',
                args: { item_code: itemCode, quantity: quantity }
            });
            this.loadCart();
        },
        
        async removeItem(itemCode) {
            await frappe.call({
                method: 'rental_management.api.customer_portal.remove_from_cart',
                args: { item_code: itemCode }
            });
            this.loadCart();
        }
    }
}
```

### **Phase 4: Integration with Existing Backend (1 week)**

#### 4.1 Enhance Sales Invoice Creation
```python
# Modify rental_management/automations/booking_automation.py

@frappe.whitelist()
def create_booking_from_portal(cart_data, customer_details, rental_dates):
    """Create Sales Invoice from portal cart"""
    
    # Validate items availability
    for item in cart_data:
        if not check_item_availability(item['item_code'], 
                                     rental_dates['start'], 
                                     rental_dates['end']):
            frappe.throw(f"Item {item['item_code']} not available")
    
    # Create Sales Invoice
    doc = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": customer_details['customer'],
        "is_rental_booking": 1,
        "function_date": rental_dates['function_date'],
        "rental_duration_days": rental_dates['duration'],
        "delivery_address": customer_details['address'],
        "items": [
            {
                "item_code": item['service_item_code'],  # Use rental service item
                "qty": item['quantity'],
                "rate": item['rate']
            } for item in cart_data
        ]
    })
    
    doc.insert()
    doc.submit()
    
    # Clear cart
    clear_customer_cart(customer_details['customer'])
    
    return doc.name
```

#### 4.2 Customer Authentication
```python
# Portal login/registration integration
@frappe.whitelist(allow_guest=True)
def portal_login(mobile_number, otp=None):
    """Login/Register customer via mobile OTP"""
    
@frappe.whitelist()
def send_otp(mobile_number):
    """Send OTP for login"""
    
@frappe.whitelist()
def verify_otp(mobile_number, otp):
    """Verify OTP and create session"""
```

### **Phase 5: UI/UX Implementation (2 weeks)**

#### 5.1 Responsive Design System
```css
/* rental_management/public/css/portal.css */

:root {
    --primary-color: #7B2CBF;    /* Purple from design */
    --secondary-color: #FF6B6B;  /* Accent color */
    --background: #F8F9FA;
    --text-primary: #2C3E50;
    --text-secondary: #7F8C8D;
}

.category-card {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.category-card:hover {
    transform: translateY(-4px);
}

.item-card {
    background: white;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.price-tag {
    font-weight: 600;
    color: var(--primary-color);
}

.discount-badge {
    background: #10B981;
    color: white;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 12px;
}

/* Mobile-first responsive design */
@media (max-width: 768px) {
    .category-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
    }
    
    .items-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
}
```

#### 5.2 Interactive Components
```javascript
// rental_management/public/js/portal.js

class RentalPortal {
    constructor() {
        this.cart = new CartManager();
        this.booking = new BookingManager();
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadUserData();
    }
    
    setupEventListeners() {
        // Add to cart buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-cart-btn')) {
                this.handleAddToCart(e);
            }
        });
    }
    
    async handleAddToCart(event) {
        const itemCode = event.target.dataset.itemCode;
        const rentalDates = this.getSelectedDates();
        
        try {
            await this.cart.addItem(itemCode, rentalDates);
            this.showSuccess('Item added to cart!');
            this.updateCartCounter();
        } catch (error) {
            this.showError(error.message);
        }
    }
}

// Initialize portal
document.addEventListener('DOMContentLoaded', () => {
    new RentalPortal();
});
```

## 📅 **Implementation Timeline**

### **Week 1-2: Backend Foundation**
- [ ] Create Customer Portal APIs
- [ ] Enhance Item doctype for portal
- [ ] Implement Cart management system
- [ ] Set up authentication system

### **Week 3-4: Frontend Development**
- [ ] Create base portal templates
- [ ] Implement home screen
- [ ] Build product listing page
- [ ] Develop product detail page

### **Week 5-6: Advanced Features**
- [ ] Shopping cart functionality
- [ ] Checkout/booking process
- [ ] Customer booking history
- [ ] Profile management

### **Week 7: Integration & Testing**
- [ ] Connect frontend with existing backend
- [ ] Test complete booking flow
- [ ] Mobile responsiveness testing
- [ ] Performance optimization

### **Week 8: Deployment & Polish**
- [ ] Production deployment
- [ ] User acceptance testing
- [ ] Bug fixes and refinements
- [ ] Documentation

## 🔗 **Integration Points**

### **With Existing System:**
1. **Item Management** → Portal displays rental items
2. **Customer Management** → Portal user registration/login
3. **Sales Invoice** → Portal booking creation
4. **Booking Automation** → Availability checking
5. **Commission System** → Third-party item handling

### **New Components:**
1. **Rental Cart** → Shopping cart management
2. **Portal APIs** → Customer-facing endpoints
3. **Web Templates** → Portal UI pages
4. **Authentication** → Mobile OTP system
5. **Image Gallery** → Product photos management

## 🎯 **Success Metrics**

- **User Experience**: Mobile-responsive, fast loading
- **Functionality**: Complete booking flow from browse to payment
- **Integration**: Seamless with existing ERPNext backend
- **Performance**: < 3 second page loads
- **Security**: Proper authentication and data protection

## 🚀 **Getting Started**

1. **Create Portal Structure**: Set up www folder and base templates
2. **API Development**: Build customer portal APIs
3. **Database Schema**: Add portal-specific fields to existing doctypes
4. **Frontend Implementation**: Build screens one by one
5. **Testing**: End-to-end testing of booking flow

Would you like me to start with any specific phase or component?
