from app.modules.flight_watcher.models import FlightWatch, FlightWatchCreate

_WATCHES: list[FlightWatch] = []

def create_watch(payload: FlightWatchCreate) -> FlightWatch:
    watch = FlightWatch(id=len(_WATCHES) + 1, **payload.model_dump())
    _WATCHES.append(watch)
    return watch

def list_watches() -> list[FlightWatch]:
    return _WATCHES
