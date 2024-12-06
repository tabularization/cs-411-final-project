import logging
from flight_price_tracker.utils.flight_utils import fetch_token, get_flight_offers

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class FlightModel:
    """
    Handles interactions with the Amadeus API and manages flight data.
    
    Attributes:
        flights (list[dict]): In-memory storage for flight details from searches.
    """
    
    def __init__(self):
        self.flights = []
        logger.info("Initialized FlightModel with an empty flight list")

    def search_flights(self, origin, destination, departure_date, return_date=None, adults=1):
        """
        Fetch flights from the Amadeus API and store unique flights.

        Args:
            origin (str): Origin airport IATA code.
            destination (str): Destination airport IATA code.
            departure_date (str): Departure date (YYYY-MM-DD).
            return_date (str, optional): Return date (YYYY-MM-DD). Defaults to None.
            adults (int, optional): Number of travelers. Defaults to 1.

        Returns:
            list[dict]: List of newly added unique flights.
        """
        logger.info(f"Searching flights from {origin} to {destination} on {departure_date}" +
                    (f" returning on {return_date}" if return_date else "") +
                    f" for {adults} adult(s)")

        try:
            access_token = fetch_token()
            response = get_flight_offers(access_token, origin, destination, departure_date, return_date, adults)
            unique_flights = set()
            new_flights = []

            for offer in response.get("data", []):
                airline = offer["itineraries"][0]["segments"][0]["carrierCode"]
                price = float(offer["price"]["grandTotal"])
                flight_key = (airline, price)

                if flight_key not in unique_flights:
                    unique_flights.add(flight_key)
                    flight = {
                        "airline": airline,
                        "origin": offer["itineraries"][0]["segments"][0]["departure"]["iataCode"],
                        "destination": offer["itineraries"][-1]["segments"][-1]["arrival"]["iataCode"],
                        "departureDate": departure_date,
                        "returnDate": return_date,
                        "price": f"{price:.2f} USD",
                    }
                    new_flights.append(flight)

            self.flights.extend(new_flights)
            logger.info(f"Added {len(new_flights)} new flights to memory")
            return new_flights

        except Exception as e:
            logger.error(f"Failed to search flights: {e}")
            raise

    def get_flights(self):
        """
        Retrieve all stored flights.

        Returns:
            list[dict]: List of all stored flights.
        """
        logger.info("Retrieved all stored flights")
        return self.flights

    def clear_flights(self):
        """
        Clear all stored flights from memory.
        """
        self.flights = []
        logger.info("Cleared all flights from memory")

    def filter_by_airline(self, airline_code):
        """
        Retrieve flights operated by a specific airline.

        Args:
            airline_code (str): IATA code of the airline.

        Returns:
            list[dict]: Flights matching the airline code.
        """
        logger.info(f"Filtering flights for airline: {airline_code}")
        filtered_flights = []
        for flight in self.flights:
            if flight['airline'] == airline_code.upper():
                filtered_flights.append(flight)
        logger.info(f"Found {len(filtered_flights)} flights for airline: {airline_code}")
        return filtered_flights

    def filter_by_price_range(self, min_price, max_price):
        """
        Retrieve flights within a specific price range.

        Args:
            min_price (float): Minimum price in USD.
            max_price (float): Maximum price in USD.

        Returns:
            list[dict]: Flights within the specified price range.
        """
        logger.info(f"Filtering flights with price between {min_price} and {max_price}")
        filtered_flights = []
        for flight in self.flights:
            price_value = float(flight['price'].split()[0])  # Extract numeric price
            if min_price <= price_value <= max_price:
                filtered_flights.append(flight)
        logger.info(f"Found {len(filtered_flights)} flights in price range: {min_price}-{max_price} USD")
        return filtered_flights

    def filter_by_origin(self, origin_code):
        """
        Retrieve flights departing from a specific origin airport.

        Args:
            origin_code (str): IATA code of the origin airport.

        Returns:
            list[dict]: Flights departing from the specified origin.
        """
        logger.info(f"Filtering flights with origin: {origin_code}")
        filtered_flights = []
        for flight in self.flights:
            if flight['origin'] == origin_code.upper():
                filtered_flights.append(flight)
        logger.info(f"Found {len(filtered_flights)} flights departing from: {origin_code}")
        return filtered_flights