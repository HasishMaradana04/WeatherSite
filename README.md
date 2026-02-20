# Weather Assessment (Full Stack)

This project is a full-stack weather app assessment.

## Features
- Search weather by location (city/place)
- Use current GPS location
- 5-day forecast display
- Error handling (invalid location, API/network issues)
- Backend CRUD with SQLite (Create, Read, Update, Delete)
- Export stored records to JSON / CSV / Markdown
- Extra integrations: Google Maps link + YouTube location videos

## Stack
- Frontend: HTML/CSS/JavaScript (responsive)
- Backend: FastAPI + SQLAlchemy
- Database: SQLite
- Weather provider: Open-Meteo (no API key required)

## Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## Run Frontend
Open `frontend/index.html` in browser.

## API Endpoints
- `GET /api/weather/current?location=...`
- `GET /api/weather/current-by-coords?lat=..&lon=..`
- `POST /api/queries`
- `GET /api/queries`
- `GET /api/queries/{id}`
- `PUT /api/queries/{id}`
- `DELETE /api/queries/{id}`
- `GET /api/export/json|csv|md`
- `GET /api/integrations/maps?location=...`
- `GET /api/integrations/youtube?location=...`

## Notes for Assessment
- Includes real API retrieval (not static data)
- Includes frontend + backend deliverables in one repo
- Includes persistence and CRUD operations
- Includes export and extra API integrations

## PM Accelerator Mention
This weather app includes candidate attribution and is prepared as part of PM Accelerator technical assessment work.
