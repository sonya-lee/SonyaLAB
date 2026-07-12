from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import NotificationEventRecord, SavedPaperSearchRecord
from app.modules.paper_explorer.models import PaperSearchRequest
from app.modules.paper_explorer.service import persist_search_results, search_papers
from app.scheduler.locking import JobAlreadyRunning
from app.scheduler.service import finish_run, start_run


async def collect_saved_paper_search(db: Session, saved: SavedPaperSearchRecord, trigger_type: str = "scheduled"):
    try:
        run = start_run(db, job_type="paper_collection", trigger_type=trigger_type, target_id=saved.id, provider=saved.provider)
    except JobAlreadyRunning:
        return None
    saved.last_run_at = datetime.now().astimezone()
    try:
        filters = saved.filters_json or {}
        payload = PaperSearchRequest(query=saved.query, **filters)
        results, provider, provider_error = await search_papers(payload)
        if provider_error and provider == "mock":
            saved.last_error = provider_error
            db.commit()
            return finish_run(db, run, status="failed", error=provider_error)
        created, updated = persist_search_results(db, results)
        if created:
            key=f"paper-new:{saved.id}:{saved.last_run_at.date()}"
            if not db.query(NotificationEventRecord).filter_by(user_id=saved.user_id,dedupe_key=key).first():
                db.add(NotificationEventRecord(user_id=saved.user_id,event_type="paper_search_match",severity="info",title="새 논문 발견",message=f"{saved.name} 검색에서 신규 논문 {created}건을 찾았습니다.",data_json={"saved_search_id":saved.id},dedupe_key=key))
        saved.last_success_at = datetime.now().astimezone(); saved.last_error = None
        saved.next_run_at = saved.last_success_at + timedelta(minutes=saved.collection_interval_minutes) if saved.collection_enabled and saved.collection_interval_minutes else None
        db.commit()
        return finish_run(db, run, status="success", processed=len(results), created=created, updated=updated, metadata={"provider": provider})
    except Exception as exc:
        db.rollback(); saved.last_error = str(exc); db.add(saved); db.commit()
        return finish_run(db, run, status="failed", error=str(exc))
