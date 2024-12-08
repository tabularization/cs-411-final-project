# **Flight Price Tracker**

## **Overview**
The **Flight Price Tracker** application provides an interface for managing and retrieving flight data. It interacts with the Amadeus Flight Offers API to fetch flight details and stores the data in memory for further filtering and retrieval. Users can filter flights by airline, price range, and origin, clear stored flights, and retrieve all flight data.

---

## **Features**
- Fetch real-time flight offers using the Amadeus API.
- Store and manage flight data.
- Filter flights by:
  - Airline
  - Price range
  - Origin airport
- Clear stored flight data.

---

## **Environment Variables**
To run this application, the following environment variables must be defined:

- **`API_KEY`**: Your Amadeus API key.
- **`API_SECRET`**: Your Amadeus API secret.

Create a `.env` file in the root directory and add the following:
```env
API_KEY=your_amadeus_api_key
API_SECRET=your_amadeus_api_secret
```
# Routes Documentation

## 1. Health Check
- **Route:** `/api/health`
- **Request Type:** `GET`
- **Purpose:** Verifies if the application is running.
- **Request Format:** None
- **Response Format:** JSON
  - `status` (String): Health status of the application.
- **Example Request:**
  ```bash
  curl -X GET http://127.0.0.1:5000/api/health
  ```
- **Example Response:**
  ```json
  {
    "status": "healthy"
  }
  ```

---

## 2. Retrieve All Flights
- **Route:** `/api/flights`
- **Request Type:** `GET`
- **Purpose:** Retrieve all stored flight data from memory.
- **Request Body:** None
- **Response Format:** JSON
  - `status` (String): Indicates success or failure.
  - `flights` (List of Objects): List of stored flight details.
- **Example Request:**
  ```bash
  curl -X GET http://127.0.0.1:5000/api/flights
  ```
- **Example Response:**
  ```json
  {
    "status": "success",
    "flights": [
      {
        "airline": "AA",
        "origin": "JFK",
        "destination": "LAX",
        "departureDate": "2024-12-20",
        "returnDate": "2024-12-27",
        "price": "250.00 USD"
      }
    ]
  }
  ```

---

## 3. Clear All Flights
- **Route:** `/api/flights/clear`
- **Request Type:** `POST`
- **Purpose:** Clear all stored flight data from memory.
- **Request Body:** None
- **Response Format:** JSON
  - `status` (String): Indicates success.
  - `message` (String): Confirmation message.
- **Example Request:**
  ```bash
  curl -X POST http://127.0.0.1:5000/api/flights/clear
  ```
- **Example Response:**
  ```json
  {
    "status": "success",
    "message": "All flights have been cleared"
  }
  ```

---

## 4. Search for Flights
- **Route:** `/api/flights/search`
- **Request Type:** `POST`
- **Purpose:** Fetch flights from the Amadeus API and store unique flights in memory.
- **Request Body:** JSON
  - `origin` (String): Origin airport code (required).
  - `destination` (String): Destination airport code (required).
  - `departureDate` (String): Departure date in `YYYY-MM-DD` (required).
  - `returnDate` (String): Return date in `YYYY-MM-DD` (optional).
  - `adults` (Integer): Number of travelers (default: 1).
- **Response Format:** JSON
  - `status` (String): Indicates success.
  - `flights` (List of Objects): Newly fetched flights.
- **Example Request:**
  ```bash
  curl -X POST http://127.0.0.1:5000/api/flights/search \\
       -H "Content-Type: application/json" \\
       -d '{
             "origin": "JFK",
             "destination": "LAX",
             "departureDate": "2024-12-20",
             "returnDate": "2024-12-27",
             "adults": 1
           }'
  ```
- **Example Response:**
  ```json
  {
    "status": "success",
    "flights": [
      {
        "airline": "AA",
        "origin": "JFK",
        "destination": "LAX",
        "departureDate": "2024-12-20",
        "returnDate": "2024-12-27",
        "price": "250.00 USD"
      }
    ]
  }
  ```

---

## 5. Filter Flights by Airline
- **Route:** `/api/flights/airline`
- **Request Type:** `GET`
- **Purpose:** Retrieve flights filtered by a specific airline.
- **Request Body:**
  - `airline_code` (String): IATA code of the airline (required).
- **Response Format:** JSON
  - `status` (String): Indicates success.
  - `flights` (List of Objects): Flights matching the airline code.
- **Example Request:**
  ```bash
  curl -X GET "http://127.0.0.1:5000/api/flights/airline?airline_code=AA"
  ```
- **Example Response:**
  ```json
  {
    "status": "success",
    "flights": [
      {
        "airline": "AA",
        "origin": "JFK",
        "destination": "LAX",
        "departureDate": "2024-12-20",
        "returnDate": "2024-12-27",
        "price": "250.00 USD"
      }
    ]
  }
  ```

---

## 6. Filter Flights by Price Range
- **Route:** `/api/flights/price`
- **Request Type:** `GET`
- **Purpose:** Retrieve flights within a specific price range.
- **Request Body:**
  - `min` (Float): Minimum price in USD (required).
  - `max` (Float): Maximum price in USD (required).
- **Response Format:** JSON
  - `status` (String): Indicates success.
  - `flights` (List of Objects): Flights within the price range.
- **Example Request:**
  ```bash
  curl -X GET "http://127.0.0.1:5000/api/flights/price?min=200&max=500"
  ```
- **Example Response:**
  ```json
  {
    "status": "success",
    "flights": [
      {
        "airline": "AA",
        "origin": "JFK",
        "destination": "LAX",
        "departureDate": "2024-12-20",
        "returnDate": "2024-12-27",
        "price": "250.00 USD"
      }
    ]
  }
  ```

---

## 7. Filter Flights by Origin
- **Route:** `/api/flights/origin`
- **Request Type:** `GET`
- **Purpose:** Retrieve flights filtered by origin airport.
- **Request Body:**
  - `origin_code` (String): IATA code of the origin airport (required).
- **Response Format:** JSON
  - `status` (String): Indicates success.
  - `flights` (List of Objects): Flights departing from the origin airport.
- **Example Request:**
  ```bash
  curl -X GET "http://127.0.0.1:5000/api/flights/origin?origin_code=JFK"
  ```
- **Example Response:**
  ```json
  {
    "status": "success",
    "flights": [
      {
        "airline": "AA",
        "origin": "JFK",
        "destination": "LAX",
        "departureDate": "2024-12-20",
        "returnDate": "2024-12-27",
        "price": "250.00 USD"
      }
    ]
  }
  ```
