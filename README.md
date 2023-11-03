# CS425-Pos-Web-App
## This is the flask backend application for CS 425. It is a CRUD application for a point-of-sale system. 

The database ERD is designed as such: 

![Capture](https://github.com/MeganYTan/CS425-Pos-Web-App/assets/22186227/3b494977-c203-4d98-a7e8-05f0d55af10a)

This application contains all the CRUD operations for all the tables listed. Note that since Payment and Order_Product are dependent on Orders, they are updated by updating the Orders table.

To run the application: 

$ env FLASK_APP=app.py  flask run

It runs on port 500 by default.

The front-end of this application can be found in this repo: https://github.com/MeganYTan/CS-425-POS-UI
