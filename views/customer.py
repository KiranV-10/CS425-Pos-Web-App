from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQL_Error
from config import mydb
import logging
from .helper import get_serializable_data

logger = logging.getLogger(__name__)
customer_bp = Blueprint('customer', __name__)


# get all customer
@customer_bp.route('/', methods=['GET'])
def get_all_customers():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CUSTOMER")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(result), 200


# get customer by id. Parameters: id: id of the customer to get
@customer_bp.route('/<int:id>', methods=['GET'])
def get_customer_by_id(id):
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM customer WHERE customer_id = %s", (id,))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({'message': 'Customer not found!'}), 404
    finally:
        cursor.close()
        connection.close()
    return jsonify(customer), 200


# add a customer to the database. Parameter in post body is the customer object
@customer_bp.route('/add', methods=['POST'])
def add():
    data = request.json
    connection = mydb()
    try:
        with connection.cursor() as cursor:
            sql = ("INSERT INTO `customer` (`name_first_name`, `name_last_name`, `email`, `loyalty_points`, "
                   "`phone_number`) VALUES (%s, %s, %s, %s, %s)")
            cursor.execute(sql, (data['name_first_name'], data['name_last_name'], data['email'], data['loyalty_points'],
                                 data['phone_number']))
            customer_id = cursor.lastrowid
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Adding Customer: ' + str(e), 'success': False}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({'message': 'Customer added successfully!', 'customer_id': customer_id, 'success': True}), 201


# edit customer. Parameter: customer_id: the id of the customer to edit. The customer details are in the body of
# the post request
@customer_bp.route('/edit/<int:customer_id>', methods=['POST'])
def edit(customer_id):
    data = request.json
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        sql = ("UPDATE CUSTOMER SET name_first_name = %s, name_last_name=%s, email=%s, loyalty_points=%s, "
               "phone_number=%s WHERE customer_id=%s")
        cursor.execute(sql, (
            data['name_first_name'], data['name_last_name'], data['email'], data['loyalty_points'],
            data['phone_number'],
            customer_id))
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Updating Customer: ' + str(e), 'success': False}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify({'message': 'Customer updated successfully!', 'success': True}), 200


# delete customer. Parameter: id: the id of the customer to delete
@customer_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        cursor.execute("DELETE FROM customer WHERE customer_id = %s", (id,))
        if cursor.rowcount == 0:
            return jsonify({'message': 'Customer not found!'}), 404
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Deleting Customer: ' + str(e), 'success': False}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({'message': 'Customer deleted successfully!', 'success': True}), 200


# get rank of customer based on purchase amount
@customer_bp.route('/rank', methods=['GET'])
def get_all_customers_with_rank():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''With customer_with_order as 
    (Select customer_id, sum(quantity*price) as product_price_total from ORDERS natural join order_product natural join product 
    GROUP BY customer_id)
    select *, rank() over (order by product_price_total desc) as customer_rank from customer_with_order natural join customer;
    ''')
    result = cursor.fetchall()
    result = get_serializable_data(result)
    cursor.close()
    connection.close()
    return jsonify(result), 200


# get customers whole have an order
@customer_bp.route('/with-orders', methods=['GET'])
def get_all_customers_with_orders():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CUSTOMER WHERE customer_id in (Select distinct customer_id from ORDERS)")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(result), 200
