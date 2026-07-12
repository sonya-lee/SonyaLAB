from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SchedulerRunRecord
from app.scheduler.locking import assert_not_running


def start_run(db: Session, *, job_type: str, trigger_type: str, target_id: str | None, provider: str) -> SchedulerRunRecord:
    assert_not_running(db, job_type, target_id)
    run = SchedulerRunRecord(job_type=job_type, trigger_type=trigger_type, target_id=target_id, provider=provider, status="running")
    db.add(run); db.commit(); db.refresh(run)
    return run


def finish_run(db: Session, run: SchedulerRunRecord, *, status: str, processed: int = 0, created: int = 0, updated: int = 0, error: str | None = None, metadata: dict | None = None) -> SchedulerRunRecord:
    run.status = status
    run.finished_at = datetime.now().astimezone()
    run.processed_count = processed
    run.created_count = created
    run.updated_count = updated
    run.error_message = error
    run.metadata_json = metadata or {}
    db.commit(); db.refresh(run)
    return run


def list_runs(db: Session, limit: int = 100) -> list[SchedulerRunRecord]:
    return list(db.scalars(select(SchedulerRunRecord).order_by(SchedulerRunRecord.started_at.desc()).limit(limit)).all())
