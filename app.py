import sys

from flask import Flask
from modules import customer
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

@app.route('/')
def index():
    app.logger.debug('This is flask app')
    return '<h1>Hello from Flask!</h1>'


if __name__ == '__main__':
    app.run(debug=True)

app.register_blueprint(customer.customer_bp, url_prefix="/customer")
