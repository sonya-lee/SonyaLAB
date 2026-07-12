from typing import Protocol

from app.modules.flight_watcher.models import FlightPriceObservationCreate, FlightWatch


class FlightSearchProvider(Protocol):
    name: str
    minimum_interval_minutes: int

    async def search(self, watch: FlightWatch) -> list[FlightPriceObservationCreate]: ...
    async def health_check(self) -> tuple[bool, str | None]: ...
