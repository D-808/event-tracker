import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class ArtistTourTracker:
    """
    Ticketmaster Discovery API.
    Free API key at: https://developer.ticketmaster.com/
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://app.ticketmaster.com/discovery/v2"
    
    def search_events(self, 
                     artist_name: Optional[str] = None,
                     city: Optional[str] = None,
                     country_code: Optional[str] = None,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     size: int = 20) -> List[Dict]:
        """
        Search for events by artist, location, and date range.
        
        Args:
            artist_name: Name of the artist/band
            city: City name
            country_code: Two-letter country code (e.g., 'US', 'GB', 'IE')
            start_date: Start date in YYYY-MM-DDTHH:mm:ssZ format
            end_date: End date in YYYY-MM-DDTHH:mm:ssZ format
            size: Number of results (max 200)
        """
        endpoint = f"{self.base_url}/events.json"
        
        params = {
            "apikey": self.api_key,
            "size": size,
            "sort": "date,asc"
        }
        
        if artist_name:
            params["keyword"] = artist_name
        if city:
            params["city"] = city
        if country_code:
            params["countryCode"] = country_code
        if start_date:
            params["startDateTime"] = start_date
        if end_date:
            params["endDateTime"] = end_date
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "_embedded" in data and "events" in data["_embedded"]:
                return self._parse_events(data["_embedded"]["events"])
            return []
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching events: {e}")
            return []
    
    def _parse_events(self, events: List[Dict]) -> List[Dict]:
        """Parse raw event data into clean format."""
        parsed_events = []
        
        for event in events:
            parsed = {
                "name": event.get("name", "Unknown Event"),
                "date": event.get("dates", {}).get("start", {}).get("localDate", "TBA"),
                "time": event.get("dates", {}).get("start", {}).get("localTime", "TBA"),
                "url": event.get("url", ""),
                "venue": {},
                "artists": []
            }
            
            # Extract venue info
            if "_embedded" in event and "venues" in event["_embedded"]:
                venue = event["_embedded"]["venues"][0]
                parsed["venue"] = {
                    "name": venue.get("name", "Unknown Venue"),
                    "city": venue.get("city", {}).get("name", "Unknown"),
                    "country": venue.get("country", {}).get("name", "Unknown"),
                    "address": venue.get("address", {}).get("line1", "N/A")
                }
            
            # Extract artist info
            if "_embedded" in event and "attractions" in event["_embedded"]:
                for attraction in event["_embedded"]["attractions"]:
                    parsed["artists"].append({
                        "name": attraction.get("name", "Unknown"),
                        "genre": attraction.get("classifications", [{}])[0].get("genre", {}).get("name", "Unknown")
                    })
            
            parsed_events.append(parsed)
        
        return parsed_events
    
    def track_multiple_artists(self, artists: List[str], **kwargs) -> Dict[str, List[Dict]]:
        """Track multiple artists at once."""
        results = {}
        
        for artist in artists:
            print(f"Searching for {artist}...")
            events = self.search_events(artist_name=artist, **kwargs)
            results[artist] = events
        
        return results
    
    def print_events(self, events: List[Dict]):
        """Pretty print event list."""
        if not events:
            print("No events found.")
            return
        
        for i, event in enumerate(events, 1):
            print(f"\n{i}. {event['name']}")
            print(f"   Date: {event['date']} at {event['time']}")
            print(f"   Venue: {event['venue'].get('name', 'N/A')}")
            print(f"   Location: {event['venue'].get('city', 'N/A')}, {event['venue'].get('country', 'N/A')}")
            if event['artists']:
                artists = ", ".join([a['name'] for a in event['artists']])
                print(f"   Artists: {artists}")
            print(f"   Tickets: {event['url']}")


# Example usage
if __name__ == "__main__":
    print("=== Ticketmaster Artist Tour Tracker ===")
    print("Get your free API key at: https://developer.ticketmaster.com/\n")
    
    # Try to get API key from environment variable first
    API_KEY = os.getenv('TICKETMASTER_API_KEY')
    
    if not API_KEY:
        API_KEY = input("Enter your Ticketmaster API key: ").strip()
    
    if not API_KEY:
        print("Error: API key is required!")
        exit(1)
    
    tracker = ArtistTourTracker(API_KEY)
    
    # Prompt for country code
    print("\nSupported country codes: US, GB, IE, CA, AU, DE, FR, ES, IT, NL, BE, etc.")
    print("(Use ISO 3166-1 alpha-2 country codes)\n")
    country_code = input("Enter country code (e.g., NL for Netherlands): ").strip().upper()
    
    if not country_code or len(country_code) != 2:
        print("Error: Please enter a valid 2-letter country code!")
        exit(1)
    
    # Prompt for city (optional)
    print("\nEnter a city to narrow down results, or press Enter to search entire country")
    print("Examples: Amsterdam, Rotterdam, Utrecht, etc.\n")
    city = input("Enter city name (optional): ").strip()
    
    if city:
        print(f"\nSearching for events in {city}, {country_code}")
    else:
        print(f"\nSearching for events in all of {country_code}")
    
    # Calculate date range (next 14 days)
    from datetime import datetime, timedelta
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)
    
    # Format dates for API (ISO 8601 format)
    start_date_str = start_date.strftime("%Y-%m-%dT00:00:00Z")
    end_date_str = end_date.strftime("%Y-%m-%dT23:59:59Z")
    
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("Fetching events...\n")
    
    # Search for events with optional city filter
    events = tracker.search_events(
        country_code=country_code,
        city=city if city else None,
        start_date=start_date_str,
        end_date=end_date_str,
        size=200  # Max per request
    )
    
    location_str = f"{city}, {country_code}" if city else country_code
    print(f"\n=== Found {len(events)} events in {location_str} ===")
    tracker.print_events(events)
    
    # Save to JSON
    output_data = {
        "country": country_code,
        "city": city if city else "All cities",
        "date_range": {
            "start": start_date.strftime('%Y-%m-%d'),
            "end": end_date.strftime('%Y-%m-%d')
        },
        "total_events": len(events),
        "events": events
    }
    
    filename_city = f"_{city.lower().replace(' ', '_')}" if city else ""
    filename = f"events_{country_code.lower()}{filename_city}_{start_date.strftime('%Y%m%d')}.json"
    with open(filename, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\n\nResults saved to {filename}")