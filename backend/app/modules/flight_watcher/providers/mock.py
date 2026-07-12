from datetime import datetime
from hashlib import sha256

from app.modules.flight_watcher.models import FlightPriceObservationCreate, FlightWatch


class MockFlightProvider:
    name = "mock"
    minimum_interval_minutes = 60

    async def search(self, watch: FlightWatch) -> list[FlightPriceObservationCreate]:
        bucket = datetime.now().astimezone().strftime("%Y%m%d%H")
        seed = int(sha256(f"{watch.id}:{bucket}".encode()).hexdigest()[:8], 16)
        price = 650_000 + seed % 1_200_000
        return [FlightPriceObservationCreate(
            total_price_krw=price,
            provider=self.name,
            external_offer_id=f"mock-{watch.id}-{bucket}",
            airline="Mock Airlines",
            direct=watch.direct_only,
            baggage_included=watch.baggage_required,
            baggage_summary="위탁 수하물 포함" if watch.baggage_required else "정보 없음",
            taxes_included=True,
            fees_included=True,
            confidence="mock",
        )]

    async def health_check(self) -> tuple[bool, str | None]:
        return True, None
