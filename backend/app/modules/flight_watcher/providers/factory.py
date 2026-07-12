from app.core.config import settings
from app.modules.flight_watcher.providers.base import FlightSearchProvider
from app.modules.flight_watcher.providers.mock import MockFlightProvider


def get_flight_provider(name: str | None = None) -> FlightSearchProvider:
    provider_name = (name or settings.flight_provider).lower()
    if provider_name == "mock":
        return MockFlightProvider()
    raise ValueError(f"Flight provider '{provider_name}' is not configured. Use FLIGHT_PROVIDER=mock until API credentials are available.")
