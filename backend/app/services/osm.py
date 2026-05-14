import httpx
import math
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.services.http_client import HttpClientManager

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Returns the distance in metres between two lat/lon points."""
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

async def geocode_address(address: str, city: str) -> Optional[Dict[str, float]]:
    """Geocode a street address within a city, returning lat/lon or None."""
    query = f"{address}, {city}"
    try:
        client = HttpClientManager.get_client()
        resp = await client.get(
            NOMINATIM_URL,
            params={"q": query, "format": "json", "limit": 1, "addressdetails": 1},
            headers={"User-Agent": "InPost-Internship-Demo/1.0"}
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            address_details = data[0].get("address", {})
            local_city = address_details.get("city") or address_details.get("town") or address_details.get("village") or city
            return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"]), "local_name": local_city}
    except httpx.HTTPStatusError as e:
        print(f"Nominatim geocode HTTP error: {e}")
        raise HTTPException(status_code=502, detail="Geocoding service unavailable")
    except httpx.RequestError as e:
        print(f"Nominatim geocode request error: {e}")
        raise HTTPException(status_code=503, detail="Geocoding service unreachable")
    return None

async def get_city_center(city: str) -> Optional[Dict[str, float]]:
    """Geocode city to get its lat/lon."""
    try:
        client = HttpClientManager.get_client()
        # Request 'addressdetails=1' to get localized city names
        resp = await client.get(
            NOMINATIM_URL,
            params={"q": city, "format": "json", "limit": 1, "addressdetails": 1},
            headers={"User-Agent": "InPost-Internship-Demo/1.0"}
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            # Try to extract the localized (Polish) city name if available, fallback to the query city
            address_details = data[0].get("address", {})
            local_city = address_details.get("city") or address_details.get("town") or address_details.get("village") or city
            
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"]),
                "local_name": local_city
            }
    except httpx.HTTPStatusError as e:
        print(f"Nominatim Error: {e}")
        raise HTTPException(status_code=502, detail="Geocoding service unavailable")
    except httpx.RequestError as e:
        print(f"Nominatim request error: {e}")
        raise HTTPException(status_code=503, detail="Geocoding service unreachable")
    return None

async def find_pois(city: str, poi_type: str) -> List[Dict[str, Any]]:
    """Find Points of Interest in a given city using Overpass API."""
    if not poi_type:
        return []

    # Get coordinates of the city
    center = await get_city_center(city)
    if not center:
        return []
        
    lat = center["lat"]
    lon = center["lon"]
    radius = 2000 # 2km search radius
    poi_type = poi_type.lower()
    
    # Exact match for amenity/shop is much faster than case-insensitive regex
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="{poi_type}"](around:{radius},{lat},{lon});
      node["shop"="{poi_type}"](around:{radius},{lat},{lon});
      way["amenity"="{poi_type}"](around:{radius},{lat},{lon});
      way["shop"="{poi_type}"](around:{radius},{lat},{lon});
    );
    out center 10;
    """
    
    try:
        client = HttpClientManager.get_client()
        resp = await client.post(
            OVERPASS_URL, 
            data={"data": query},
            headers={"User-Agent": "InPost-Internship-Demo/1.0"}
        )
        resp.raise_for_status()
        data = resp.json()
        
        pois = []
        for element in data.get("elements", []):
            lat = element.get("lat") or element.get("center", {}).get("lat")
            lon = element.get("lon") or element.get("center", {}).get("lon")
            
            if lat and lon:
                tags = element.get("tags", {})
                name = tags.get("name", f"Unnamed {poi_type.capitalize()}")
                
                pois.append({
                    "id": str(element.get("id")),
                    "name": name,
                    "type": poi_type,
                    "location": {"lat": lat, "lon": lon}
                })
        return pois
    except httpx.HTTPStatusError as e:
        print(f"Overpass HTTP Error: {e.response.text}")
        raise HTTPException(status_code=502, detail="OSM Overpass service unavailable")
    except httpx.RequestError as e:
        print(f"Overpass Request Error: {e}")
        raise HTTPException(status_code=503, detail="OSM Overpass service unreachable")
