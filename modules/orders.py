from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQL_Error
from helper import get_serializable_data, get_serializable_item
from db import mydb
import logging

logger = logging.getLogger(__name__)
orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/', methods=['GET'])
def get_all_orders():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM ORDERS_WITH_INFO ORDER BY ORDER_ID"
    cursor.execute(sql)
    result = cursor.fetchall()
    logger.debug(result)
    result = get_serializable_data(result)
    return jsonify(result), 200


@orders_bp.route('/<int:id>', methods=['GET'])
def get_order_by_id(id):
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM ORDERS_WITH_INFO WHERE order_id = %s", (id,))
        order = cursor.fetchone()
        logger.debug(order)
        order = get_serializable_item(order)
        if not order:
            return jsonify({'message': 'order not found!'}), 404
    finally:
        cursor.close()
        connection.close()
    return jsonify({ 'success': True, 'order': order}), 200


@orders_bp.route('/add', methods=['POST'])
def add():
    # order table, order product table, payment table
    data = request.json
    logger.debug(data)
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
        return jsonify({'message': 'Error Adding order', 'success': False}), 500
    finally:
        connection.close()

    return get_order_by_id(order_id)


@orders_bp.route('/edit/<int:order_id>', methods=['POST'])
def edit(order_id):
    data = request.json
    logger.debug(data)
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        # orders
        sql = "UPDATE orders SET date_time = %s, employee_id=%s, customer_id=%s, discount_id=%s WHERE order_id=%s"
        cursor.execute(sql, (data['date_time'], data['employee_id'], data['customer_id'], data['discount_id'], order_id))
        logger.debug(cursor._executed)


        # payment
        payment_sql = "UPDATE payment SET payment_method = %s, payment_amount=%s WHERE order_id=%s"
        cursor.execute(payment_sql,
                       (data['payment_method'], data['payment_amount'], order_id))
        logger.debug(cursor._executed)
        # order_product
        # drop first
        order_product_drop_sql = "DELETE FROM ORDER_PRODUCT WHERE ORDER_ID = %s"
        cursor.execute(order_product_drop_sql, (order_id,))
        order_product_sql = "INSERT INTO `order_product` (`product_id`, `quantity`, `order_id`) VALUES (%s, %s, %s)"
        for order_product in data['order_products']:
            cursor.execute(order_product_sql, (order_product['product_id'], order_product['quantity'], order_id))
        logger.debug(cursor._executed)
        # if cursor.rowcount == 0:
        #     return jsonify({'message': 'order not found!'}), 404
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Updating order', 'success': False}), 500
    finally:
        connection.close()

    return get_order_by_id(order_id)


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
        return jsonify({'message': 'Error Deleting order', 'success': False}), 500
    finally:
        # cursor.close()
        connection.close()

    return jsonify({'message': 'order deleted successfully!'}), 200
