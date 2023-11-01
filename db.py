# CHANGE CREDENTIALS HERE
import mysql.connector

host="localhost"
user="root"
password="root"
database="cs425_project"

def mydb() :
        return mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
        )