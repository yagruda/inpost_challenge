# Inpost Locker Natural Language  Finder

## Author

- **Name:** Yurii Hruda
- **Email:** yhruda@student.42warsaw.pl

## Overview

Full-Stack application interprets natural language queries (e.g., "Find me the closest locker to st. Wyciszona 2 in Warsaw"),
which makes a process of finding package lockers easier for a customer. 
## Demo & Description

The application consists of a FastAPI backend and a React/Vite frontend. The architecture is broken into 3 critical stages:
1. **LLM Extraction**: Using Google AI Studio (Gemini) as example (can be easily changed to other LLMs), natural language is analyzed to identify the target city, Points of Interest (POIs) type, and constraints.
2. **Geospatial Cross-referencing**: It uses Nominatim and Overpass APIs to find the coordinates of the requested POIs. We filter by distance and calculate a bounding box around these locations.
3. **InPost Integration**: Utilizing the geographic constraints discovered by our OSM cross-reference, we fetch active parcel lockers from the InPost Global Points API, avoiding over-fetching by using intelligent data correlation.

Use the following example queries to test the system:

- "Give me a locker in Warsaw close to Wyciszona 2"
- "Find a parcel locker in Krakow near a Biedronka grocery store that is open 24/7"
- "I need to pick up a package late at night in Wrocław. Find an outdoor locker near a well-lit area like a gas station"

**Test deployed solution at https://stride.sbs/inpost**  
**Watch a screen recording at https://www.loom.com/share/12eef5c8869f4f81adfc776f98b9bee3**  
 

## Technologies

- **Backend**: Python, FastAPI, Pydantic, HTTPX (Async operations), Google (Gemini) API for LLM analysis.
- **Geospatial APIs**: OpenStreetMap Nominatim and Overpass QL APIs.
- **Frontend**: React, Vite, Tailwind CSS, React Leaflet, Lucide React.
- **Infrastructure**: Docker

## How to run

### Prerequisites

- Docker installed
- OR locally installed Node 18+ and Python 3.11+
- A Google AI Studio Gemini API Key (if you want real extraction, otherwise the app uses a fallback mock system for specific Polish cities)

### Build & run

Run using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/yagruda/inpost_challenge
cd inpost_challenge

# Copy the example environment file and fill in your values
# Or you can test live at https://stride.sbs/inpost
cp .env.example .env

# Build and start the containers
docker-compose up --build
```

- `GEMINI_API_KEY`: (Optional) Your Google AI Studio key. If left blank, the app uses a keyword-based mock extractor.
- `VITE_API_URL`: Set to `http://localhost:8000` for local development.
- `VITE_BASE_PATH`: Set to `/` for local development (unless deploying to a subpath like `/inpost/`).
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins (e.g., `http://localhost:5173`).

Access the frontend application at: http://localhost:5173
Access the backend API and Swagger UI at: http://localhost:8000/docs

## What I would do with more time

I'll go deeper and rewrite the whole architecture.
Make proper automatic tests for edge cases (you will definitely find a lot of bugs in the current version).  
After polishing the current version, a lot of features can be implemented in the future to make it user friendly.   
Such as: integrate browser Geolocation API to auto-fill the user's city, delete workflow window (user doesn't need it), distinguish more complex constraints from user's prompt, show more information about a locker once client clicked on it on map.

## AI usage

After implementing basic architecture, Google Antigravity was used as a companion to code faster and writing tests. I used ligthly edited Andrej Karpathy's [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)  as behavioral guidelines for my Antigravity. 

## Anything else?

Due to time limitation (spotted this internship a day before deadline) project was done in a rush. Because of it AI was used more than it should be in production. 
