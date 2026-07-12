import asyncio
from datetime import datetime

from sqlalchemy import select

from app.core.config import settings
from app.db.models import FlightWatchRecord, SavedPaperSearchRecord
from app.db.session import SessionLocal
from app.scheduler.jobs.flight_collection import collect_flight_watch
from app.scheduler.jobs.paper_collection import collect_saved_paper_search


async def poll_once() -> None:
    current = datetime.now().astimezone()
    with SessionLocal() as db:
        flights = list(db.scalars(select(FlightWatchRecord).where(FlightWatchRecord.active.is_(True), FlightWatchRecord.collection_enabled.is_(True), FlightWatchRecord.next_run_at <= current)).all())
        papers = list(db.scalars(select(SavedPaperSearchRecord).where(SavedPaperSearchRecord.collection_enabled.is_(True), SavedPaperSearchRecord.next_run_at <= current)).all())
        for watch in flights:
            await collect_flight_watch(db, watch)
        for saved in papers:
            await collect_saved_paper_search(db, saved)


async def run_forever() -> None:
    while True:
        try:
            await poll_once()
        except Exception as exc:
            print(f"scheduler poll failed: {exc}", flush=True)
        await asyncio.sleep(settings.scheduler_poll_seconds)


if __name__ == "__main__":
    asyncio.run(run_forever())
