# Run this from the /backend directory:
# PYTHONPATH=. python tests/manual_test.py
import asyncio
from app.models import SearchRequest
from app.main import search
import json

async def test_search():
    request = SearchRequest(query="Find me a parcel locker near a grocery store in Warsaw")
    
    print(f"Testing query: '{request.query}'")
    try:
        response = await search(request)
        print("\n--- Search Results ---")
        print(f"City: {response.city}")
        print(f"POI Type: {response.poi_type}")
        print(f"Found POIs: {len(response.pois)}")
        print(f"Found InPost Points: {len(response.inpost_points)}")
        
        print("\n--- Reasoning Feed ---")
        for step in response.reasoning:
            print(f"- {step.step}: {json.dumps(step.details)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
