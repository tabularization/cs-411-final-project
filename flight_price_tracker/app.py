from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
# from flask_cors import CORS

from flight_price_tracker.models import flight_model
from flight_price_tracker.models.price_model import PriceModel
from flight_price_tracker.models.login_model import User, db

from flight_price_tracker.utils.sql_utils import check_database_connection, check_table_exists
from flight_price_tracker.utils.password_utils import verify_password, generate_salt, hash_password

# ------- Flight API ---------
from flight_price_tracker.utils.flight_utils import fetch_token, get_cheapest_destinations, extract_flight_details


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db.init_app(app)

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
    Search for flights based on user input.

    Expected JSON Input:
        - origin (str): Origin IATA code
        - destination (str): Destination IATA code
        - departureDate (str): Departure date (YYYY-MM-DD)
        - adults (int): Number of adults
        - maxPrice (int): Maximum price

    Returns:
        JSON response with flight details.
    """
    try:
        # Parse user input from JSON
        data = request.get_json()
        origin = data.get('origin')
        destination = data.get('destination')
        departure_date = data.get('departureDate')
        adults = data.get('adults', 1)  # Default to 1 adult if not specified
        max_price = data.get('maxPrice', None)

        # Validate required fields
        if not origin or not destination or not departure_date:
            return jsonify({'Error': 'origin, destination, and departureDate are required'}), 400

        access_token = fetch_token()

        response = get_cheapest_destinations(access_token, origin, destination, departure_date, adults, max_price)

        flights = extract_flight_details(response)
        return jsonify({'status': 'success', 'flights': flights}), 200
    
    except Exception as e:
        app.logger.error(f"Error during flight search: {e}")
        return jsonify({'error': str(e)}), 500
# Initialize database
with app.app_context():
    db.create_all()