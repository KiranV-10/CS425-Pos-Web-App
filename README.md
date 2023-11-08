# CS425-Pos-Web-App
## This is the flask backend application for CS 425. It is a CRUD application for a point-of-sale system. 

The database ERD is designed as such: 

![Capture](https://github.com/MeganYTan/CS425-Pos-Web-App/assets/22186227/3b494977-c203-4d98-a7e8-05f0d55af10a)

The database is implemented in MySQL, and the process for creating it is detailed in this [document](https://docs.google.com/document/d/1tLjxkQ88COiYGmfYtHXzkRQGGcegsuj0LORLRAHLDZ0/edit). 

This application contains all the CRUD operations for all the tables listed. Note that since Payment and Order_Product are dependent on Orders, they are updated by updating the Orders table. To connect to the database, the mysql.connector library is used. 

The application's entry file is app.py. db.py details the database details, and helper.py is a shared file containing helper functions for all the modules. Each dao can be found in the modules folder.

To connect your own DB to this application, edit the details in db.py, providing the host, user, password, and database names for the database you want to connect to. 



To run the application: 

Clone the application.

Create virtualenvironment: python3 -m venv env

Activate virtualenvironment: source env/scripts/activate

Install requirements: pip install -r requirements.txt

Run the application: $ env FLASK_APP=app.py  flask run

It runs on port 500 by default.

The front-end of this application can be found in this repo: https://github.com/MeganYTan/CS-425-POS-UI
