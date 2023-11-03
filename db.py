# This file returns the database for the modules to use
import mysql.connector

# change credentials here to connect to the database
host="localhost"
user="root"
password="root"
database="cs425_project"

# return the connected database
def mydb() :
        return mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
        )