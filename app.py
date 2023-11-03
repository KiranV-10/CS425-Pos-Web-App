import sys
from flask import Flask
from modules import customer, employee, discount, product, orders
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
# allow the front end to get data
CORS(app, origins=["http://localhost:3000"])


# basic route used to test if the backend is running
@app.route('/')
def index():
    app.logger.debug('This is flask app')
    return '<h1>Hello from Flask!</h1>'


if __name__ == '__main__':
    app.run(debug=True)

# registers all the blueprints here with corresponding urls
app.register_blueprint(customer.customer_bp, url_prefix="/customer")
app.register_blueprint(employee.employee_bp, url_prefix="/employee")
app.register_blueprint(product.product_bp, url_prefix="/product")
app.register_blueprint(discount.discount_bp, url_prefix="/discount")
app.register_blueprint(orders.orders_bp, url_prefix="/orders")