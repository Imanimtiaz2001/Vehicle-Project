import mysql.connector 
import pandas as pd
from mysql.connector import Error

# Step 1: Connect to MySQL Server
def connect_to_mysql():
    try:
        # Establish connection to MySQL server
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            port=3306,
            password='password'
        )
        # Confirm connection and return connection object
        if conn.is_connected():
            print("Connected to MySQL server")
            return conn
    except Error as e:
        # Print error if connection fails
        print(f"Error connecting to MySQL server: {e}")
        return None

# Step 2: Create and Use Database
def create_and_use_database(cursor):
    try:
        # Create database if it does not exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS VehicleData;")
        print("Database created or already exists.")
        # Switch to the created or existing database
        cursor.execute("USE VehicleData;")
    except Error as e:
        # Print error if database creation or selection fails
        print(f"Error creating or using the database: {e}")

# Step 3: Create Tables with Improved Schema
def create_tables(cursor):
    # Create Dealers table with a schema for dealer details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Dealers (
            dealer_id INT AUTO_INCREMENT PRIMARY KEY,
            dealer_name VARCHAR(255),  -- Store dealer names up to 255 characters
            dealer_street VARCHAR(255),  -- Store street address up to 255 characters
            dealer_city VARCHAR(255),
            dealer_state VARCHAR(2),
            dealer_zip VARCHAR(15)
        );
    """)

    # Create Vehicles table with a schema for vehicle details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Vehicles (
            vin VARCHAR(17) PRIMARY KEY,  -- VIN as unique identifier
            year INT,
            make VARCHAR(255),
            model VARCHAR(255),
            trim VARCHAR(255),
            driven_wheels VARCHAR(255),
            used BOOLEAN,
            certified BOOLEAN,
            dealer_id INT,
            FOREIGN KEY (dealer_id) REFERENCES Dealers(dealer_id) ON DELETE SET NULL
        );
    """)

    # Create Vehicle_Attributes table with additional attributes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Vehicle_Attributes (
            vin VARCHAR(17),
            engine VARCHAR(255),
            fuel_type VARCHAR(255),
            exterior_color VARCHAR(255),
            interior_color VARCHAR(255),
            style VARCHAR(255),
            FOREIGN KEY (vin) REFERENCES Vehicles(vin) ON DELETE CASCADE
        );
    """)

    # Create Listings table with listing details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Listings (
            listing_id INT AUTO_INCREMENT PRIMARY KEY,
            vin VARCHAR(17),
            dealer_id INT,
            listing_price DECIMAL(10, 2),
            listing_mileage INT,
            seller_website TEXT,
            FOREIGN KEY (vin) REFERENCES Vehicles(vin) ON DELETE CASCADE,
            FOREIGN KEY (dealer_id) REFERENCES Dealers(dealer_id) ON DELETE SET NULL
        );
    """)

    # Create Status_Log table to log listing status history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Status_Log (
            listing_id INT,
            first_seen_date DATE,
            last_seen_date DATE,
            status VARCHAR(150),
            FOREIGN KEY (listing_id) REFERENCES Listings(listing_id) ON DELETE CASCADE
        );
    """)

    print("Tables created successfully.")

# Step 4: Load and Clean Data from Text File
def load_and_clean_data(file_path):
    # Load data from specified file path
    df = pd.read_csv(file_path, sep='|', encoding='utf-8')
    print(f"Loaded {len(df)} rows from the text file.")

    # Fill numeric columns with 0 for missing values
    numeric_cols = ['year', 'listing_price', 'listing_mileage']
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Fill text columns with empty strings for missing values
    text_cols = ['vin', 'make', 'model', 'trim', 'style', 'driven_wheels',
                 'engine', 'fuel_type', 'exterior_color', 'interior_color',
                 'dealer_name', 'dealer_street', 'dealer_city', 'dealer_state',
                 'seller_website']
    df[text_cols] = df[text_cols].fillna('')

    # Remove duplicates based on VIN
    df.drop_duplicates(subset='vin', inplace=True)
    print(f"{len(df)} rows remain after removing duplicates.")

    return df

# Step 5: Insert Data into Database
def insert_data(cursor, conn, df):
    try:
        batch_size = 1000  # Number of rows to commit at once for efficiency

        # Insert Dealers data
        dealers = df[['dealer_name', 'dealer_street', 'dealer_city', 'dealer_state', 'dealer_zip']].drop_duplicates()
        for idx, row in dealers.iterrows():
            cursor.execute("""
                INSERT INTO Dealers (dealer_name, dealer_street, dealer_city, dealer_state, dealer_zip)
                VALUES (%s, %s, %s, %s, %s)
            """, tuple(row))

            # Commit every batch_size rows for performance
            if idx % batch_size == 0:
                conn.commit()
                print(f"Committed {idx} dealers")

        # Insert Vehicles data
        for idx, row in df.iterrows():
            cursor.execute("""
                INSERT INTO Vehicles (vin, year, make, model, trim, driven_wheels, used, certified, dealer_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                    (SELECT dealer_id FROM Dealers WHERE dealer_name=%s LIMIT 1))
            """, (row['vin'], row['year'], row['make'], row['model'], row['trim'],
                  row['driven_wheels'], row['used'], row['certified'], row['dealer_name']))

            if idx % batch_size == 0:
                conn.commit()
                print(f"Committed {idx} vehicles")

        # Insert Vehicle_Attributes data
        for idx, row in df.iterrows():
            cursor.execute("""
                INSERT INTO Vehicle_Attributes (vin, engine, fuel_type, exterior_color, interior_color, style)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row['vin'], row['engine'], row['fuel_type'], row['exterior_color'], row['interior_color'], row['style']))

            if idx % batch_size == 0:
                conn.commit()
                print(f"Committed {idx} vehicle attributes")

        # Insert Listings and Status_Log data
        for idx, row in df.iterrows():
            cursor.execute("""
                INSERT INTO Listings (vin, dealer_id, listing_price, listing_mileage, seller_website)
                VALUES (%s, 
                    (SELECT dealer_id FROM Dealers WHERE dealer_name=%s LIMIT 1), 
                    %s, %s, %s)
            """, (row['vin'], row['dealer_name'], row['listing_price'], row['listing_mileage'], row['seller_website']))

            # Fetch the listing_id to log status
            cursor.execute("""
                SELECT listing_id FROM Listings 
                WHERE vin = %s AND dealer_id = (SELECT dealer_id FROM Dealers WHERE dealer_name = %s LIMIT 1)
            """, (row['vin'], row['dealer_name']))
            listing_id = cursor.fetchone()[0]

            # Insert listing status into Status_Log
            cursor.execute("""
                INSERT INTO Status_Log (listing_id, first_seen_date, last_seen_date, status) 
                VALUES (%s, %s, %s, %s)
            """, (listing_id, row['first_seen_date'], row['last_seen_date'], row['listing_status']))

            if idx % batch_size == 0:
                conn.commit()
                print(f"Committed {idx} listings and status logs")

        # Final commit after all inserts
        conn.commit()
        print("Data inserted successfully.")

    except Error as e:
        print(f"Error inserting data: {e}")
        print(cursor.statement)

# Step 6: Main function to execute the full workflow
def main():
    # Establish MySQL connection
    conn = connect_to_mysql()
    if conn:
        cursor = conn.cursor()
        # Set up database and tables
        create_and_use_database(cursor)
        create_tables(cursor)

        # Load and clean data from file
        df = load_and_clean_data('data.txt')

        # Insert cleaned data into database
        insert_data(cursor, conn, df)

        # Close database connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
