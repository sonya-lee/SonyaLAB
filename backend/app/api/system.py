from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import NotificationEventRecord, SchedulerRunRecord
from app.db.session import SessionLocal, database_health, get_db
from app.modules.flight_watcher.providers.factory import get_flight_provider
from app.modules.paper_explorer.providers.factory import get_paper_provider

router = APIRouter()

@router.get("/settings")
async def public_settings():
    db_ok, db_error = database_health()
    latest_run = None
    if db_ok:
        with SessionLocal() as db:
            run=db.scalar(select(SchedulerRunRecord).order_by(SchedulerRunRecord.started_at.desc()).limit(1))
            if run: latest_run={"job_type":run.job_type,"status":run.status,"started_at":run.started_at,"error":run.error_message}
    try: flight_ok, flight_error = await get_flight_provider().health_check()
    except ValueError as exc: flight_ok, flight_error = False, str(exc)
    try: paper_ok, paper_error = await get_paper_provider().health_check()
    except ValueError as exc: paper_ok, paper_error = False, str(exc)
    return {"mode":"single-user" if settings.single_user_mode else "external-auth","mock_mode":settings.flight_provider=="mock","timezone":settings.timezone,"currency":settings.default_currency,"database":{"connected":db_ok,"error":db_error},"backend":{"status":"ok","port":settings.backend_port},"frontend":{"port":5175,"version":"0.2.0"},"scheduler":{"latest_run":latest_run},"flight":{"provider":settings.flight_provider,"connected":flight_ok,"error":flight_error,"api_key_configured":False,"minimum_interval_minutes":settings.minimum_collection_interval_minutes,"default_interval_minutes":360,"default_drop_threshold_pct":25},"paper":{"provider":settings.paper_provider,"connected":paper_ok,"error":paper_error,"api_key_configured":bool(settings.crossref_mailto),"ai_summary_available":bool(settings.openai_api_key),"ai_key_configured":bool(settings.openai_api_key),"default_schedule":"manual","default_period_years":2,"default_summary_mode":"key"}}

@router.get("/notifications")
def notifications(db: Session = Depends(get_db)):
    return list(db.scalars(select(NotificationEventRecord).where(NotificationEventRecord.user_id==settings.single_user_id).order_by(NotificationEventRecord.created_at.desc()).limit(200)).all())

@router.post("/notifications/{event_id}/read")
def mark_read(event_id: str, db: Session = Depends(get_db)):
    event=db.get(NotificationEventRecord,event_id)
    if event and event.user_id==settings.single_user_id: event.read_at=datetime.now().astimezone(); db.commit()
    return {"ok":bool(event)}
