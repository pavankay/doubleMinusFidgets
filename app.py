from flask import Flask, render_template, jsonify, request
import random
import string
from datetime import datetime

app = Flask(__name__)


# Helper function to generate order IDs
def generate_order_id():
    letters = ''.join(random.choices(string.ascii_lowercase, k=4))
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"{letters}_{numbers}"


fidgets = [
    {
        "id": 1,
        "name": "Premium Spinner Pro",
        "price": 19.99,
        "description": "High-quality metal spinner with ultra-smooth bearings",
        "image": "https://placehold.co/400x400?text=Spinner+Pro"  # Using placeholder
    },
    {
        "id": 2,
        "name": "Infinity Cube Classic",
        "price": 14.99,
        "description": "Endless flipping satisfaction in your pocket",
        "image": "https://placehold.co/400x400?text=Infinity+Cube"  # Using placeholder
    },
    {
        "id": 3,
        "name": "Pop It Rainbow",
        "price": 9.99,
        "description": "Colorful bubble popping sensory toy",
        "image": "https://placehold.co/400x400?text=Pop+It"  # Using placeholder
    }
]

orders = {}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/shop')
def shop():
    return render_template('shop.html', fidgets=fidgets)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/cart')
def cart():
    # Cart page now relies on localStorage
    return render_template('cart.html')


@app.route('/product/<int:id>')
def product(id):
    fidget = next((item for item in fidgets if item["id"] == id), None)
    if fidget:
        return render_template('product.html', fidget=fidget)
    return render_template('404.html'), 404


@app.route('/admin')
def admin():
    # Convert orders dictionary to list and sort by date
    orders_list = sorted(
        orders.values(),
        key=lambda x: datetime.strptime(x['date'], '%B %d, %Y'),
        reverse=True
    )
    return render_template('admin.html', orders=orders_list)


# API endpoints
@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    return jsonify(fidgets)


@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    """Get a specific product"""
    product = next((item for item in fidgets if item["id"] == id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404


@app.route('/api/orders/create', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.json

        # Validate order data
        if not data or 'items' not in data:
            return jsonify({"error": "Invalid order data"}), 400

        # Create new order
        order_id = generate_order_id()
        new_order = {
            "id": order_id,
            "user_id": generate_order_id(),  # In a real app, this would be the actual user ID
            "date": datetime.now().strftime('%B %d, %Y'),
            "total": data.get('totalPrice', 0),
            "status": "Pending",
            "order_items": data.get('items', [])
        }

        # Store order
        orders[order_id] = new_order

        return jsonify({
            "success": True,
            "orderId": order_id,
            "message": "Order created successfully"
        })

    except Exception as e:
        return jsonify({
            "error": "Failed to create order",
            "message": str(e)
        }), 500


@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order"""
    if order_id in orders:
        return jsonify(orders[order_id])
    return jsonify({"error": "Order not found"}), 404


@app.route('/api/orders/<order_id>/complete', methods=['POST'])
def complete_order(order_id):
    """Mark an order as completed"""
    if order_id in orders:
        orders[order_id]['status'] = "Completed"
        return jsonify({
            "success": True,
            "message": "Order marked as completed"
        })
    return jsonify({"error": "Order not found"}), 404


@app.route('/order-confirmation/<order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    order = orders.get(order_id)
    if order:
        return render_template('order-confirmation.html', order=order)
    return render_template('404.html'), 404


# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.route('/favicon.ico')
def favicon():
    return '', 204


if __name__ == '__main__':
    app.run(debug=True)
