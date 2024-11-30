import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://test.api.amadeus.com/v1"
api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")

def fetch_token():
    """
    Fetch an access token from the Amadeus API.

    Returns:
        str: Bearer token for API authentication.
    """
    token_url = f"{url}/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": api_secret
    }
    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def get_cheapest_destinations(access_token, origin, destination, departure_date, adults, max_price):
    """
    Retrieve cheapest flight offers from the Amadeus API.

    Args:
        access_token (str): Bearer token.
        origin (str): IATA code for departure location.
        destination (str): IATA code for destination.
        departure_date (str): Date in YYYY-MM-DD format.
        adults (int): Number of adult passengers.
        max_price (int): Max price per passenger.

    Returns:
        dict: JSON response containing flight offers.
    """
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": adults,
        "maxPrice": max_price
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def extract_flight_details(response):
    """
    Extract airline, origin, destination, and price from flight offers.

    Args:
        response (dict): API response containing flight offers.

    Returns:
        list[dict]: List of flights with keys: 'airline', 'origin', 'destination', 'price'.
    """
    flights = []
    for offer in response["data"]:
        segments = offer["itineraries"][0]["segments"]
        airline = response["dictionaries"]["carriers"].get(segments[0]["carrierCode"], segments[0]["carrierCode"])
        flights.append({
            "airline": airline,
            "origin": segments[0]["departure"]["iataCode"],
            "destination": segments[-1]["arrival"]["iataCode"],
            "price": f"{offer['price']['total']} {offer['price']['currency']}"
        })
    return flights