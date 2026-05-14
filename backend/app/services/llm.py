import os
import json
from google import genai
from google.genai import types
from typing import Dict, Any

api_key = os.getenv("GEMINI_API_KEY", "").strip()
if not api_key:
    api_key = "mock-key"

client = genai.Client(api_key=api_key) if api_key != "mock-key" else None

async def extract_entities(query: str) -> Dict[str, Any]:
    """
    Extract city and POI type from natural language query using LLM.
    Returns a dict with 'city', 'poi_type', and 'constraints'.
    """
    # Fallback to mock if no API key is provided
    if api_key == "mock-key" or not api_key:
        return _mock_extract(query)
    
    prompt = f"""
    You are a logistics AI. Extract structured information from the user's query about finding a parcel locker.
    Return a valid JSON object with exactly these keys:

    - city: The city name in English (string). Default to 'Warsaw' if not found.
    - street_address: If the user mentions a specific street address or street name (e.g. "Wyciszona 2", "ul. Marszałkowska 10"), return the full address string. Otherwise return null.
    - poi_type: The OSM tag value for the nearby place. Use these mappings:
        gas station / petrol station / fuel → "fuel"
        grocery store / supermarket / shop → "supermarket"
        park / green area → "park"
        pharmacy → "pharmacy"
        cafe / coffee shop → "cafe"
        restaurant → "restaurant"
        gym / fitness → "fitness_centre"
        train station → "station"
        shopping mall / gallery → "mall"
        hospital / clinic → "hospital"
        Return null if no nearby place of interest is mentioned (a street address alone is NOT a poi_type).
    - constraints: Extract as a string if the user implies:
        after hours / late at night / midnight / 24h / always open → "24/7"
        outdoor / outside → "outdoor"
        Return null otherwise.

    Query: "{query}"
    """
    try:
        response = await client.aio.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                system_instruction="You are a specialized logistics extraction AI. Output strictly valid JSON."
            )
        )
        content = response.text
        if content:
            return json.loads(content)
        return _mock_extract(query)
    except Exception as e:
        print(f"LLM Error: {e}")
        return _mock_extract(query)

def _mock_extract(query: str) -> Dict[str, Any]:
    q = query.lower()
    city = "Warsaw"
    if "krakow" in q or "kraków" in q: city = "Krakow"
    elif "gdansk" in q or "gdańsk" in q: city = "Gdansk"
    elif "wroclaw" in q or "wrocław" in q: city = "Wroclaw"

    poi_type = None
    if "grocery" in q or "supermarket" in q: poi_type = "supermarket"
    elif "gym" in q or "fitness" in q: poi_type = "fitness_centre"
    elif "park" in q: poi_type = "park"
    elif "gas station" in q or "petrol" in q or "fuel" in q: poi_type = "fuel"
    elif "train" in q: poi_type = "station"
    elif "pharmacy" in q: poi_type = "pharmacy"
    elif "cafe" in q or "coffee" in q: poi_type = "cafe"

    constraints = None
    if any(w in q for w in ["late", "night", "midnight", "24/7", "24h", "after hours"]):
        constraints = "24/7"
    elif "outdoor" in q or "outside" in q:
        constraints = "outdoor"

    return {
        "city": city,
        "poi_type": poi_type,
        "constraints": constraints
    }
