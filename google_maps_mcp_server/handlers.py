"""
Google Maps MCP Server Handlers

This module implements all Google Maps API tool handlers for the MCP server.
Each handler corresponds to a tool defined in tools.json and provides access
to different Google Maps APIs.
"""

import os
from typing import Dict, List, Any, Optional
import googlemaps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Initialize Google Maps client
gmaps = None


def get_gmaps_client() -> googlemaps.Client:
    """Get or create the Google Maps client."""
    global gmaps
    if gmaps is None:
        if not GOOGLE_MAPS_API_KEY:
            raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    return gmaps


# ============================================================================
# Google Maps Tool Handlers using the official googlemaps package
# ============================================================================


async def maps_geocode(address: str) -> Dict[str, Any]:
    """Convert an address into geographic coordinates."""
    if not address:
        raise ValueError("address parameter is required")

    try:
        gmaps_client = get_gmaps_client()
        results = gmaps_client.geocode(address)

        if not results:
            raise ValueError("No results found for the given address")

        result = results[0]
        return {
            "location": result["geometry"]["location"],
            "formatted_address": result["formatted_address"],
            "place_id": result["place_id"],
        }
    except Exception as e:
        raise ValueError(f"Geocoding error: {e}")


async def maps_reverse_geocode(latitude: float, longitude: float) -> Dict[str, Any]:
    """Convert coordinates into an address."""
    if latitude is None or longitude is None:
        raise ValueError("latitude and longitude parameters are required")

    # Validate coordinate ranges
    if not (-90 <= latitude <= 90):
        raise ValueError("latitude must be between -90 and 90")
    if not (-180 <= longitude <= 180):
        raise ValueError("longitude must be between -180 and 180")

    try:
        gmaps_client = get_gmaps_client()
        results = gmaps_client.reverse_geocode((latitude, longitude))

        if not results:
            raise ValueError("No results found for the given coordinates")

        result = results[0]
        return {
            "formatted_address": result["formatted_address"],
            "place_id": result["place_id"],
            "address_components": result["address_components"],
        }
    except Exception as e:
        raise ValueError(f"Reverse geocoding error: {e}")


async def maps_search_places(
    query: str,
    location: Optional[Dict[str, float]] = None,
    radius: Optional[int] = None,
) -> Dict[str, Any]:
    """Search for places using Google Places API."""
    if not query:
        raise ValueError("query parameter is required")

    # Validate radius if provided
    if radius is not None and (radius <= 0 or radius > 50000):
        raise ValueError("radius must be between 1 and 50000 meters")

    try:
        gmaps_client = get_gmaps_client()

        # Build search parameters
        search_params = {}

        # Validate location if provided
        if location:
            if "latitude" not in location or "longitude" not in location:
                raise ValueError("location must contain both latitude and longitude")

            # Only use location if radius is also provided
            if radius:
                search_params["location"] = (
                    location["latitude"],
                    location["longitude"],
                )
                search_params["radius"] = radius

        results = gmaps_client.places(query=query, **search_params)

        places = []
        for place in results.get("results", []):
            places.append(
                {
                    "name": place.get("name", ""),
                    "formatted_address": place.get("formatted_address", ""),
                    "location": place.get("geometry", {}).get("location", {}),
                    "place_id": place.get("place_id", ""),
                    "rating": place.get("rating"),
                    "types": place.get("types", []),
                }
            )

        return {"places": places}
    except Exception as e:
        raise ValueError(f"Places search error: {e}")


async def maps_place_details(place_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific place."""
    if not place_id:
        raise ValueError("place_id parameter is required")

    try:
        gmaps_client = get_gmaps_client()
        result = gmaps_client.place(
            place_id,
            fields=[
                "name",
                "formatted_address",
                "geometry",
                "formatted_phone_number",
                "website",
                "rating",
                "reviews",
                "opening_hours",
            ],
        )

        place_data = result.get("result", {})

        # Format reviews to match schema
        reviews = []
        for review in place_data.get("reviews", []):
            reviews.append(
                {
                    "author_name": review.get("author_name", ""),
                    "rating": review.get("rating", 0),
                    "text": review.get("text", ""),
                    "time": review.get("time", 0),
                }
            )

        return {
            "name": place_data.get("name", ""),
            "formatted_address": place_data.get("formatted_address", ""),
            "location": place_data.get("geometry", {}).get("location", {}),
            "formatted_phone_number": place_data.get("formatted_phone_number", ""),
            "website": place_data.get("website", ""),
            "rating": place_data.get("rating"),
            "reviews": reviews,
            "opening_hours": place_data.get("opening_hours", {}),
        }
    except Exception as e:
        raise ValueError(f"Place details error: {e}")


async def maps_distance_matrix(
    origins: List[str], destinations: List[str], mode: str = "driving"
) -> Dict[str, Any]:
    """Calculate travel distance and time for multiple origins and destinations."""
    if not origins:
        raise ValueError("origins parameter is required and cannot be empty")
    if not destinations:
        raise ValueError("destinations parameter is required and cannot be empty")

    valid_modes = ["driving", "walking", "bicycling", "transit"]
    if mode not in valid_modes:
        raise ValueError(f"mode must be one of: {', '.join(valid_modes)}")

    try:
        gmaps_client = get_gmaps_client()

        result = gmaps_client.distance_matrix(
            origins=origins, destinations=destinations, mode=mode, units="imperial"
        )

        # Format results to match expected schema
        results = []
        for row in result.get("rows", []):
            elements = []
            for element in row.get("elements", []):
                elements.append(
                    {
                        "status": element.get("status", ""),
                        "duration": element.get("duration"),
                        "distance": element.get("distance"),
                    }
                )
            results.append({"elements": elements})

        return {
            "origin_addresses": result.get("origin_addresses", []),
            "destination_addresses": result.get("destination_addresses", []),
            "results": results,
        }
    except Exception as e:
        raise ValueError(f"Distance matrix error: {e}")


async def maps_elevation(locations: List[Dict[str, float]]) -> Dict[str, Any]:
    """Get elevation data for locations on the earth."""
    if not locations:
        raise ValueError("locations parameter is required and cannot be empty")

    # Validate location format
    location_tuples = []
    for loc in locations:
        if "latitude" not in loc or "longitude" not in loc:
            raise ValueError("Each location must contain both latitude and longitude")

        lat, lng = loc["latitude"], loc["longitude"]
        if not (-90 <= lat <= 90):
            raise ValueError(f"latitude {lat} must be between -90 and 90")
        if not (-180 <= lng <= 180):
            raise ValueError(f"longitude {lng} must be between -180 and 180")

        location_tuples.append((lat, lng))

    try:
        gmaps_client = get_gmaps_client()
        result = gmaps_client.elevation(location_tuples)

        results = []
        for elevation_result in result:
            results.append(
                {
                    "elevation": elevation_result.get("elevation", 0),
                    "location": elevation_result.get("location", {}),
                    "resolution": elevation_result.get("resolution", 0),
                }
            )

        return {"results": results}
    except Exception as e:
        raise ValueError(f"Elevation error: {e}")


async def maps_directions(
    origin: str, destination: str, mode: str = "driving"
) -> Dict[str, Any]:
    """Get directions between two points."""
    if not origin:
        raise ValueError("origin parameter is required")
    if not destination:
        raise ValueError("destination parameter is required")

    valid_modes = ["driving", "walking", "bicycling", "transit"]
    if mode not in valid_modes:
        raise ValueError(f"mode must be one of: {', '.join(valid_modes)}")

    try:
        gmaps_client = get_gmaps_client()

        result = gmaps_client.directions(
            origin=origin, destination=destination, mode=mode, units="imperial"
        )

        routes = []
        for route in result:
            # Get the first leg for basic route info
            leg = route.get("legs", [{}])[0]

            steps = []
            for step in leg.get("steps", []):
                steps.append(
                    {
                        "instructions": step.get("html_instructions", ""),
                        "distance": step.get("distance"),
                        "duration": step.get("duration"),
                        "travel_mode": step.get("travel_mode", ""),
                    }
                )

            routes.append(
                {
                    "summary": route.get("summary", ""),
                    "distance": leg.get("distance"),
                    "duration": leg.get("duration"),
                    "steps": steps,
                }
            )

        return {"routes": routes}
    except Exception as e:
        raise ValueError(f"Directions error: {e}")


# ============================================================================
# Tool Functions Mapping
# ============================================================================

TOOL_FUNCTIONS = {
    "maps_geocode": maps_geocode,
    "maps_reverse_geocode": maps_reverse_geocode,
    "maps_search_places": maps_search_places,
    "maps_place_details": maps_place_details,
    "maps_distance_matrix": maps_distance_matrix,
    "maps_elevation": maps_elevation,
    "maps_directions": maps_directions,
}
