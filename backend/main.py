from datetime import date, datetime
from io import StringIO
import csv

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import WeatherQuery
from schemas import QueryCreate, QueryUpdate, QueryOut
from weather_service import geocode_location, get_weather

app = FastAPI(title="Weather Assessment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def db_get():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def validate_dates(start_date: str, end_date: str):
    try:
        s = datetime.fromisoformat(start_date).date()
        e = datetime.fromisoformat(end_date).date()
    except ValueError:
        raise HTTPException(400, "Dates must be YYYY-MM-DD")
    if s > e:
        raise HTTPException(400, "start_date must be before or equal to end_date")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/weather/current")
def weather_current(location: str):
    try:
        geo = geocode_location(location)
        weather = get_weather(geo["latitude"], geo["longitude"])
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception:
        raise HTTPException(502, "Weather provider failed")
    return {"location": geo, "weather": weather}


@app.get("/api/weather/current-by-coords")
def weather_by_coords(lat: float, lon: float):
    try:
        weather = get_weather(lat, lon)
    except Exception:
        raise HTTPException(502, "Weather provider failed")
    return {"location": {"latitude": lat, "longitude": lon}, "weather": weather}


@app.post("/api/queries", response_model=QueryOut)
def create_query(payload: QueryCreate, db: Session = Depends(db_get)):
    validate_dates(payload.start_date, payload.end_date)
    try:
        geo = geocode_location(payload.location)
        weather = get_weather(geo["latitude"], geo["longitude"], payload.start_date, payload.end_date)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception:
        raise HTTPException(502, "External API error")

    current = weather.get("current", {})
    summary = f"Temp: {current.get('temperature_2m', 'n/a')}°C, Wind: {current.get('wind_speed_10m', 'n/a')} km/h"

    row = WeatherQuery(
        location=payload.location,
        latitude=geo["latitude"],
        longitude=geo["longitude"],
        start_date=payload.start_date,
        end_date=payload.end_date,
        summary=summary,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/queries", response_model=list[QueryOut])
def list_queries(db: Session = Depends(db_get)):
    return db.query(WeatherQuery).order_by(WeatherQuery.id.desc()).all()


@app.get("/api/queries/{query_id}", response_model=QueryOut)
def read_query(query_id: int, db: Session = Depends(db_get)):
    row = db.query(WeatherQuery).filter(WeatherQuery.id == query_id).first()
    if not row:
        raise HTTPException(404, "Record not found")
    return row


@app.put("/api/queries/{query_id}", response_model=QueryOut)
def update_query(query_id: int, payload: QueryUpdate, db: Session = Depends(db_get)):
    row = db.query(WeatherQuery).filter(WeatherQuery.id == query_id).first()
    if not row:
        raise HTTPException(404, "Record not found")

    location = payload.location or row.location
    start_date = payload.start_date or row.start_date
    end_date = payload.end_date or row.end_date
    validate_dates(start_date, end_date)

    try:
        geo = geocode_location(location)
        weather = get_weather(geo["latitude"], geo["longitude"], start_date, end_date)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception:
        raise HTTPException(502, "External API error")

    current = weather.get("current", {})
    row.location = location
    row.latitude = geo["latitude"]
    row.longitude = geo["longitude"]
    row.start_date = start_date
    row.end_date = end_date
    row.summary = f"Temp: {current.get('temperature_2m', 'n/a')}°C, Wind: {current.get('wind_speed_10m', 'n/a')} km/h"

    db.commit()
    db.refresh(row)
    return row


@app.delete("/api/queries/{query_id}")
def delete_query(query_id: int, db: Session = Depends(db_get)):
    row = db.query(WeatherQuery).filter(WeatherQuery.id == query_id).first()
    if not row:
        raise HTTPException(404, "Record not found")
    db.delete(row)
    db.commit()
    return {"deleted": True}


@app.get("/api/export/{fmt}")
def export_data(fmt: str, db: Session = Depends(db_get)):
    rows = db.query(WeatherQuery).order_by(WeatherQuery.id.asc()).all()
    data = [
        {
            "id": r.id,
            "location": r.location,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "summary": r.summary,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]

    if fmt == "json":
        return {"items": data}
    if fmt == "csv":
        buf = StringIO()
        writer = csv.DictWriter(buf, fieldnames=["id", "location", "latitude", "longitude", "start_date", "end_date", "summary", "created_at"])
        writer.writeheader()
        writer.writerows(data)
        return PlainTextResponse(buf.getvalue(), media_type="text/csv")
    if fmt == "md":
        lines = ["| id | location | start_date | end_date | summary |", "|---|---|---|---|---|"]
        for d in data:
            lines.append(f"| {d['id']} | {d['location']} | {d['start_date']} | {d['end_date']} | {d['summary']} |")
        return PlainTextResponse("\n".join(lines), media_type="text/markdown")

    raise HTTPException(400, "Supported formats: json, csv, md")


@app.get("/api/integrations/maps")
def map_link(location: str):
    return {"maps_url": f"https://www.google.com/maps/search/?api=1&query={location}"}


@app.get("/api/integrations/youtube")
def youtube_link(location: str):
    return {"youtube_url": f"https://www.youtube.com/results?search_query={location}+travel+guide"}

# Mount the static frontend files onto the root "/"
# Important: this must come AFTER all /api routes!
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
