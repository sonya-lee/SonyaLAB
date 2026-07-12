from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SchedulerRunRecord


class JobAlreadyRunning(Exception):
    pass


def assert_not_running(db: Session, job_type: str, target_id: str | None) -> None:
    existing = db.scalar(select(SchedulerRunRecord.id).where(
        SchedulerRunRecord.job_type == job_type,
        SchedulerRunRecord.target_id == target_id,
        SchedulerRunRecord.status == "running",
    ))
    if existing:
        raise JobAlreadyRunning(f"{job_type} is already running for {target_id}")
