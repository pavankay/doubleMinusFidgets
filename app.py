from flask import Flask, render_template, jsonify, request
import random
import string

app = Flask(__name__)


# Helper function to generate order IDs
def generate_order_id():
    letters = ''.join(random.choices(string.ascii_lowercase, k=4))
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"{letters}_{numbers}"


# Sample fidget data
fidgets = [
    {
        "id": 1,
        "name": "Premium Spinner Pro",
        "price": 19.99,
        "description": "High-quality metal spinner with ultra-smooth bearings",
        "image": "/static/images/spinner.jpg"
    },
    {
        "id": 2,
        "name": "Infinity Cube Classic",
        "price": 14.99,
        "description": "Endless flipping satisfaction in your pocket",
        "image": "/static/images/cube.jpg"
    },
    {
        "id": 3,
        "name": "Pop It Rainbow",
        "price": 9.99,
        "description": "Colorful bubble popping sensory toy",
        "image": "/static/images/popit.jpg"
    }
]

# Orders data
orders = [
    {
        "id": "abcd_1234",
        "user_id": "abcd_1234",
        "date": "March 3, 2024",
        "total": 54.97,
        "status": "Pending",
        "order_items": [
            {
                "name": "Premium Spinner Pro",
                "quantity": 2,
                "price": 19.99
            },
            {
                "name": "Infinity Cube Classic",
                "quantity": 1,
                "price": 14.99
            }
        ]
    },
    {
        "id": "efgh_5678",
        "user_id": "efgh_5678",
        "date": "March 2, 2024",
        "total": 29.97,
        "status": "Completed",
        "order_items": [
            {
                "name": "Pop It Rainbow",
                "quantity": 3,
                "price": 9.99
            }
        ]
    }
]

# Shopping cart data
cart_items = []


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
    cart_total = sum(item.get('price', 0) * item.get('quantity', 0) for item in cart_items)
    return render_template('cart.html', items=cart_items, total=cart_total)


@app.route('/product/<int:id>')
def product(id):
    fidget = next((item for item in fidgets if item["id"] == id), None)
    return render_template('product.html', fidget=fidget)


@app.route('/admin')
def admin():
    pending_orders = [order for order in orders if order['status'] == 'Pending']
    completed_orders = [order for order in orders if order['status'] == 'Completed']
    return render_template('admin.html', orders=orders)


# Shopping Cart Functions
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    product_id = data.get('product_id')

    fidget = next((item for item in fidgets if item["id"] == product_id), None)
    if fidget:
        cart_item = next((item for item in cart_items if item["id"] == product_id), None)
        if cart_item:
            cart_item["quantity"] += 1
        else:
            cart_items.append({
                "id": fidget["id"],
                "name": fidget["name"],
                "price": fidget["price"],
                "quantity": 1
            })
        return jsonify({"success": True, "cart_count": len(cart_items)})
    return jsonify({"success": False})


@app.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    cart_item = next((item for item in cart_items if item["id"] == product_id), None)
    if cart_item:
        if quantity > 0:
            cart_item["quantity"] = quantity
        else:
            cart_items.remove(cart_item)
        return jsonify({"success": True, "cart_count": len(cart_items)})
    return jsonify({"success": False})


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.json
    product_id = data.get('product_id')

    cart_item = next((item for item in cart_items if item["id"] == product_id), None)
    if cart_item:
        cart_items.remove(cart_item)
        return jsonify({"success": True, "cart_count": len(cart_items)})
    return jsonify({"success": False})


@app.route('/complete_order/<order_id>', methods=['POST'])
def complete_order(order_id):
    order = next((order for order in orders if order['id'] == order_id), None)
    if order:
        order['status'] = "Completed"
        return jsonify({"success": True})
    return jsonify({"success": False}), 404


@app.route('/checkout', methods=['POST'])
def checkout():
    if not cart_items:
        return jsonify({"success": False, "message": "Cart is empty"}), 400

    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in cart_items)

    # Create new order
    new_order = {
        "id": generate_order_id(),
        "user_id": generate_order_id(),  # In a real app, this would be the actual user ID
        "date": "March 3, 2024",  # In a real app, use actual date
        "total": total,
        "status": "Pending",
        "order_items": [
            {
                "name": item['name'],
                "quantity": item['quantity'],
                "price": item['price']
            } for item in cart_items
        ]
    }

    # Add order to orders list
    orders.append(new_order)

    # Clear cart
    cart_items.clear()

    return jsonify({"success": True, "order_id": new_order['id']})


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