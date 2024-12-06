#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

###############################################
#
# Flight Search Tests
#
###############################################

search_flights() {
  local origin=$1
  local destination=$2
  local departure_date=$3
  local return_date=$4
  local adults=${5:-1}

  echo "Searching flights from $origin to $destination on $departure_date..."
  flight_data="{\"origin\":\"$origin\",\"destination\":\"$destination\",\"departureDate\":\"$departure_date\""
  
  if [ ! -z "$return_date" ]; then
    flight_data+=",\"returnDate\":\"$return_date\""
  fi
  
  flight_data+=",\"adults\":$adults}"

  response=$(curl -s -X POST -H "Content-Type: application/json" -d "$flight_data" "$BASE_URL/flights/search")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Flight search successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Flight Search JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Flight search failed."
    echo "Response: $response"
    exit 1
  fi
}

get_all_flights() {
  echo "Retrieving all flights..."
  response=$(curl -s -X GET "$BASE_URL/flights")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Flights retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "All Flights JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve flights."
    exit 1
  fi
}

clear_flights() {
  echo "Clearing all flights..."
  response=$(curl -s -X POST "$BASE_URL/flights/clear")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Flights cleared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Clear Flights JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to clear flights."
    exit 1
  fi
}

filter_flights_by_airline() {
  local airline_code=$1
  echo "Filtering flights by airline: $airline_code..."
  response=$(curl -s -X GET "$BASE_URL/flights/airline/$airline_code")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Flights filtered by airline successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Flights by Airline JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to filter flights by airline."
    exit 1
  fi
}

filter_flights_by_price() {
  local min_price=$1
  local max_price=$2
  echo "Filtering flights by price range: $min_price - $max_price..."
  response=$(curl -s -X GET "$BASE_URL/flights/price?min=$min_price&max=$max_price")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Flights filtered by price successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Flights by Price JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to filter flights by price."
    exit 1
  fi
}

filter_flights_by_origin() {
  local origin_code=$1
  echo "Filtering flights by origin: $origin_code..."
  response=$(curl -s -X GET "$BASE_URL/flights/origin/$origin_code")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Flights filtered by origin successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Flights by Origin JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to filter flights by origin."
    exit 1
  fi
}

# Run health checks
check_health
check_db

# Clear any existing flights
clear_flights

# Test flight search
search_flights "JFK" "LAX" "2024-07-15" "2024-07-22" 2
search_flights "ORD" "SFO" "2024-08-10"

# Retrieve all flights
get_all_flights

# Test filtering
filter_flights_by_airline "AA"
filter_flights_by_price 100 500
filter_flights_by_origin "JFK"

# Clear flights again
clear_flights

echo "All flight API smoke tests passed successfully!"