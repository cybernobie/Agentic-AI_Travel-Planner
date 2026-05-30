import json
import os
import requests
from langchain.tools import tool

# Load JSON Data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(filename):
    """
    Utility function to load static mock data (flights, hotels, places) from JSON files.
    This is used to simulate a database or external API for the tools to query.
    """
    with open(os.path.join(BASE_DIR, filename), 'r') as f:
        return json.load(f)

flights_data = load_json('flights.json')
hotels_data = load_json('hotels.json')
places_data = load_json('places.json')

# City Coordinates for Open-Meteo
CITY_COORDS = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Goa": {"lat": 15.2993, "lon": 74.1240}
}

@tool
def flight_search(source: str, destination: str) -> str:
    """
    Search for flights between a source and destination city.
    Returns a list of available flights sorted by price.
    Why it is used: Used by the AI agent to find and select the best flight options for the user's itinerary based on real available data.
    """
    results = [f for f in flights_data if f['from'].lower() == source.lower() and f['to'].lower() == destination.lower()]
    if not results:
        return f"No flights found from {source} to {destination}."
    
    results = sorted(results, key=lambda x: x['price'])
    formatted = []
    for r in results:
        formatted.append(f"- {r['airline']} (Flight {r['flight_id']}): {r['departure_time']} to {r['arrival_time']} | Price: ₹{r['price']}")
    
    return "Available Flights:\n" + "\n".join(formatted)

@tool
def hotel_recommendation(city: str) -> str:
    """
    Get hotel recommendations for a specific city.
    Returns a list of top hotels available in the city.
    Why it is used: Used by the AI agent to select appropriate accommodation for the user based on the destination city and implicit preferences.
    """
    results = [h for h in hotels_data if h['city'].lower() == city.lower()]
    if not results:
        return f"No hotels found in {city}."
    
    # Sort by stars (descending) and price (ascending)
    results = sorted(results, key=lambda x: (-x['stars'], x['price_per_night']))
    formatted = []
    for r in results[:10]: # Return top 10
        amenities = ", ".join(r['amenities'])
        formatted.append(f"- {r['name']} ({r['stars']} Stars): ₹{r['price_per_night']}/night | Amenities: {amenities}")
    
    return f"Hotel Recommendations in {city}:\n" + "\n".join(formatted)

@tool
def places_discovery(city: str) -> str:
    """
    Discover top attractions and places to visit in a specific city.
    Returns a list of popular places.
    Why it is used: Used by the AI agent to build the day-wise itinerary with relevant attractions and activities for the destination.
    """
    results = [p for p in places_data if p['city'].lower() == city.lower()]
    if not results:
        return f"No places found for {city}."
    
    results = sorted(results, key=lambda x: -x['rating'])
    formatted = []
    for r in results[:10]:
        formatted.append(f"- {r['name']} (Type: {r['type'].title()}) | Rating: {r['rating']}")
    
    return f"Top Places to Visit in {city}:\n" + "\n".join(formatted)

@tool
def weather_lookup(city: str) -> str:
    """
    Get the weather forecast for a specific city.
    Returns the maximum temperature for the next 7 days.
    Why it is used: Used by the AI agent to provide weather context in the itinerary, helping the user pack and plan outdoor activities accordingly.
    """
    coords = CITY_COORDS.get(city.title())
    if not coords:
        return f"Coordinates for {city} are not available."
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&daily=temperature_2m_max&timezone=auto"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        dates = data['daily']['time']
        temps = data['daily']['temperature_2m_max']
        
        formatted = []
        for d, t in zip(dates, temps):
            formatted.append(f"{d}: {t}°C")
            
        return f"7-Day Weather Forecast for {city}:\n" + "\n".join(formatted)
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

@tool
def budget_estimation(flight_cost: float, hotel_cost_per_night: float, num_nights: int, daily_food_travel_cost: float) -> str:
    """
    Estimate the total budget for the trip.
    Provide the selected flight cost, hotel cost per night, number of nights, and estimated daily food/travel cost.
    Returns the budget breakdown and total.
    Why it is used: Used by the AI agent to calculate and present a comprehensive cost estimation for the entire trip.
    """
    hotel_total = hotel_cost_per_night * num_nights
    food_travel_total = daily_food_travel_cost * (num_nights + 1) # Assuming days = nights + 1
    total_cost = flight_cost + hotel_total + food_travel_total
    
    breakdown = (
        f"Budget Breakdown:\n"
        f"- Flight Cost: ₹{flight_cost}\n"
        f"- Hotel Cost ({num_nights} nights): ₹{hotel_total}\n"
        f"- Food & Local Travel ({num_nights + 1} days): ₹{food_travel_total}\n"
        f"-------------------------------------\n"
        f"Total Estimated Cost: ₹{total_cost}"
    )
    return breakdown

# List of all tools
get_tools = [flight_search, hotel_recommendation, places_discovery, weather_lookup, budget_estimation]
