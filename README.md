**Vehicle Price Estimator**

**Objective**
The Vehicle Price Estimator is a smart web-based application designed to estimate the average market value of a vehicle based on its year, make, model, and optional mileage. This system includes:
A user-friendly web interface for input and result display.
A backend that calculates the average price of similar vehicle listings.
Database integration to store and retrieve data for cars and their listings.

**Features**
Search Interface: Allows users to input vehicle details (year, make, model, mileage) to retrieve estimated prices.
Price Estimation: Uses regression analysis to calculate price estimates based on vehicle mileage.
Listings: Displays up to 100 vehicle listings that match the user’s search criteria.

**Database Structure**
The project integrates with a MySQL database that stores the following tables:
Dealers Table: Contains information about car dealers.
Vehicles Table: Stores details about vehicles available for sale.
Vehicle Attributes Table: Includes additional attributes like engine type and fuel type.
Listings Table: Holds information about vehicle listings including price and mileage.
Status Log Table: Tracks the status of vehicle listings over time.

**Data Flow**
User Input: The user specifies the year, make, model, and optional mileage.
Database Query: The system queries the database to find matching listings.
Price Calculation: A regression analysis is performed to estimate the market price.
Output Display: The application displays the estimated market value and relevant listings.

**Setup**
**Prerequisites**
MySQL Server (installed and running)
Python 3.10 or later

**Required Libraries:**
mysql-connector-python
pandas
Flask
scikit-learn

**Install the necessary libraries:**
pip install mysql-connector-python pandas Flask scikit-learn

**Database Setup**
The populate_database.py script creates the database and tables, and loads the data into the system. Ensure to update MySQL credentials before running.

**Running the Application**
**Run the Flask app:**
python app.py
Access the web interface at http://127.0.0.1:5000.

**Backend Implementation**
Flask is used to handle web requests and interact with the MySQL database.
Linear Regression is applied for estimating vehicle prices based on mileage.

**Frontend Implementation**
The frontend consists of HTML and JavaScript files for vehicle search input and displaying results. The frontend interacts with the backend via AJAX requests.

**Testing**
Test cases are documented in the Google Sheet: Vehicle Market Value Estimator Test Cases.

**Deployment**
The application can be deployed using Gunicorn and Nginx for production. Refer to the deployment instructions for setting up a virtual environment, configuring the application server, and managing the Flask app using systemd.
