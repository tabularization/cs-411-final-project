import pytest
from unittest.mock import patch
from flight_price_tracker.models.flight_model import FlightModel




@pytest.fixture
def sample_offer():
    """Sample valid flight offer."""
    return {
        "id": "1",
        "itineraries": [
            {
                "segments": [
                    {
                        "carrierCode": "AA",
                        "departure": {"iataCode": "JFK"},
                        "arrival": {"iataCode": "LAX"},
                    }
                ]
            }
        ],
        "price": {"grandTotal": "200.00", "currency": "USD"},
    }




@pytest.fixture
def flight_model():
    """Fixture to provide a new instance of FlightModel for each test."""
    return FlightModel()




@pytest.fixture
def mock_api_calls(mocker):
    """Mock external API calls."""
    mocker.patch("flight_price_tracker.models.flight_model.fetch_token", return_value="mocked_token")
    mocker.patch(
        "flight_price_tracker.models.flight_model.get_flight_offers",
        return_value={
            "data": [
                {
                    "itineraries": [
                        {
                            "segments": [
                                {
                                    "carrierCode": "AA",
                                    "departure": {"iataCode": "JFK"},
                                    "arrival": {"iataCode": "LAX"},
                                }
                            ]
                        }
                    ],
                    "price": {"grandTotal": "200.00", "currency": "USD"},
                    "validatingAirlineCodes": ["AA"]
                }
            ]
        },
    )






@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("API_KEY", "mock_api_key")
    monkeypatch.setenv("API_SECRET", "mock_api_secret")




@pytest.fixture
def mock_fetch_token(mocker):
    """Mock fetch_token function to return a valid token."""
    mocker.patch("flight_price_tracker.models.flight_model.fetch_token", return_value="mocked_token")


##########################################################
# Flight Search
##########################################################


def test_search_flights_valid(mock_api_calls, flight_model, sample_offer):
    """Test searching for flights with valid offers."""
    new_flights = flight_model.search_flights(
        "JFK", "LAX", "2024-12-01", "2024-12-10", adults=1
    )
    assert len(new_flights) == 1, "One valid flight should be added."
    assert new_flights[0]["origin"] == "JFK", "Origin should match the flight offer."
    assert new_flights[0]["destination"] == "LAX", "Destination should match the flight offer."




def test_search_flights_no_offers(mock_api_calls, flight_model):
    """Test searching for flights with no offers."""
    with patch(
        "flight_price_tracker.models.flight_model.get_flight_offers",
        return_value={"data": []},
    ):
        new_flights = flight_model.search_flights(
            "JFK", "LAX", "2024-12-01", "2024-12-10", adults=1
        )
        assert len(new_flights) == 0, "No flights should be added when there are no offers."




def test_search_flights_failed(mock_api_calls, flight_model):
    """Test handling of errors during flight search."""
    with patch(
        "flight_price_tracker.models.flight_model.get_flight_offers",
        side_effect=Exception("API call failed"),
    ):
        with pytest.raises(Exception, match="API call failed"):
            flight_model.search_flights("JFK", "LAX", "2024-12-01")








def test_search_flights_empty_input(flight_model):
    """Test searching flights with missing or empty input parameters."""
    with patch("flight_price_tracker.models.flight_model.fetch_token", return_value="mocked_token"), \
         patch("flight_price_tracker.models.flight_model.get_flight_offers", return_value={"data": []}):
        with pytest.raises(ValueError, match="Origin and destination must be provided"):
            flight_model.search_flights("", "LAX", "2024-12-01")






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
    filtered_flights = flight_model.filter_by_price_range(100.00, 200.00)
    assert len(filtered_flights) == 3, "Flights at boundaries should be included."
    assert {"100.00 USD", "150.00 USD", "200.00 USD"}.issubset(
        {f["price"] for f in filtered_flights}
    ), "Flights at exact boundaries should match the filter."



