import pytest
from flight_price_tracker.models.flight_model import FlightModel

@pytest.fixture
def sample_offer():
    """Sample valid flight offer."""
    return {
        "id": "1",
        "source": "GDS",
        "itineraries": [{
            "segments": [
                {
                    "carrierCode": "AA",
                    "departure": {"iataCode": "JFK"},
                    "arrival": {"iataCode": "LAX"}
                }
            ]
        }],
        "price": {"grandTotal": "200.00", "currency": "USD"},
        "validatingAirlineCodes": ["AA"],
        "travelerPricings": [{"fareDetailsBySegment": [{}]}]
    }

@pytest.fixture
def flight_model():
    """Fixture to provide a new instance of FlightModel for each test."""
    return FlightModel()

@pytest.fixture
def mock_api_calls(mocker):
    """Mock external API calls."""
    fetch_token_mock = mocker.patch(
        "flight_price_tracker.models.flight_model.fetch_token",
        return_value="mocked_token"
    )
    get_flight_offers_mock = mocker.patch(
        "flight_price_tracker.models.flight_model.get_flight_offers"
    )
    return {"fetch_token": fetch_token_mock, "get_flight_offers": get_flight_offers_mock}



##########################################################
# Flight Search
##########################################################

def test_search_flights_valid(mock_api_calls, flight_model, sample_offer):
    """Test searching for flights with valid offers."""
    mock_api_calls["get_flight_offers"].return_value = {"data": [sample_offer]}

    new_flights = flight_model.search_flights("JFK", "LAX", "2024-12-01", "2024-12-10", adults=1)

    assert len(new_flights) == 1, "One valid flight should be added."
    assert new_flights[0]["origin"] == "JFK", "Origin should match the flight offer."
    assert new_flights[0]["destination"] == "LAX", "Destination should match the flight offer."

def test_search_flights_no_offers(mock_api_calls, flight_model):
    """Test searching for flights with no offers."""
    mock_api_calls["get_flight_offers"].return_value = {"data": []}
    new_flights = flight_model.search_flights("JFK", "LAX", "2024-12-01", "2024-12-10", adults=1)
    assert len(new_flights) == 0, "No flights should be added when there are no offers."

def test_search_flights_failed(mock_api_calls, flight_model):
    """Test handling of errors during flight search."""
    mock_api_calls["get_flight_offers"].side_effect = Exception("API call failed")

    with pytest.raises(Exception, match="API call failed"):
        flight_model.search_flights("JFK", "LAX", "2024-12-01")


##########################################################
# Flight Storage and Filtering
##########################################################

def test_filter_flights_by_price(flight_model):
    """Test filtering flights by price."""
    flight_model.flights = [
        {"id": "1", "price": "150.00 USD", "airline": "AA"},
        {"id": "2", "price": "200.00 USD", "airline": "DL"},
        {"id": "3", "price": "100.00 USD", "airline": "UA"},
    ]
    filtered_flights = flight_model.filter_by_price_range(100.00, 150.00)
    assert len(filtered_flights) == 2, "Only flights within the price range should be returned."

def test_filter_flights_by_airline(flight_model):
    """Test filtering flights by airline."""
    flight_model.flights = [
        {"id": "1", "price": "150.00 USD", "airline": "AA"},
        {"id": "2", "price": "200.00 USD", "airline": "DL"},
        {"id": "3", "price": "100.00 USD", "airline": "AA"},
    ]
    filtered_flights = flight_model.filter_by_airline("AA")
    assert len(filtered_flights) == 2, "Only flights matching the airline should be returned."


def test_filter_flights_by_origin(flight_model):
    """Test filtering flights by origin."""
    flight_model.flights = [
        {"id": "1", "origin": "JFK", "price": "150.00 USD", "airline": "AA"},
        {"id": "2", "origin": "LAX", "price": "200.00 USD", "airline": "DL"},
        {"id": "3", "origin": "JFK", "price": "100.00 USD", "airline": "UA"},
    ]
    filtered_flights = flight_model.filter_by_origin("JFK")
    assert len(filtered_flights) == 2, "Only flights departing from JFK should be returned."
    assert all(f["origin"] == "JFK" for f in filtered_flights), "All filtered flights should have origin JFK."


def test_filter_with_no_flights(flight_model):
    """Test filtering when no flights are stored."""
    assert flight_model.filter_by_price_range(0, 100) == [], "No flights should be returned for an empty list."
    assert flight_model.filter_by_airline("AA") == [], "No flights should be returned for an empty list."


def test_search_flights_empty_input(flight_model):
    """Test searching flights with missing or empty input parameters."""
    with pytest.raises(TypeError):
        flight_model.search_flights()  

    with pytest.raises(ValueError):
        flight_model.search_flights("", "LAX", "2024-12-01")  # Empty origin



def test_filter_flights_non_usd_price(flight_model):
    """Test behavior when flights have non-USD prices."""
    flight_model.flights = [
        {"id": "1", "price": "150.00 EUR", "airline": "AA"},
        {"id": "2", "price": "200.00 GBP", "airline": "DL"},
    ]
    filtered_flights = flight_model.filter_by_price_range(100.00, 200.00)
    assert len(filtered_flights) == 0, "Non-USD prices should not match the price filter."
    
##########################################################
# Flight Storage
##########################################################

def test_get_flights(flight_model, sample_offer):
    """Test retrieving stored flights."""
    flight_model.flights.append(sample_offer)
    flights = flight_model.get_flights()
    assert len(flights) == 1, "Stored flights should match the number of added flights."

def test_clear_flights(flight_model, sample_offer):
    """Test clearing stored flights."""
    flight_model.flights.append(sample_offer)
    flight_model.clear_flights()
    flights = flight_model.get_flights()
    assert len(flights) == 0, "All flights should be cleared."


##########################################################
# Edge Cases
##########################################################

def test_filter_by_price_range_edge_cases(flight_model):
    """Test price filtering at exact boundaries."""
    flight_model.flights = [
        {"id": "1", "price": "100.00 USD", "airline": "AA"},
        {"id": "2", "price": "150.00 USD", "airline": "DL"},
        {"id": "3", "price": "200.00 USD", "airline": "UA"},
    ]
    # Filter with min and max matching prices exactly
    filtered_flights = flight_model.filter_by_price_range(100.00, 200.00)
    assert len(filtered_flights) == 3, "Flights at boundaries should be included."
    assert {"100.00 USD", "150.00 USD", "200.00 USD"}.issubset(
        {f["price"] for f in filtered_flights}
    ), "Flights at exact boundaries should match the filter."

def test_filter_by_price_with_mixed_currency(flight_model):
    """Test behavior when flights have a mix of USD and other currencies."""
    flight_model.flights = [
        {"id": "1", "price": "100.00 USD", "airline": "AA"},
        {"id": "2", "price": "150.00 EUR", "airline": "DL"},
        {"id": "3", "price": "200.00 USD", "airline": "UA"},
    ]
    filtered_flights = flight_model.filter_by_price_range(100.00, 200.00)
    assert len(filtered_flights) == 2, "Only USD flights within range should match."
    assert {"100.00 USD", "200.00 USD"}.issubset(
        {f["price"] for f in filtered_flights}
    ), "Filtered flights should only include USD within the range."
