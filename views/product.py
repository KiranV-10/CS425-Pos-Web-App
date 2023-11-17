from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQL_Error
from .helper import get_serializable_data, get_serializable_item
from config import mydb
import logging

logger = logging.getLogger(__name__)
product_bp = Blueprint('product', __name__)


# get all product
@product_bp.route('/', methods=['GET'])
def get_all_products():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM PRODUCT")
    result = cursor.fetchall()
    result = get_serializable_data(result)
    return jsonify(result), 200


# get product by id. Parameters: id: id of the product to get
@product_bp.route('/<int:id>', methods=['GET'])
def get_product_by_id(id):
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM product WHERE product_id = %s", (id,))
        product = cursor.fetchone()
        product = get_serializable_item(product)
        if not product:
            return jsonify({'message': 'product not found!'}), 404
    finally:
        cursor.close()
        connection.close()
    return jsonify(product), 200


# add a product to the database. Parameter in request body is the product object
@product_bp.route('/add', methods=['POST'])
def add():
    data = request.json
    connection = mydb()
    try:
        with connection.cursor() as cursor:
            sql = ("INSERT INTO `product` (`category`, `product_name`, `price`, `product_description`) VALUES (%s, %s, "
                   "%s, %s)")
            cursor.execute(sql, (data['category'], data['product_name'], data['price'], data['product_description']))
            product_id = cursor.lastrowid
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Adding product: ' + str(e), 'success': False}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify({'message': 'product added successfully!', 'product_id': product_id, 'success': True}), 201


# edit product. Parameter: product_id: the id of the product to edit. The product details are in the body of
# the post request
@product_bp.route('/edit/<int:product_id>', methods=['POST'])
def edit(product_id):
    data = request.json
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        sql = "UPDATE product SET category = %s, product_name=%s, price=%s, product_description=%s WHERE product_id=%s"
        cursor.execute(sql,
                       (data['category'], data['product_name'], data['price'], data['product_description'], product_id))
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Updating product: ' + str(e), 'success': False}), 500
    finally:
        connection.close()

    return jsonify({'message': 'product updated successfully!', 'success': True}), 200


# delete product. Parameter: id: the id of the product to delete
@product_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        cursor.execute("DELETE FROM product WHERE product_id = %s", (id,))
        if cursor.rowcount == 0:
            return jsonify({'message': 'product not found!'}), 404
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Deleting product: ' + str(e), 'success': False}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify({'message': 'product deleted successfully!', 'success': True}), 200


# get all products with orders and discount
@product_bp.route('/orders-and-discount', methods=['GET'])
def get_all_products_with_orders_and_discount():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''SELECT * FROM PRODUCT WHERE PRODUCT_ID in (
    SELECT DISTINCT p.product_id
    FROM Product p
    JOIN Order_Product op ON p.product_id = op.product_id
    UNION
    SELECT DISTINCT p.product_id
    FROM Product p
    JOIN Order_Product op ON p.product_id = op.product_id
    JOIN Orders o ON op.order_id = o.order_id
    WHERE o.discount_id IS NOT NULL)''')
    result = cursor.fetchall()
    result = get_serializable_data(result)
    return jsonify(result), 200


# get all products cheaper than average product
@product_bp.route('/cheaper-than-average', methods=['GET'])
def get_all_products_cheaper_than_average():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Product WHERE price < ALL (SELECT AVG(price) FROM Product GROUP BY category)")
    result = cursor.fetchall()
    result = get_serializable_data(result)
    return jsonify(result), 200


# get all product with sales
@product_bp.route('/with-sales', methods=['GET'])
def get_all_products_with_sales():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''SELECT p.product_id, p.category, product_name, price, product_description, PRODUCT_TOTAL_SALES_AMOUNT FROM PRODUCT RIGHT JOIN (
    SELECT 
        COALESCE(category, 'All') AS category,
        product_id,
        SUM(quantity*price) AS PRODUCT_TOTAL_SALES_AMOUNT 
    FROM ORDER_PRODUCT NATURAL JOIN PRODUCT 
    GROUP BY category, product_id 
    WITH ROLLUP
    )p on PRODUCT.product_id = p.product_id''')
    result = cursor.fetchall()
    result = get_serializable_data(result)
    return jsonify(result), 200
