from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
# from flask_cors import CORS

from flight_price_tracker.models import flight_model
from flight_price_tracker.models.price_model import PriceModel
from flight_price_tracker.models.login_model import User, db

from flight_price_tracker.utils.sql_utils import check_database_connection, check_table_exists
from flight_price_tracker.utils.password_utils import verify_password, generate_salt, hash_password

# ------- Flight API ---------
from flight_price_tracker.models.flight_model import FlightModel


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db.init_app(app)

# Initialize the FlightModel
flight_model = FlightModel()

@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and meals table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if users table exists...")
        check_table_exists("users")
        #need to do create a flight table and check if flight table is healthy
        app.logger.info("users table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)


@app.route('/create-account', methods=['POST'])
def create_account():
    """
    Create a new user account.
    
    Request JSON:
    {
        "username": "example_user",
        "password": "secure_password"
    }
    
    Returns:
        JSON response with success status
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Validate input
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409
    
    # Create user
    try:
        User.create_user(username, password)
        return jsonify({"message": "Account created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate user login.
    
    Request JSON:
    {
        "username": "example_user",
        "password": "secure_password"
    }
    
    Returns:
        JSON response with login status
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Validate input
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    # Find user
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Verify password
    if verify_password(user.hashed_password, user.salt, password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/update-password', methods=['PUT'])
def update_password():
    """
    Update user's password.
    
    Request JSON:
    {
        "username": "example_user",
        "current_password": "old_password",
        "new_password": "new_secure_password"
    }
    
    Returns:
        JSON response with update status
    """
    data = request.json
    username = data.get('username')
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    # Validate input
    if not all([username, current_password, new_password]):
        return jsonify({"error": "All fields are required"}), 400
    
    # Find user
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Verify current password
    if not verify_password(user.hashed_password, user.salt, current_password):
        return jsonify({"error": "Current password is incorrect"}), 401
    
    # Update password
    try:
        new_salt = generate_salt()
        new_hashed_password = hash_password(new_password, new_salt)
        
        user.salt = new_salt
        user.hashed_password = new_hashed_password
        db.session.commit()
        
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/flights/search', methods=['POST'])
def search_flights():
    """
    Search for flights based on user input and store unique flights.
    
    Args:
        - origin (str): Origin IATA code
        - destination (str): Destination IATA code
        - departureDate (str): Departure date (YYYY-MM-DD)
        - returnDate (str, optional): Return date (YYYY-MM-DD)
        - adults (int, optional): Number of adults (default: 1)
    
    Returns:
        JSON response with flight details.
    """
    data = request.get_json()
    origin = data.get('origin')
    destination = data.get('destination')
    departure_date = data.get('departureDate')
    return_date = data.get('returnDate')
    adults = data.get('adults', 1)
    try:
        if not all([origin, destination, departure_date]):
            app.logger.warning("Missing required fields in flight search request")
            return jsonify({'error': 'origin, destination, and departureDate are required'}), 400

        flights = flight_model.search_flights(origin, destination, departure_date, return_date, adults)
        return jsonify({'status': 'success', 'flights': flights}), 200

    except Exception as e:
        app.logger.error(f"Error during flight search: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/flights', methods=['GET'])
def get_all_flights():
    """
    Retrieve all stored flight data from memory.

    Returns:
        JSON response with status and all stored flight details.
    """
    try:
        flights = flight_model.get_flights()
        return jsonify({'status': 'success', 'flights': flights}), 200
    except Exception as e:
        app.logger.error(f"Error retrieving all flights: {e}")
        return jsonify({'error': 'Failed to retrieve flights'}), 500


@app.route('/api/flights/clear', methods=['POST'])
def clear_flights():
    """
    Clear all stored flight data from memory.

    Returns:
        JSON response confirming the operation.
    """
    try:
        flight_model.clear_flights()
        return jsonify({'status': 'success', 'message': 'All flights have been cleared'}), 200
    except Exception as e:
        app.logger.error(f"Error clearing flights: {e}")
        return jsonify({'error': 'Failed to clear flights'}), 500


@app.route('/api/flights/airline/<airline_code>', methods=['GET'])
def get_flights_by_airline(airline_code):
    """
    Retrieve flights filtered by airline code.

    Args:
        airline_code (str): IATA code of the airline.

    Returns:
        JSON response with status and flights matching the airline code.
    """
    try:
        app.logger.info(f"Retrieving flights for airline: {airline_code}")
        filtered_flights = flight_model.filter_by_airline(airline_code)
        return jsonify({'status': 'success', 'flights': filtered_flights}), 200
    except Exception as e:
        app.logger.error(f"Error retrieving flights by airline: {e}")
        return jsonify({'error': 'Failed to retrieve flights by airline'}), 500


@app.route('/api/flights/price', methods=['GET'])
def get_flights_by_price():
    """
    Retrieve flights within a specific price range.

    Args:
        min (float): Minimum price in USD.
        max (float): Maximum price in USD.

    Returns:
        JSON response with status and flights in the price range.
    """
    try:
        min_price = request.args.get('min', type=float)
        max_price = request.args.get('max', type=float)

        if min_price is None or max_price is None:
            app.logger.warning("Missing min or max price parameters")
            return jsonify({'error': 'min and max price parameters are required'}), 400

        app.logger.info(f"Retrieving flights with price between {min_price} and {max_price}")
        filtered_flights = flight_model.filter_by_price_range(min_price, max_price)
        return jsonify({'status': 'success', 'flights': filtered_flights}), 200
    except Exception as e:
        app.logger.error(f"Error retrieving flights by price: {e}")
        return jsonify({'error': 'Failed to retrieve flights by price range'}), 500


@app.route('/api/flights/origin/<origin_code>', methods=['GET'])
def get_flights_by_origin(origin_code):
    """
    Retrieve flights filtered by origin airport.

    Args:
        origin_code (str): IATA code of the origin airport.

    Returns:
        JSON response with status and flights departing from the origin.
    """
    try:
        app.logger.info(f"Retrieving flights from origin: {origin_code}")
        filtered_flights = flight_model.filter_by_origin(origin_code)
        return jsonify({'status': 'success', 'flights': filtered_flights}), 200
    except Exception as e:
        app.logger.error(f"Error retrieving flights by origin: {e}")
        return jsonify({'error': 'Failed to retrieve flights by origin'}), 500

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
