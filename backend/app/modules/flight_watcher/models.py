from datetime import date
from pydantic import BaseModel, Field

class FlightWatchCreate(BaseModel):
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    departure_date_from: date
    departure_date_to: date
    trip_nights: int = Field(ge=1, le=30)
    drop_threshold_pct: float = Field(default=30.0, ge=1, le=90)
    direct_only: bool = True
    baggage_required: bool = True

class FlightWatch(FlightWatchCreate):
    id: int
    active: bool = True
