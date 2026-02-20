from pydantic import BaseModel, Field
from datetime import datetime


class QueryCreate(BaseModel):
    location: str = Field(min_length=2)
    start_date: str
    end_date: str


class QueryUpdate(BaseModel):
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class QueryOut(BaseModel):
    id: int
    location: str
    latitude: float
    longitude: float
    start_date: str
    end_date: str
    summary: str
    created_at: datetime

    class Config:
        from_attributes = True
