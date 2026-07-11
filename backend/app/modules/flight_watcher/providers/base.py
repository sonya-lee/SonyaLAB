from typing import Protocol

class FlightSearchProvider(Protocol):
    async def search(self, *, origin: str, destination: str, departure_date: str) -> list[dict]:
        ...
