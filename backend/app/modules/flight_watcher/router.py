from fastapi import APIRouter

from app.modules.flight_watcher.models import FlightWatch, FlightWatchCreate
from app.modules.flight_watcher.service import create_watch, list_watches

router = APIRouter()

@router.post("/watches", response_model=FlightWatch)
def add_watch(payload: FlightWatchCreate) -> FlightWatch:
    return create_watch(payload)

@router.get("/watches", response_model=list[FlightWatch])
def get_watches() -> list[FlightWatch]:
    return list_watches()
