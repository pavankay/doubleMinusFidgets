from flask import Flask, render_template

app = Flask(__name__)

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
    return render_template('cart.html')

@app.route('/product/<int:id>')
def product(id):
    fidget = next((item for item in fidgets if item["id"] == id), None)
    return render_template('product.html', fidget=fidget)

if __name__ == '__main__':
    app.run(debug=True)