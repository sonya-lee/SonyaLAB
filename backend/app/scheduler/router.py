from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import SavedPaperSearchRecord
from app.db.session import get_db
from app.modules.flight_watcher.service import get_watch_record
from app.scheduler.jobs.flight_collection import collect_flight_watch
from app.scheduler.jobs.paper_collection import collect_saved_paper_search
from app.scheduler.models import SchedulerRun
from app.scheduler.service import list_runs

router = APIRouter()


@router.get("/runs", response_model=list[SchedulerRun])
def runs(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    return list_runs(db, limit)


@router.post("/flights/{watch_id}/run", response_model=SchedulerRun | None)
async def run_flight(watch_id: str, db: Session = Depends(get_db)):
    try:
        watch = get_watch_record(db, watch_id, settings.single_user_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    return await collect_flight_watch(db, watch, "manual")


@router.post("/papers/{search_id}/run", response_model=SchedulerRun | None)
async def run_paper(search_id: str, db: Session = Depends(get_db)):
    saved = db.get(SavedPaperSearchRecord, search_id)
    if not saved or saved.user_id != settings.single_user_id:
        raise HTTPException(404, "saved paper search not found")
    return await collect_saved_paper_search(db, saved, "manual")
