from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SearchRequest(BaseModel):
    query: str

class Location(BaseModel):
    lat: float
    lon: float

class POI(BaseModel):
    id: str
    name: str
    type: str
    location: Location

class InPostPoint(BaseModel):
    name: str
    location: Location
    address: Dict[str, Any]
    status: str
    distance_m: Optional[float] = None  # Distance from reference point, if applicable

class ReasoningStep(BaseModel):
    step: str
    details: Dict[str, Any]

class SearchResponse(BaseModel):
    city: str
    poi_type: Optional[str] = None
    street_address: Optional[str] = None
    city_lat: Optional[float] = None
    city_lon: Optional[float] = None
    pois: List[POI]
    inpost_points: List[InPostPoint]
    reasoning: List[ReasoningStep]
