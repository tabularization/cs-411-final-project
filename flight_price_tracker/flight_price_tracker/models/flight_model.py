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

    REQUIRED_FIELDS = [
        'id',
        'source',
        'itineraries',
        'price',
        'validatingAirlineCodes',
        'travelerPricings'
    ]

    def __init__(self):
        self.flights = []
        logger.info("Initialized FlightModel with an empty flight list")

    def validate_and_extract(self, offer, departure_date, return_date):
        """Validates a flight offer and extracts necessary details."""
        offer.setdefault('type', 'flight-offer')

        if not all(field in offer and offer[field] for field in self.REQUIRED_FIELDS):
            logger.error(f"Missing required fields in offer ID {offer.get('id', 'N/A')}")
            return None

        segments = offer['itineraries'][0].get('segments', [])
        if not segments:
            logger.warning(f"No segments in offer ID {offer.get('id', 'N/A')}")
            return None

        first_segment, last_segment = segments[0], segments[-1]
        airline = first_segment.get('carrierCode')
        price_total = offer['price'].get('grandTotal')
        currency = offer['price'].get('currency', 'USD')

        if not airline or not price_total:
            logger.warning(f"Incomplete data in offer ID {offer.get('id', 'N/A')}")
            return None

        try:
            price = float(price_total)
        except ValueError:
            logger.warning(f"Invalid price format in offer ID {offer.get('id', 'N/A')}")
            return None

        origin = first_segment['departure']['iataCode']
        destination = last_segment['arrival']['iataCode']

        if origin == destination:
            logger.warning(f"Origin and destination same in offer ID {offer.get('id', 'N/A')}")
            return None

        if not offer.get('travelerPricings'):
            logger.warning(f"No travelerPricings in offer ID {offer.get('id', 'N/A')}")
            return None

        return {
            "airline": airline,
            "origin": origin,
            "destination": destination,
            "departureDate": departure_date,
            "returnDate": return_date,
            "price": f"{price_total} {currency}"
        }, (airline, price)

    def search_flights(self, origin, destination, departure_date, return_date=None, adults=1):
        """Searches for flights and stores unique ones based on airline and price."""
        logger.info(f"Searching flights from {origin} to {destination} on {departure_date}"
                    + (f" returning on {return_date}" if return_date else "")
                    + f" for {adults} adult(s)")

        try:
            access_token = fetch_token()
            response = get_flight_offers(access_token, origin, destination, departure_date, return_date, adults)
            unique_flights = set()
            new_flights = []

            for offer in response.get("data", []):
                flight_data = self.validate_and_extract(offer, departure_date, return_date)
                if not flight_data:
                    continue

                flight_details, flight_key = flight_data
                if flight_key in unique_flights:
                    continue

                unique_flights.add(flight_key)
                new_flights.append(flight_details)

            if new_flights:
                self.flights.extend(new_flights)
                logger.info(f"Added {len(new_flights)} unique flight(s) to memory")
            else:
                logger.info("No new flights found to add")

            return new_flights

        except Exception as e:
            logger.error(f"Error during flight search: {e}")
            raise

    def get_flights(self):
        """Returns the list of stored flights."""
        logger.info("Retrieving stored flights")
        return self.flights

    def clear_flights(self):
        """Clears all stored flights."""
        self.flights = []
        logger.info("Cleared all flights from memory")