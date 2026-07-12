from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import FlightWatchRecord, NotificationEventRecord
from app.modules.flight_watcher.models import FlightWatch
from app.modules.flight_watcher.providers.factory import get_flight_provider
from app.modules.flight_watcher.service import add_observation, calculate_next_run
from app.scheduler.locking import JobAlreadyRunning
from app.scheduler.service import finish_run, start_run


async def collect_flight_watch(db: Session, watch: FlightWatchRecord, trigger_type: str = "scheduled"):
    try:
        provider = get_flight_provider(watch.provider)
    except ValueError as exc:
        run = start_run(db, job_type="flight_collection", trigger_type=trigger_type, target_id=watch.id, provider=watch.provider)
        watch.last_run_at = datetime.now().astimezone(); watch.last_error = str(exc)
        db.commit()
        return finish_run(db, run, status="skipped", error=str(exc), metadata={"reason": "provider_not_configured"})
    try:
        run = start_run(db, job_type="flight_collection", trigger_type=trigger_type, target_id=watch.id, provider=provider.name)
    except JobAlreadyRunning:
        return None
    started = datetime.now().astimezone()
    watch.last_run_at = started
    try:
        offers = await provider.search(FlightWatch.model_validate(watch))
        created = 0
        for offer in offers:
            try:
                add_observation(db, watch.id, offer, watch.user_id); created += 1
            except Exception as exc:
                if "uq_flight_offer_observation" not in str(exc).lower():
                    raise
                db.rollback()
        if created:
            latest = min(offers, key=lambda item: item.total_price_krw)
            new_low_key = f"flight-new-low:{watch.id}:{latest.total_price_krw}"
            if not db.query(NotificationEventRecord).filter_by(user_id=watch.user_id, dedupe_key=new_low_key).first():
                db.add(NotificationEventRecord(user_id=watch.user_id,event_type="flight_new_lowest",severity="info",title="새 항공권 최저가",message=f"{watch.origin} → {watch.destination} {latest.total_price_krw:,}원",data_json={"watch_id":watch.id},dedupe_key=new_low_key))
            if not latest.booking_url:
                no_link_key=f"flight-no-link:{watch.id}:{datetime.now().astimezone().date()}"
                if not db.query(NotificationEventRecord).filter_by(user_id=watch.user_id,dedupe_key=no_link_key).first():
                    db.add(NotificationEventRecord(user_id=watch.user_id,event_type="flight_booking_link_missing",severity="warning",title="예약 링크 없음",message="현재 공급자가 검증된 예약 링크를 제공하지 않았습니다.",data_json={"watch_id":watch.id},dedupe_key=no_link_key))
        watch.last_success_at = datetime.now().astimezone(); watch.last_error = None
        watch.next_run_at = calculate_next_run(watch.collection_interval_minutes, watch.last_success_at) if watch.collection_enabled else None
        db.commit()
        return finish_run(db, run, status="success", processed=len(offers), created=created, metadata={"mock": provider.name == "mock"})
    except Exception as exc:
        db.rollback()
        watch.last_error = str(exc); watch.next_run_at = calculate_next_run(watch.collection_interval_minutes)
        db.add(watch)
        event = NotificationEventRecord(user_id=watch.user_id, event_type="flight_provider_failed", severity="error", title="항공권 검색 실패", message=str(exc), data_json={"watch_id": watch.id}, dedupe_key=f"flight-failed:{watch.id}:{started.strftime('%Y%m%d%H')}")
        db.add(event); db.commit()
        return finish_run(db, run, status="failed", error=str(exc))
