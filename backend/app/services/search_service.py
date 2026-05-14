from typing import Optional
from app.models import SearchRequest, SearchResponse, ReasoningStep, POI, Location
from app.services import llm
from app.services import osm
from app.services.inpost import InPostService

inpost_service = InPostService()

# Polish city name fallback — used when Nominatim is unreachable or returns
# an unexpected local name that the InPost API would not recognize.
_CITY_FALLBACK: dict[str, str] = {
    "warsaw": "Warszawa",
    "krakow": "Kraków",
    "gdansk": "Gdańsk",
    "wroclaw": "Wrocław",
    "poznan": "Poznań",
    "lodz": "Łódź",
}

async def execute_search(request: SearchRequest) -> SearchResponse:
    reasoning = []

    extraction = await llm.extract_entities(request.query)

    city = extraction.get("city")
    poi_type = extraction.get("poi_type")
    street_address = extraction.get("street_address")

    reasoning.append(ReasoningStep(
        step="LLM Extraction",
        details={"city": city, "poi_type": poi_type, "street_address": street_address, "constraints": extraction.get("constraints")}
    ))

    if not city:
        reasoning.append(ReasoningStep(
            step="Error",
            details={"message": "Could not identify a city from the query. Try including a city name (e.g. 'near a park in Warsaw')."}
        ))
        return SearchResponse(city="Unknown", poi_type=None, pois=[], inpost_points=[], reasoning=reasoning)

    # Resolve localized city name and center coordinates.
    # Nominatim is tried first; fallback map used if it fails.
    city_center = await osm.get_city_center(city)
    if city_center:
        local_city = city_center["local_name"]
        city_lat, city_lon = city_center["lat"], city_center["lon"]
    else:
        local_city = _CITY_FALLBACK.get(city.lower(), city)
        city_lat, city_lon = None, None

    # --- Address-based flow ---
    if street_address:
        ref = await osm.geocode_address(street_address, city)
        if ref:
            local_city = ref.get("local_name", local_city)
            reasoning.append(ReasoningStep(
                step="Address Geocoding",
                details={"address": f"{street_address}, {city}", "lat": ref["lat"], "lon": ref["lon"]}
            ))
            all_points = await inpost_service.get_points(city=local_city)
            
            for pt in all_points:
                pt.distance_m = round(osm.haversine_m(ref["lat"], ref["lon"], pt.location.lat, pt.location.lon))
            all_points.sort(key=lambda p: p.distance_m)
            closest = all_points[:10]
            
            reasoning.append(ReasoningStep(
                step="Proximity Sort",
                details={"closest_count": len(closest), "nearest_m": closest[0].distance_m if closest else None}
            ))
            return SearchResponse(
                city=city, poi_type=poi_type, street_address=street_address,
                city_lat=ref["lat"], city_lon=ref["lon"],
                pois=[], inpost_points=closest, reasoning=reasoning
            )
        else:
            reasoning.append(ReasoningStep(
                step="Address Geocoding Failed",
                details={"message": f"Could not geocode '{street_address}' in {city}. Falling back to city-wide search."}
            ))

    # --- City-wide InPost search if no POI provided ---
    if not poi_type:
        reasoning.append(ReasoningStep(
            step="No POI Type",
            details={"message": "No specific POI type found. Showing all InPost points in the city.", "city": local_city}
        ))
        inpost_points = await inpost_service.get_points(city=local_city)
        inpost_points = inpost_points[:25]
        reasoning.append(ReasoningStep(
            step="InPost API Query",
            details={"points_found": len(inpost_points)}
        ))
        return SearchResponse(city=city, poi_type=None, city_lat=city_lat, city_lon=city_lon, pois=[], inpost_points=inpost_points, reasoning=reasoning)

    # --- POI-based flow ---
    pois_raw = await osm.find_pois(city, poi_type)
    reasoning.append(ReasoningStep(
        step="OSM POI Query",
        details={"poi_count": len(pois_raw), "city": city, "poi_type": poi_type}
    ))
    
    pois = []
    for p in pois_raw:
        pois.append(POI(
            id=p["id"],
            name=p["name"],
            type=p["type"],
            location=Location(**p["location"])
        ))
    
    if not pois:
        reasoning.append(ReasoningStep(
            step="OSM No Results",
            details={"message": f"No '{poi_type}' POIs found near {city}. Showing all InPost points in city."}
        ))
        inpost_points = await inpost_service.get_points(city=local_city)
        inpost_points = inpost_points[:25]
        reasoning.append(ReasoningStep(
            step="InPost API Query",
            details={"points_found": len(inpost_points)}
        ))
        return SearchResponse(city=city, poi_type=poi_type, city_lat=city_lat, city_lon=city_lon, pois=[], inpost_points=inpost_points, reasoning=reasoning)
        
    # Calculate Bounding Box of POIs with a tighter, more reasonable buffer
    # 0.005 degrees is roughly 500m
    buffer = 0.005 
    lats = [poi.location.lat for poi in pois]
    lons = [poi.location.lon for poi in pois]
    bbox = (min(lats) - buffer, min(lons) - buffer, max(lats) + buffer, max(lons) + buffer)
    
    reasoning.append(ReasoningStep(
        step="Bounding Box Calculation",
        details={"bbox": bbox, "buffer_deg": buffer}
    ))
    
    inpost_points = await inpost_service.get_points(city=local_city, bbox=bbox)
    inpost_points = inpost_points[:25]
    
    reasoning.append(ReasoningStep(
        step="InPost API Query",
        details={"points_found": len(inpost_points)}
    ))
    
    return SearchResponse(
        city=city,
        poi_type=poi_type,
        city_lat=city_lat,
        city_lon=city_lon,
        pois=pois,
        inpost_points=inpost_points,
        reasoning=reasoning
    )
