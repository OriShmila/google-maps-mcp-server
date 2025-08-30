# Google Maps MCP Server

A Model Context Protocol (MCP) server that provides access to Google Maps APIs. This server enables AI assistants to geocode addresses, search for places, get directions, calculate distances, retrieve elevation data, and more using Google Maps services.

## Features

This MCP server provides the following tools:

### 🗺️ Core Mapping Tools
- **`maps_geocode`** - Convert addresses to coordinates
- **`maps_reverse_geocode`** - Convert coordinates to addresses  
- **`maps_search_places`** - Search for places by query
- **`maps_place_details`** - Get detailed information about places

### 🚗 Navigation & Distance Tools  
- **`maps_directions`** - Get turn-by-turn directions between locations
- **`maps_distance_matrix`** - Calculate travel time/distance for multiple origin/destination pairs

### 🏔️ Geographic Data Tools
- **`maps_elevation`** - Get elevation data for locations

## Installation

### Prerequisites

1. **Google Maps API Key**: Get your API key from the [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable Required APIs**: Make sure the following APIs are enabled for your project:
   - Geocoding API
   - Places API (New) - *Replaces legacy Places API*
   - Routes API - *Replaces legacy Directions API and Distance Matrix API*
   - Elevation API

**Note**: This server uses the official `googlemaps` Python package which automatically handles the newer API versions and ensures compatibility with Google's latest services. This eliminates legacy API issues and provides robust, future-proof integration.

### Install from GitHub

```bash
# Install using uvx (recommended)
uvx --from git+https://github.com/yourusername/google-maps-mcp-server google-maps-server

# Or install using pip
pip install git+https://github.com/yourusername/google-maps-mcp-server
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/google-maps-mcp-server
cd google-maps-mcp-server

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env and add your Google Maps API key

# Test the server
uv run python test_server.py

# Run the server
uv run python main.py
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required: Your Google Maps API Key
GOOGLE_MAPS_API_KEY=your_api_key_here

# Optional: Enable debug logging  
DEBUG=true
```

### MCP Client Configuration

Add this to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "google-maps": {
      "command": "uvx",
      "args": [
        "--from", 
        "git+https://github.com/yourusername/google-maps-mcp-server",
        "google-maps-server"
      ],
      "env": {
        "GOOGLE_MAPS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Usage Examples

### Geocoding
```python
# Convert address to coordinates
{
  "tool": "maps_geocode",
  "arguments": {
    "address": "1600 Amphitheatre Parkway, Mountain View, CA"
  }
}
```

### Place Search
```python
# Search for restaurants near a location
{
  "tool": "maps_search_places", 
  "arguments": {
    "query": "restaurants",
    "location": {"latitude": 37.7749, "longitude": -122.4194},
    "radius": 5000
  }
}
```

### Directions
```python
# Get driving directions
{
  "tool": "maps_directions",
  "arguments": {
    "origin": "San Francisco, CA",
    "destination": "Los Angeles, CA", 
    "mode": "driving"
  }
}
```

### Distance Matrix
```python
# Calculate distances between multiple points
{
  "tool": "maps_distance_matrix",
  "arguments": {
    "origins": ["San Francisco, CA", "Oakland, CA"],
    "destinations": ["Los Angeles, CA", "San Diego, CA"],
    "mode": "driving"
  }
}
```

## API Reference

### maps_geocode
Convert an address into geographic coordinates.

**Parameters:**
- `address` (string, required): The address to geocode

**Returns:** Location coordinates, formatted address, and place ID

### maps_reverse_geocode  
Convert coordinates into an address.

**Parameters:**
- `latitude` (number, required): Latitude coordinate (-90 to 90)
- `longitude` (number, required): Longitude coordinate (-180 to 180)

**Returns:** Formatted address, place ID, and address components

### maps_search_places
Search for places using text queries.

**Parameters:**
- `query` (string, required): Search query
- `location` (object, optional): Center point with latitude/longitude
- `radius` (number, optional): Search radius in meters (max 50,000)

**Returns:** Array of places with names, addresses, coordinates, ratings, and types

### maps_place_details
Get detailed information about a specific place.

**Parameters:**
- `place_id` (string, required): Google Places place ID

**Returns:** Detailed place information including contact info, hours, reviews

### maps_directions
Get turn-by-turn directions between locations.

**Parameters:**
- `origin` (string, required): Starting location
- `destination` (string, required): Ending location  
- `mode` (string, optional): Travel mode (driving, walking, bicycling, transit)

**Returns:** Route information with steps, distance, and duration

### maps_distance_matrix
Calculate travel distance and time for multiple origin/destination pairs.

**Parameters:**
- `origins` (array, required): Array of origin locations
- `destinations` (array, required): Array of destination locations
- `mode` (string, optional): Travel mode (driving, walking, bicycling, transit)

**Returns:** Distance and duration matrix for all origin/destination combinations

### maps_elevation
Get elevation data for locations.

**Parameters:**
- `locations` (array, required): Array of objects with latitude/longitude

**Returns:** Elevation data in meters for each location

## Development

### Running Tests

```bash
# Run all test cases
uv run python test_server.py

# Run with verbose output
uv run python test_server.py --verbose
```

### Project Structure

```
google-maps-mcp-server/
├── google_maps_mcp_server/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py          # MCP server implementation
│   ├── handlers.py        # Google Maps API handlers
│   └── tools.json         # Tool schema definitions
├── test_cases.json        # Test cases for all tools
├── test_server.py         # Test runner
├── main.py               # Server entry point
├── pyproject.toml        # Project configuration
└── README.md
```

## Error Handling

The server includes comprehensive error handling for:

- Missing or invalid API keys
- Invalid coordinates (out of range)
- Missing required parameters
- Google Maps API errors
- Network connectivity issues
- Invalid travel modes
- Malformed requests

## Rate Limits & Quotas

Be aware of Google Maps API quotas and rate limits:

- **Geocoding API**: 40,000 requests per month (free tier)
- **Places API**: Varies by request type
- **Distance Matrix API**: 40,000 elements per month
- **Directions API**: 40,000 requests per month
- **Elevation API**: 40,000 requests per month

See [Google Maps Platform pricing](https://developers.google.com/maps/pricing-and-plans) for current limits.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- [MCP Specification](https://github.com/modelcontextprotocol/specification)
- [Issues](https://github.com/yourusername/google-maps-mcp-server/issues)