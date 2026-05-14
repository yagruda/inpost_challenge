from typing import List, Dict, Any, Tuple, Optional
import httpx
from fastapi import HTTPException
from app.models import InPostPoint, Location
from app.services.http_client import HttpClientManager

class InPostService:
    BASE_URL = "https://api-global-points.easypack24.net/v1/points"

    async def get_points(self, city: str, bbox: Optional[Tuple[float, float, float, float]] = None) -> List[InPostPoint]:
        """
        Fetches InPost points for a specific city and optionally filters them by a bounding box.
        The bounding box is defined as (min_lat, min_lon, max_lat, max_lon).
        """
        try:
            client = HttpClientManager.get_client()
            
            # Use the provided city name directly. Callers should provide localized names if necessary.
            params = {"city": city, "per_page": 500}
            
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"InPost API HTTP Error: {e.response.text}")
            raise HTTPException(status_code=502, detail="InPost service unavailable")
        except httpx.RequestError as e:
            print(f"InPost API Request Error: {e}")
            raise HTTPException(status_code=503, detail="InPost service unreachable")
            
        data = response.json()
        items = data.get("items", [])
        
        points = []
        for item in items:
            lat = item.get("location", {}).get("latitude")
            lon = item.get("location", {}).get("longitude")
            
            if lat is None or lon is None:
                continue
            
            # Filter by bounding box if provided
            if bbox:
                min_lat, min_lon, max_lat, max_lon = bbox
                if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
                    continue
            
            points.append(InPostPoint(
                name=item.get("name", "Unknown"),
                location=Location(lat=lat, lon=lon),
                address=item.get("address", {}),
                status=item.get("status", "Unknown")
            ))
            
        return points
