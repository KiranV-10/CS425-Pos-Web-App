from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQL_Error
from helper import get_serializable_data, get_serializable_item
from db import mydb
import logging
# error here
logger = logging.getLogger(__name__)
discount_bp = Blueprint('discount', __name__)


@discount_bp.route('/', methods=['GET'])
def get_all_discounts():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM DISCOUNT")
    result = cursor.fetchall()
    result = get_serializable_data(result)
    return jsonify(result), 200


@discount_bp.route('/<int:id>', methods=['GET'])
def get_discount_by_id(id):
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM discount WHERE discount_id = %s", (id,))
        discount = cursor.fetchone()
        discount = get_serializable_item(discount)
        if not discount:
            return jsonify({'message': 'Discount not found!'}), 404
    finally:
        cursor.close()
        connection.close()
    return jsonify(discount), 200


@discount_bp.route('/add', methods=['POST'])
def add():
    data = request.json
    logger.debug(data)
    connection = mydb()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `discount` (`discount_description`, `discount_amount`, `coupon_code`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (data['discount_description'], data['discount_amount'], data['coupon_code']))
            discount_id = cursor.lastrowid
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Adding Discount', 'success': False}), 500
    finally:
        connection.close()

    return jsonify({'message': 'Discount added successfully!', 'discount_id': discount_id}), 201


@discount_bp.route('/edit/<int:discount_id>', methods=['POST'])
def edit(discount_id):
    data = request.json
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        sql = "UPDATE DISCOUNT SET discount_amount = %s, discount_description=%s, coupon_code=%s WHERE discount_id =%s"
        cursor.execute(sql, (
        data['discount_amount'], data['discount_description'], data['coupon_code'], discount_id))
        logger.debug(cursor._executed)
        # if cursor.rowcount == 0:
        #     return jsonify({'message': 'Discount not found!'}), 404
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Updating Discount', 'success': False}), 500
    finally:
        connection.close()

    return jsonify({'message': 'Discount updated successfully!', 'success': True}), 200


@discount_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        cursor.execute("DELETE FROM discount WHERE discount_id = %s", (id,))
        if cursor.rowcount == 0:
            return jsonify({'message': 'Discount not found!'}), 404
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Deleting Discount:' + str(e), 'success': False}), 500
    finally:
        # cursor.close()
        connection.close()

    return jsonify({'message': 'Discount deleted successfully!'}), 200
