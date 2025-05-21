// cart.js

class CartManager {
    constructor() {
        this.STORAGE_KEY = 'dmf_cart';  // dmf = Double Minus Fidgets
        this.cart = this.loadCart();
        this.bindEvents();
        this.updateCartDisplay();
    }

    getCart() {
        return this.cart;
    }

    loadCart() {
        const savedCart = localStorage.getItem(this.STORAGE_KEY);
        return savedCart ? JSON.parse(savedCart) : {
            items: [],
            totalPrice: 0
        };
    }

    saveCart() {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.cart));
        this.updateCartDisplay();
    }

    calculateTotal() {
        this.cart.totalPrice = this.cart.items.reduce((sum, item) =>
            sum + (item.price * item.quantity), 0);
        return this.cart.totalPrice;
    }

    findItemIndex(productId) {
        return this.cart.items.findIndex(item => item.id === productId);
    }

    addToCart(product, quantity = 1) {
        const itemIndex = this.findItemIndex(product.id);

        if (itemIndex > -1) {
            // Item exists, update quantity
            this.cart.items[itemIndex].quantity += quantity;
        } else {
            // Add new item
            this.cart.items.push({
                id: product.id,
                name: product.name,
                price: product.price,
                quantity: quantity,
                image: product.image
            });
        }

        this.calculateTotal();
        this.saveCart();
        this.showNotification('Item added to cart');
    }

    updateQuantity(productId, newQuantity) {
        const itemIndex = this.findItemIndex(productId);

        if (itemIndex > -1) {
            if (newQuantity > 0) {
                this.cart.items[itemIndex].quantity = newQuantity;
            } else {
                this.removeItem(productId);
                return;
            }

            this.calculateTotal();
            this.saveCart();
        }
    }

    removeItem(productId) {
        const itemIndex = this.findItemIndex(productId);

        if (itemIndex > -1) {
            this.cart.items.splice(itemIndex, 1);
            this.calculateTotal();
            this.saveCart();
            this.showNotification('Item removed from cart');
        }
    }

    clearCart() {
        this.cart.items = [];
        this.cart.totalPrice = 0;
        this.saveCart();
    }

    updateCartDisplay() {
        // Update cart count in header
        const cartCount = document.querySelector('.cart-count');
        if (cartCount) {
            const totalItems = this.cart.items.reduce((sum, item) => sum + item.quantity, 0);
            cartCount.textContent = totalItems;
        }

        // Update cart page if we're on it
        const cartContainer = document.querySelector('.cart-items');
        if (cartContainer) {
            if (this.cart.items.length === 0) {
                document.querySelector('.cart-container').innerHTML = `
                    <h1>Shopping Cart</h1>
                    <div class="empty-cart">
                        <p>Your cart is empty</p>
                        <a href="/shop" class="btn-primary">Continue Shopping</a>
                    </div>
                `;
                return;
            }

            cartContainer.innerHTML = this.cart.items.map(item => this.generateCartItemHtml(item)).join('');

            // Update total
            const cartTotal = document.querySelector('.cart-total');
            if (cartTotal) {
                cartTotal.textContent = `$${this.cart.totalPrice.toFixed(2)}`;
            }

            // Rebind events for new elements
            this.bindCartItemEvents();
        }
    }

    generateCartItemHtml(item) {
        return `
            <div class="cart-item" data-product-id="${item.id}">
                <div class="cart-item-image">
                    <img src="${item.image}" alt="${item.name}">
                </div>
                <div class="cart-item-details">
                    <h3>${item.name}</h3>
                    <p class="price">$${item.price.toFixed(2)}</p>
                    <div class="quantity-controls">
                        <button class="quantity-update" data-product-id="${item.id}" data-change="-1">-</button>
                        <span class="quantity">${item.quantity}</span>
                        <button class="quantity-update" data-product-id="${item.id}" data-change="1">+</button>
                    </div>
                    <p class="item-total">Total: $${(item.price * item.quantity).toFixed(2)}</p>
                </div>
                <button class="remove-item" data-product-id="${item.id}">&times;</button>
            </div>
        `;
    }

    bindEvents() {
        // Add to cart buttons on product pages
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = parseInt(e.target.dataset.productId);
                const product = this.getProductDetails(productId);
                if (product) {
                    this.addToCart(product);
                }
            });
        });

        // Bind events for cart items if we're on the cart page
        this.bindCartItemEvents();
    }

    bindCartItemEvents() {
        // Quantity update buttons
        document.querySelectorAll('.quantity-update').forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = parseInt(e.target.dataset.productId);
                const change = parseInt(e.target.dataset.change);
                const currentQty = parseInt(e.target.closest('.cart-item')
                    .querySelector('.quantity').textContent);
                this.updateQuantity(productId, currentQty + change);
            });
        });

        // Remove buttons
        document.querySelectorAll('.remove-item').forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = parseInt(e.target.dataset.productId);
                this.removeItem(productId);
            });
        });
    }

    getProductDetails(productId) {
        // This should match your product data structure
        const products = [
            {
                id: 1,
                name: "Premium Spinner Pro",
                price: 19.99,
                image: "/static/images/spinner.jpg"
            },
            {
                id: 2,
                name: "Infinity Cube Classic",
                price: 14.99,
                image: "/static/images/cube.jpg"
            },
            {
                id: 3,
                name: "Pop It Rainbow",
                price: 9.99,
                image: "/static/images/popit.jpg"
            }
        ];

        return products.find(p => p.id === productId);
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Checkout process
    async checkout() {
        try {
            // Prepare order data
            const orderData = {
                items: this.cart.items,
                totalPrice: this.cart.totalPrice
            };

            // Send order to server
            const response = await fetch('/api/orders/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(orderData)
            });

            if (!response.ok) throw new Error('Checkout failed');

            const result = await response.json();

            // Clear cart after successful checkout
            this.clearCart();

            // Show success message
            this.showNotification('Order placed successfully!');

            // Redirect to order confirmation page
            window.location.href = `/order-confirmation/${result.orderId}`;

        } catch (error) {
            this.showNotification('Checkout failed. Please try again.', 'error');
            console.error('Checkout error:', error);
        }
    }
}

// Initialize cart manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cartManager = new CartManager();
});