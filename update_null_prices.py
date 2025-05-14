import mysql.connector
from mysql.connector import Error

def connect_to_mysql():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='VehicleData'
        )
        if conn.is_connected():
            print("Connected to MySQL database")
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def update_zero_listing_prices(cursor, conn):
    # Fetch records with listing_price set to 0
    cursor.execute("SELECT listing_id, year, make, model, dealer_city, dealer_state, listing_mileage FROM Listings "
                   "JOIN Vehicles ON Listings.vin = Vehicles.vin "
                   "JOIN Dealers ON Listings.dealer_id = Dealers.dealer_id "
                   "WHERE listing_price = 0;")
    zero_price_records = cursor.fetchall()
    
    for record in zero_price_records:
        listing_id, year, make, model, city, state, mileage = record
        
        # Query 1: Match all criteria (year, make, model, city, state, and similar mileage)
        cursor.execute("""
            SELECT COUNT(*), AVG(listing_price) FROM Listings 
            JOIN Vehicles ON Listings.vin = Vehicles.vin
            JOIN Dealers ON Listings.dealer_id = Dealers.dealer_id
            WHERE year = %s AND make = %s AND model = %s 
            AND dealer_city = %s AND dealer_state = %s
            AND listing_price > 0 
            AND ABS(listing_mileage - %s) <= 0.05 * %s
        """, (year, make, model, city, state, mileage, mileage))
        
        count, avg_price = cursor.fetchone()
        
        if count > 0:
            # Update the listing price
            cursor.execute("UPDATE Listings SET listing_price = %s WHERE listing_id = %s", (avg_price, listing_id))
            continue

        # Query 2: Match only year, make, model, and similar mileage
        cursor.execute("""
            SELECT COUNT(*), AVG(listing_price) FROM Listings 
            JOIN Vehicles ON Listings.vin = Vehicles.vin
            WHERE year = %s AND make = %s AND model = %s
            AND listing_price > 0 
            AND ABS(listing_mileage - %s) <= 0.05 * %s
        """, (year, make, model, mileage, mileage))
        
        count, avg_price = cursor.fetchone()
        
        if count > 0:
            # Update the listing price
            cursor.execute("UPDATE Listings SET listing_price = %s WHERE listing_id = %s", (avg_price, listing_id))
            continue

        # Query 3: Match only year, make, and model
        cursor.execute("""
            SELECT COUNT(*), AVG(listing_price) FROM Listings 
            JOIN Vehicles ON Listings.vin = Vehicles.vin
            WHERE year = %s AND make = %s AND model = %s 
            AND listing_price > 0
        """, (year, make, model))
        
        count, avg_price = cursor.fetchone()
        
        if count > 0:
            # Update the listing price
            cursor.execute("UPDATE Listings SET listing_price = %s WHERE listing_id = %s", (avg_price, listing_id))

    # Commit all updates
    conn.commit()
    print("Listing prices updated where applicable.")

def main():
    conn = connect_to_mysql()
    if conn:
        cursor = conn.cursor()
        
        update_zero_listing_prices(cursor, conn)
        
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
import mysql.connector
from mysql.connector import Error

# Function to connect to the MySQL database
def connect_to_mysql():
    try:
        # Establish connection with the database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='VehicleData'
        )
        # Check if the connection is successful
        if conn.is_connected():
            print("Connected to MySQL database")
            return conn
    except Error as e:
        # Print an error message if the connection fails
        print(f"Error connecting to MySQL: {e}")
        return None

# Function to update listings with a zero listing price
def update_zero_listing_prices(cursor, conn):
    # Fetch records from Listings with listing_price set to 0
    cursor.execute("SELECT listing_id, year, make, model, dealer_city, dealer_state, listing_mileage FROM Listings "
                   "JOIN Vehicles ON Listings.vin = Vehicles.vin "
                   "JOIN Dealers ON Listings.dealer_id = Dealers.dealer_id "
                   "WHERE listing_price = 0;")
    zero_price_records = cursor.fetchall()
    
    # Iterate through each record with a zero listing price
    for record in zero_price_records:
        listing_id, year, make, model, city, state, mileage = record
        
        # Query 1: Find similar vehicles with the same year, make, model, location, and mileage within a 5% tolerance
        cursor.execute("""
            SELECT COUNT(*), AVG(listing_price) FROM Listings 
            JOIN Vehicles ON Listings.vin = Vehicles.vin
            JOIN Dealers ON Listings.dealer_id = Dealers.dealer_id
            WHERE year = %s AND make = %s AND model = %s 
            AND dealer_city = %s AND dealer_state = %s
            AND listing_price > 0 
            AND ABS(listing_mileage - %s) <= 0.05 * %s
        """, (year, make, model, city, state, mileage, mileage))
        
        count, avg_price = cursor.fetchone()
        
        # If matches are found, update listing_price with the average price
        if count > 0:
            cursor.execute("UPDATE Listings SET listing_price = %s WHERE listing_id = %s", (avg_price, listing_id))
            continue  # Move to the next record if update is successful

        # Query 2: Find similar vehicles based on year, make, model, and mileage (without location)
        cursor.execute("""
            SELECT COUNT(*), AVG(listing_price) FROM Listings 
            JOIN Vehicles ON Listings.vin = Vehicles.vin
            WHERE year = %s AND make = %s AND model = %s
            AND listing_price > 0 
            AND ABS(listing_mileage - %s) <= 0.05 * %s
        """, (year, make, model, mileage, mileage))
        
        count, avg_price = cursor.fetchone()
        
        # If matches are found, update listing_price with the average price
        if count > 0:
            cursor.execute("UPDATE Listings SET listing_price = %s WHERE listing_id = %s", (avg_price, listing_id))
            continue  # Move to the next record if update is successful

        # Query 3: Find similar vehicles based on year, make, and model only (without mileage and location)
        cursor.execute("""
            SELECT COUNT(*), AVG(listing_price) FROM Listings 
            JOIN Vehicles ON Listings.vin = Vehicles.vin
            WHERE year = %s AND make = %s AND model = %s 
            AND listing_price > 0
        """, (year, make, model))
        
        count, avg_price = cursor.fetchone()
        
        # If matches are found, update listing_price with the average price
        if count > 0:
            cursor.execute("UPDATE Listings SET listing_price = %s WHERE listing_id = %s", (avg_price, listing_id))

    # Commit all the updates to the database
    conn.commit()
    print("Listing prices updated where applicable.")

# Main function to execute the program
def main():
    # Connect to the database
    conn = connect_to_mysql()
    if conn:
        cursor = conn.cursor()
        
        # Update listings with zero prices
        update_zero_listing_prices(cursor, conn)
        
        # Close the database cursor and connection
        cursor.close()
        conn.close()

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
