import logging
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

def fetch_token():
    """
    Fetch an access token from the Amadeus API.

    Returns:
        str: Bearer token for API authentication.
    """
    if not API_KEY or not API_SECRET:
        logger.error("API_KEY and API_SECRET must be set in environment variables.")
        raise EnvironmentError("API_KEY and API_SECRET not found.")

    token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": API_SECRET
    }

    try:
        logger.info("Fetching access token from Amadeus API")
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            logger.error("Access token not found in response.")
            raise ValueError("Access token not found.")

        logger.info("Access token successfully retrieved")
        return access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch access token: {e}")
        raise

def get_flight_offers(access_token, origin, destination, departure_date, return_date=None, adults=1):
    """
    Retrieve flight offers from the Amadeus API, restricted to specified popular airlines.

    Args:
        access_token (str): Bearer token.
        origin (str): IATA code for departure location.
        destination (str): IATA code for destination.
        departure_date (str): Date in YYYY-MM-DD format.
        return_date (str, optional): Return date in YYYY-MM-DD format. Defaults to None.
        adults (int): Number of adult passengers. Defaults to 1.

    Returns:
        dict: Raw JSON response containing flight offers.
    """
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": adults,
        "currencyCode": "USD",
        "max": 50,
    }

    if return_date:
        params["returnDate"] = return_date

    try:
        logger.info(f"Fetching flight offers from {origin} to {destination} on {departure_date}"
                    + (f" returning on {return_date}" if return_date else ""))
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        logger.info("Flight offers successfully retrieved")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch flight offers: {e}")
        raise