#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Test user credentials
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
TEST_USERNAME="smoketest_user_$TIMESTAMP"
TEST_PASSWORD="initial_password"
TEST_NEW_PASSWORD="updated_password"

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
# Login Functionality Tests
#
###############################################

create_account() {
  echo "Creating test account..."
  account_data="{\"username\":\"$TEST_USERNAME\",\"password\":\"$TEST_PASSWORD\"}"
  
  response=$(curl -s -X POST -H "Content-Type: application/json" -d "$account_data" "$BASE_URL/../create-account")
  
  if echo "$response" | grep -q '"message": "Account created successfully"'; then
    echo "Account creation successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Create Account JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Account creation failed."
    echo "Response: $response"
    exit 1
  fi
}

test_login() {
  echo "Testing login with valid credentials..."
  login_data="{\"username\":\"$TEST_USERNAME\",\"password\":\"$TEST_PASSWORD\"}"
  
  response=$(curl -s -X POST -H "Content-Type: application/json" -d "$login_data" "$BASE_URL/../login")
  
  if echo "$response" | grep -q '"message": "Login successful"'; then
    echo "Login successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Login failed."
    echo "Response: $response"
    exit 1
  fi
}

test_failed_login() {
  echo "Testing login with incorrect password..."
  login_data="{\"username\":\"$TEST_USERNAME\",\"password\":\"wrong_password\"}"
  
  response=$(curl -s -X POST -H "Content-Type: application/json" -d "$login_data" "$BASE_URL/../login")
  
  if echo "$response" | grep -q '"error": "Invalid username or password"'; then
    echo "Failed login test passed - incorrect password rejected."
    if [ "$ECHO_JSON" = true ]; then
      echo "Failed Login JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed login test failed."
    echo "Response: $response"
    exit 1
  fi
}

test_duplicate_account() {
  echo "Testing creation of duplicate account..."
  account_data="{\"username\":\"$TEST_USERNAME\",\"password\":\"another_password\"}"
  
  response=$(curl -s -X POST -H "Content-Type: application/json" -d "$account_data" "$BASE_URL/../create-account")
  
  if echo "$response" | grep -q '"error": "Username already exists"'; then
    echo "Duplicate account creation test passed - duplicate username rejected."
    if [ "$ECHO_JSON" = true ]; then
      echo "Duplicate Account JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Duplicate account test failed."
    echo "Response: $response"
    exit 1
  fi
}

update_password() {
  echo "Updating account password..."
  update_data="{\"username\":\"$TEST_USERNAME\",\"current_password\":\"$TEST_PASSWORD\",\"new_password\":\"$TEST_NEW_PASSWORD\"}"
  
  response=$(curl -s -X PUT -H "Content-Type: application/json" -d "$update_data" "$BASE_URL/../update-password")
  
  if echo "$response" | grep -q '"message": "Password updated successfully"'; then
    echo "Password update successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Update Password JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Password update failed."
    echo "Response: $response"
    exit 1
  fi
}

test_updated_login() {
  echo "Testing login with new password..."
  login_data="{\"username\":\"$TEST_USERNAME\",\"password\":\"$TEST_NEW_PASSWORD\"}"
  
  response=$(curl -s -X POST -H "Content-Type: application/json" -d "$login_data" "$BASE_URL/../login")
  
  if echo "$response" | grep -q '"message": "Login successful"'; then
    echo "Login with new password successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Updated Login JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Login with new password failed."
    echo "Response: $response"
    exit 1
  fi
}

test_invalid_password_update() {
  echo "Testing password update with incorrect current password..."
  update_data="{\"username\":\"$TEST_USERNAME\",\"current_password\":\"wrong_password\",\"new_password\":\"another_new_password\"}"
  
  response=$(curl -s -X PUT -H "Content-Type: application/json" -d "$update_data" "$BASE_URL/../update-password")
  
  if echo "$response" | grep -q '"error": "Current password is incorrect"'; then
    echo "Invalid password update test passed - incorrect current password rejected."
    if [ "$ECHO_JSON" = true ]; then
      echo "Invalid Password Update JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Invalid password update test failed."
    echo "Response: $response"
    exit 1
  fi
}

###############################################
#
# Flight Search Tests
#
###############################################

# search_flights() {
#   local origin=$1
#   local destination=$2
#   local departure_date=$3
#   local return_date=$4
#   local adults=${5:-1}

#   echo "Searching flights from $origin to $destination on $departure_date..."
#   flight_data="{\"origin\":\"$origin\",\"destination\":\"$destination\",\"departureDate\":\"$departure_date\""
  
#   if [ ! -z "$return_date" ]; then
#     flight_data+=",\"returnDate\":\"$return_date\""
#   fi
  
#   flight_data+=",\"adults\":$adults}"

#   response=$(curl -s -X POST -H "Content-Type: application/json" -d "$flight_data" "$BASE_URL/flights/search")
  
#   if echo "$response" | grep -q '"status": "success"'; then
#     echo "Flight search successful."
#     if [ "$ECHO_JSON" = true ]; then
#       echo "Flight Search JSON:"
#       echo "$response" | jq .
#     fi
#   else
#     echo "Flight search failed."
#     echo "Response: $response"
#     exit 1
#   fi
# }

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

#Run login checks
create_account
test_login
test_failed_login
test_duplicate_account
update_password
test_updated_login
test_invalid_password_update

# Clear any existing flights
clear_flights

# Retrieve all flights
get_all_flights

# Test filtering
filter_flights_by_airline "AA"
filter_flights_by_price 100 500
filter_flights_by_origin "JFK"

# Clear flights again
clear_flights

echo "All flight API smoke tests passed successfully!"