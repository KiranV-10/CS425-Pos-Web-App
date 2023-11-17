from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQL_Error
from .helper import get_serializable_data, get_serializable_item
from config import mydb
import logging

logger = logging.getLogger(__name__)
orders_bp = Blueprint('orders', __name__)


# get all orders
@orders_bp.route('/', methods=['GET'])
def get_all_orders():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    sql = '''
        WITH otp AS (
    SELECT order_id, SUM(total_price) AS total_price FROM
    (SELECT order_id, quantity*price as total_price FROM
    (SELECT * FROM ORDERS NATURAL JOIN ORDER_PRODUCT NATURAL JOIN PRODUCT) t1) t2 
    GROUP BY order_id
    ORDER BY order_id
    )
    SELECT * FROM otp NATURAL JOIN Payment natural join (
    SELECT 
        o.*, 
        GROUP_CONCAT(
            CONCAT_WS(':', op.product_id, op.quantity) 
            SEPARATOR ','
        ) AS order_products
    FROM 
        order_product op
    NATURAL JOIN
        orders o
    GROUP BY 
        o.order_id
        ) t
    ;
    '''
    cursor.execute(sql)
    result = cursor.fetchall()
    result = get_serializable_data(result)
    return jsonify(result), 200


# get order by id. Parameters: id: id of the order to get
@orders_bp.route('/<int:id>', methods=['GET'])
def get_order_by_id(id):
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM ORDERS_WITH_INFO WHERE order_id = %s", (id,))
        order = cursor.fetchone()
        order = get_serializable_item(order)
        if not order:
            return jsonify({'message': 'order not found!', 'success': False}), 404
    finally:
        cursor.close()
        connection.close()
    return jsonify({'success': True, 'order': order}), 200


# add a order to the database. Parameter in post body is the order object
@orders_bp.route('/add', methods=['POST'])
def add():
    # order table, order product table, payment table
    data = request.json
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        insert_columns = ['date_time', 'employee_id']
        insert_values = [data['date_time'], data['employee_id']]
        if "customer_id" in data:
            insert_columns.append('customer_id')
            insert_values.append(data['customer_id'])
        if "discount_id" in data:
            insert_columns.append('discount_id')
            insert_values.append(data['discount_id'])
        placeholders = ', '.join(['%s'] * len(insert_columns))
        # Create the SQL statement
        sql = f"INSERT INTO ORDERS ({', '.join(insert_columns)}) VALUES ({placeholders})"
        cursor.execute(sql, insert_values)
        order_id = cursor.lastrowid
        # order_product
        order_product_sql = "INSERT INTO `order_product` (`product_id`, `quantity`, `order_id`) VALUES (%s, %s, %s)"
        for order_product in data['order_products']:
            cursor.execute(order_product_sql, (order_product['product_id'], order_product['quantity'], order_id))
        #payment
        payment_sql = "INSERT INTO `payment` (`payment_method`, `payment_amount`, `order_id`) VALUES (%s, %s, %s)"
        cursor.execute(payment_sql, (data['payment_method'], data['payment_amount'], order_id))
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Adding order: ' + str(e), 'success': False}), 500
    finally:
        cursor.close()
        connection.close()
    return get_order_by_id(order_id)


# edit order. Parameter: order_id: the id of the order to edit. The order details are in the body of
# the post request
@orders_bp.route('/edit/<int:order_id>', methods=['POST'])
def edit(order_id):
    data = request.json
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        # orders
        sql = ("UPDATE orders SET date_time = %s, employee_id=%s, order_id=%s, discount_id=%s, customer_id=%s WHERE "
               "order_id=%s")
        cursor.execute(sql, (data['date_time'], data['employee_id'], data['order_id'], data['discount_id'], data['customer_id'], order_id))
        # payment
        payment_sql = "UPDATE payment SET payment_method = %s, payment_amount=%s WHERE order_id=%s"
        cursor.execute(payment_sql,
                       (data['payment_method'], data['payment_amount'], order_id))
        # order_product
        # drop first
        order_product_drop_sql = "DELETE FROM ORDER_PRODUCT WHERE ORDER_ID = %s"
        cursor.execute(order_product_drop_sql, (order_id,))
        order_product_sql = "INSERT INTO `order_product` (`product_id`, `quantity`, `order_id`) VALUES (%s, %s, %s)"
        for order_product in data['order_products']:
            cursor.execute(order_product_sql, (order_product['product_id'], order_product['quantity'], order_id))
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Updating order: ' + str(e), 'success': False}), 500
    finally:
        connection.close()
    return get_order_by_id(order_id)


# delete order. Parameter: id: the id of the order to delete
@orders_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        cursor.execute("DELETE FROM order_product WHERE order_id = %s", (id,))
        cursor.execute("DELETE FROM payment WHERE order_id = %s", (id,))
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (id,))
        if cursor.rowcount == 0:
            return jsonify({'message': 'order not found!'}), 404
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Deleting order: ' + str(e), 'success': False}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({'message': 'order deleted successfully!', 'success': True}), 200
