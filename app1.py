from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import mysql.connector
from mysql.connector import Error
from sklearn.linear_model import LinearRegression
import numpy as np
from decimal import Decimal  # Import Decimal

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'CarValue2'
}

def connect_to_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

class CarDatabase:
    def __init__(self):
        self.conn = connect_to_db()
        self.cursor = self.conn.cursor(dictionary=True)

    def get_listings(self, year, make, model):
        query = """
            SELECT v.year, v.make, v.model, v.trim, l.listing_price, 
                   l.listing_mileage, d.dealer_city, d.dealer_state
            FROM Vehicles v
            INNER JOIN Listings l ON v.vin = l.vin
            INNER JOIN Dealers d ON l.dealer_id = d.dealer_id
            WHERE v.year = %s AND v.make = %s AND v.model = %s
            LIMIT 100;
        """
        params = [year, make, model]
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        # Convert Decimal to float in the results
        for listing in results:
            if isinstance(listing['listing_price'], Decimal):
                listing['listing_price'] = float(listing['listing_price'])
            if isinstance(listing['listing_mileage'], Decimal):
                listing['listing_mileage'] = int(listing['listing_mileage'])
        
        return results

    def close(self):
        self.cursor.close()
        self.conn.close()

def predict_price_with_mileage(listings, input_mileage):
    if not listings:
        return 0.0

    mileages = np.array([listing['listing_mileage'] for listing in listings]).reshape(-1, 1)
    prices = np.array([listing['listing_price'] for listing in listings])

    model = LinearRegression()
    model.fit(mileages, prices)

    predicted_price = model.predict(np.array([[input_mileage]]))
    return round(predicted_price[0], -2)

@app.route('/', methods=['GET'])
def get_listings():
    year = request.args.get('year')
    make = request.args.get('make')
    model = request.args.get('model')
    mileage = request.args.get('mileage', type=int)

    if not (year and make and model):
        return jsonify({'error': 'Missing required parameters'}), 400

    db = CarDatabase()
    listings = db.get_listings(year, make, model)
    db.close()

    if not listings:
        return jsonify({'error': 'No listings found'}), 404

    estimated_price = predict_price_with_mileage(listings, mileage) if mileage else \
        round(sum(listing['listing_price'] for listing in listings) / len(listings), -2)

    response = {
        'estimated_market_value': f"${estimated_price:,.2f}",
        'listings': [
            {
                'year': listing['year'],
                'make': listing['make'],
                'model': listing['model'],
                'trim': listing['trim'],
                'listing_price': f"${listing['listing_price']:,.2f}",
                'listing_mileage': f"{listing['listing_mileage']} miles",
                'location': f"{listing['dealer_city']}, {listing['dealer_state']}"
            } for listing in listings
        ]
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
