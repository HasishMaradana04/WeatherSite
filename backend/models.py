from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base


class WeatherQuery(Base):
    __tablename__ = "weather_queries"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
