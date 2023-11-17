# CS425-Pos-Web-App
This is the flask backend application for CS 425. It is a CRUD application for a point-of-sale system. 

## DB Design and Information
The database ERD is designed as such: 

![Capture](https://github.com/MeganYTan/CS425-Pos-Web-App/assets/22186227/3b494977-c203-4d98-a7e8-05f0d55af10a)

The database is implemented in MySQL, and the process for creating it is detailed in this [document](https://docs.google.com/document/d/1tLjxkQ88COiYGmfYtHXzkRQGGcegsuj0LORLRAHLDZ0/edit). 


## Application Information

This application contains all the CRUD operations for all the tables listed. Note that since Payment and Order_Product are dependent on Orders, they are updated by updating the Orders table. To connect to the database, the mysql.connector library is used. 

### File Structure
app.py - entry file to the application

config.py  - database details and configuration 

views folder - Each dao can be found here, handling the CRUD operations for the corresponding object. helper.py is shared file containing helper functions for all the DAO.


## Running the application

To run the application on your device, run the commands in your terminal in the following steps:

1. Clone the application:

   ```git clone [https://github.com/MeganYTan/CS425-Pos-Web-App.git](https://github.com/MeganYTan/CS425-Pos-Web-App.git)```

3. Create virtualenvironment:

   ```python3 -m venv env```

5. Activate virtualenvironment:
  
   ```source env/scripts/activate```

8. Install requirements:

   ```pip install -r requirements.txt```

10. Run the application:

    ```env FLASK_APP=app.py  flask run```

The application runs on port 500 by default. To test that your application is running, navigate to http://localhost:5000/. You should see "Hello from flask".

### Setting up database for the application
To connect your own DB to this application, edit the details in config.py, providing the host, user, password, and database names for the database you want to connect to. 

## Application UI

The front-end of this application can be found in this repo: https://github.com/MeganYTan/CS-425-POS-UI
