from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQL_Error
import hashlib
from db import mydb
import logging

logger = logging.getLogger(__name__)
employee_bp = Blueprint('employee', __name__)
salt = "cs425"


# helper function to hash password inputs
def get_hashed_password(password):
    salted_password = password + salt
    return hashlib.md5(salted_password.encode("utf-8")).hexdigest()


# get employee by id. Parameters: id: id of the employee to get. This is an inner helper function
def get_employee_by_id(id):
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM EMPLOYEE WHERE employee_id = %s", (id,))
        employee = cursor.fetchone()
        if not employee:
            return jsonify({'message': 'Employee not found!'}), 404
    finally:
        cursor.close()
        connection.close()
    return employee


# get all employee
@employee_bp.route('/', methods=['GET'])
def get_all_employees():
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM EMPLOYEE")
    result = cursor.fetchall()
    return jsonify(result), 200


# get employee by id. Parameters: id: id of the employee to get
@employee_bp.route('/<int:id>', methods=['GET'])
def get_employee_by_id_json(id):
    employee = get_employee_by_id(id)
    return jsonify(employee), 200


# add a employee to the database. Parameter in post body is the employee object
@employee_bp.route('/add', methods=['POST'])
def add():
    data = request.json
    connection = mydb()
    try:
        with connection.cursor(dictionary=True) as cursor:
            db_password = get_hashed_password(data['employee_password'])
            sql = ("INSERT INTO Employee (name_first_name, name_last_name, employee_role, phone_number, "
                   "employee_email, employee_password) VALUES (%s, %s, %s, %s, %s, %s)")
            cursor.execute(sql, (data['name_first_name'], data['name_last_name'], data['employee_role'], data['phone_number'], data['employee_email'], db_password))
            employee_id = cursor.lastrowid
            # get the employee to return it
            cursor.execute("SELECT * FROM EMPLOYEE WHERE employee_id = %s", (employee_id,))
            employee = cursor.fetchone()
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Adding Employee', 'success': False}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify({'message': 'Employee added successfully!', 'employee': employee, 'success': True}), 201


# edit employee. Parameter: employee_id: the id of the employee to edit. The employee details are in the body of
# the post request
@employee_bp.route('/edit/<int:employee_id>', methods=['POST'])
def edit(employee_id):
    employee = request.json
    connection = mydb()
    cursor = connection.cursor(dictionary=True)
    try:
        # is password has been edited, get the hashed password
        if 'hasPasswordBeenEdited' in employee and employee['hasPasswordBeenEdited']:
            db_password = get_hashed_password(employee['employee_password'])
            sql = ("UPDATE EMPLOYEE SET name_first_name = %s, name_last_name=%s, employee_role=%s, phone_number=%s, "
                   "employee_email=%s,employee_password=%s  WHERE employee_id=%s")
            cursor.execute(sql, (employee['name_first_name'], employee['name_last_name'],  employee['employee_role'], employee['phone_number'], employee['employee_email'], db_password, employee_id))
        else:
            sql = ("UPDATE EMPLOYEE SET name_first_name = %s, name_last_name=%s, employee_role=%s, phone_number=%s, "
                   "employee_email=%s WHERE employee_id=%s")
            cursor.execute(sql, (employee['name_first_name'], employee['name_last_name'], employee['employee_role'],
                                 employee['phone_number'], employee['employee_email'], employee_id))
        cursor.execute("SELECT * FROM EMPLOYEE WHERE employee_id = %s", (employee_id,))
        employee = cursor.fetchone()
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Updating Employee', 'success': False}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify({'message': 'Employee updated successfully!', 'success': True, 'employee': employee}), 200


# delete employee. Parameter: id: the id of the employee to delete
@employee_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    connection = mydb()
    cursor = connection.cursor(prepared=True)
    try:
        cursor.execute("DELETE FROM EMPLOYEE WHERE EMPLOYEE_ID = %s", (id,))
        if cursor.rowcount == 0:
            return jsonify({'message': 'EMPLOYEE not found!'}), 404
        connection.commit()
    except MySQL_Error as e:
        connection.rollback()
        logger.error(f"MySQL Error: {e}")
        return jsonify({'message': 'Error Deleting EMPLOYEE', 'success': False}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify({'message': 'EMPLOYEE deleted successfully!'}), 200

