import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

# Initialize the cart list
cart = []

# Load the product_list from the JSON file (or initialize if the file doesn't exist)
try:
    with open('product_list.json', 'r') as product_file:
        product_list = json.load(product_file)
except FileNotFoundError:
    product_list = [
        {"prod_name": "Eggs", "prod_price": 7.95, "quantity": 250},
        {"prod_name": "Milk", "prod_price": 3.75, "quantity": 120},
        {"prod_name": "Cheese", "prod_price": 7.95, "quantity": 175},
        {"prod_name": "Coffee", "prod_price": 5.25, "quantity": 350},
        {"prod_name": "Bread", "prod_price": 2.45, "quantity": 150}
    ]

links = [
    {"prod_name": "Cart", "url": "/cart"},
]

# Configure the logging settings
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/')
def homepage():
    logging.info('Accessed homepage')
    return render_template('index.html', links=links, product_list=product_list)

@app.route('/about')
def about():
    logging.info('Accessed about page')
    return render_template('about.html')

@app.route('/cart', methods=['GET', 'POST'])
def view_cart():
    global cart

    if request.method == 'POST':
        selected_product_name = request.form.get('product_name')
        selected_product_quantity = int(request.form.get('quantity', 1))

        selected_product = next((product for product in product_list if product['prod_name'] == selected_product_name), None)
        if selected_product and selected_product['quantity'] >= selected_product_quantity:
            cart_item = next((item for item in cart if item['prod_name'] == selected_product_name), None)
            if cart_item:
                if cart_item['cart_quantity'] + selected_product_quantity <= selected_product['quantity']:
                    cart_item['cart_quantity'] += selected_product_quantity
            else:
                cart.append({
                    'prod_name': selected_product_name,
                    'prod_price': selected_product['prod_price'],
                    'cart_quantity': selected_product_quantity
                })
            logging.info(f'Added {selected_product_quantity} {selected_product_name}(s) to cart')

    total_items = sum(item.get('cart_quantity', 0) for item in cart)
    total_cost = sum(item['prod_price'] * item['cart_quantity'] for item in cart)

    logging.info('Viewed cart page')
    return render_template('cart.html', links=links, cart=cart, total_items=total_items, total_cost=total_cost)

@app.route('/buy', methods=['POST'])
def buy():
    global cart, product_list

    for item in cart:
        selected_product = next((product for product in product_list if product['prod_name'] == item['prod_name']), None)
        if selected_product:
            selected_product['quantity'] -= item.get('cart_quantity', 0)

    cart = []  # Clear the cart after purchase

    with open('product_list.json', 'w') as product_file:
        json.dump(product_list, product_file)

    logging.info('Completed purchase')
    
    # Redirect to the cart page after updating the product list
    return redirect(url_for('view_cart'))

if __name__ == '__main__':
    app.run(debug=True)
