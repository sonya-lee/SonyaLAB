from datetime import datetime, timedelta
from statistics import median
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import FlightObservationRecord, FlightWatchRecord, NotificationEventRecord
from app.modules.flight_watcher.airports import AIRPORTS
from app.modules.flight_watcher.models import (
    FlightOffer, FlightPriceObservationCreate, FlightWatch, FlightWatchCreate,
    FlightWatchSummary, FlightWatchUpdate, PriceDropEvaluation,
)


def now() -> datetime:
    return datetime.now().astimezone()


def as_aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.astimezone()


def destination_region(code: str) -> str:
    airport = next((item for item in AIRPORTS if item["code"] == code.upper()), None)
    return airport["region"] if airport else "other"


def calculate_next_run(interval_minutes: int, from_time: datetime | None = None) -> datetime:
    return (from_time or now()) + timedelta(minutes=interval_minutes)


def _watch_schema(record: FlightWatchRecord) -> FlightWatch:
    return FlightWatch.model_validate(record)


def create_watch(db: Session, payload: FlightWatchCreate, user_id: str) -> FlightWatch:
    if payload.collection_interval_minutes < settings.minimum_collection_interval_minutes:
        raise ValueError(f"minimum collection interval is {settings.minimum_collection_interval_minutes} minutes")
    record = FlightWatchRecord(
        user_id=user_id,
        **payload.model_dump(exclude={"destination_region"}),
        destination_region=payload.destination_region or destination_region(payload.destination),
        provider=settings.flight_provider,
        next_run_at=calculate_next_run(payload.collection_interval_minutes) if payload.collection_enabled else None,
    )
    db.add(record); db.commit(); db.refresh(record)
    return _watch_schema(record)


def list_watches(db: Session, user_id: str) -> list[FlightWatchSummary]:
    records = db.scalars(select(FlightWatchRecord).where(FlightWatchRecord.user_id == user_id).order_by(FlightWatchRecord.created_at.desc())).all()
    return [watch_summary(db, item) for item in records]


def get_watch_record(db: Session, watch_id: str, user_id: str) -> FlightWatchRecord:
    record = db.scalar(select(FlightWatchRecord).where(FlightWatchRecord.id == watch_id, FlightWatchRecord.user_id == user_id))
    if not record:
        raise LookupError("flight watch not found")
    return record


def update_watch(db: Session, watch_id: str, payload: FlightWatchUpdate, user_id: str) -> FlightWatch:
    record = get_watch_record(db, watch_id, user_id)
    changes = payload.model_dump(exclude_none=True)
    if "collection_interval_minutes" in changes:
        interval = changes["collection_interval_minutes"]
        if interval < settings.minimum_collection_interval_minutes:
            raise ValueError(f"minimum collection interval is {settings.minimum_collection_interval_minutes} minutes")
        record.next_run_at = calculate_next_run(interval) if record.collection_enabled else None
    for key, value in changes.items():
        setattr(record, key, value)
    if changes.get("collection_enabled") is False:
        record.next_run_at = None
    elif changes.get("collection_enabled") is True:
        record.next_run_at = calculate_next_run(record.collection_interval_minutes)
    db.commit(); db.refresh(record)
    return _watch_schema(record)


def _validated_booking_url(url: str) -> tuple[str, str]:
    if not url:
        return "", ""
    parsed = urlparse(url)
    allowed = {item.strip().lower() for item in getattr(settings, "flight_booking_allowed_domains", "").split(",") if item.strip()}
    domain = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not domain or not any(domain == item or domain.endswith(f".{item}") for item in allowed):
        raise ValueError("booking URL domain is not in FLIGHT_BOOKING_ALLOWED_DOMAINS")
    return url, domain


def add_observation(db: Session, watch_id: str, payload: FlightPriceObservationCreate, user_id: str) -> PriceDropEvaluation:
    watch = get_watch_record(db, watch_id, user_id)
    if payload.external_offer_id:
        existing = db.scalar(select(FlightObservationRecord).where(FlightObservationRecord.watch_id == watch_id, FlightObservationRecord.provider == payload.provider, FlightObservationRecord.external_offer_id == payload.external_offer_id))
        if existing:
            return evaluate_price_drop(db, watch, existing)
    booking_url, seller_domain = _validated_booking_url(payload.booking_url)
    record = FlightObservationRecord(
        watch_id=watch.id,
        **payload.model_dump(exclude={"flight_numbers", "stop_places", "booking_url", "fare_conditions"}),
        flight_numbers_json=payload.flight_numbers,
        stop_places_json=payload.stop_places,
        booking_url=booking_url,
        seller_domain=seller_domain,
        fare_conditions_json=payload.fare_conditions,
    )
    db.add(record); db.commit(); db.refresh(record)
    return evaluate_price_drop(db, watch, record)


def _comparable(records: list[FlightObservationRecord], current: FlightObservationRecord | None = None) -> list[FlightObservationRecord]:
    if current is None:
        return records
    return [item for item in records if item.id != current.id and item.direct == current.direct and item.baggage_included == current.baggage_included and item.currency == current.currency]


def evaluate_price_drop(db: Session, watch: FlightWatchRecord, current: FlightObservationRecord) -> PriceDropEvaluation:
    history = list(db.scalars(select(FlightObservationRecord).where(FlightObservationRecord.watch_id == watch.id).order_by(FlightObservationRecord.observed_at)).all())
    samples = _comparable(history, current)
    baseline = round(median(item.total_price_krw for item in samples)) if len(samples) >= 3 else None
    drop_pct = round((baseline - current.total_price_krw) / baseline * 100, 1) if baseline else None
    is_drop = bool(drop_pct is not None and drop_pct >= watch.drop_threshold_pct)
    reason = "price_drop_detected" if is_drop else ("insufficient_history" if baseline is None else "drop_below_threshold")
    notification = None
    if is_drop:
        dedupe_key = f"flight-price-drop:{watch.id}:{current.total_price_krw}:{current.observed_at.date()}"
        exists = db.scalar(select(NotificationEventRecord.id).where(NotificationEventRecord.user_id == watch.user_id, NotificationEventRecord.dedupe_key == dedupe_key))
        if not exists:
            event = NotificationEventRecord(user_id=watch.user_id, event_type="flight_price_drop", severity="important", title=f"{watch.origin} → {watch.destination} 항공권 급락", message=f"기준가보다 {drop_pct}% 낮은 {current.total_price_krw:,}원입니다.", data_json={"watch_id": watch.id, "observation_id": current.id}, dedupe_key=dedupe_key)
            db.add(event); db.commit()
            notification = {"status": "recorded", "id": event.id}
        else:
            notification = {"status": "duplicate_skipped"}
    return PriceDropEvaluation(watch_id=watch.id, destination_region=watch.destination_region, current_price_krw=current.total_price_krw, baseline_price_krw=baseline, sample_count=len(samples), drop_pct=drop_pct, is_price_drop=is_drop, reason=reason, notification=notification)


def list_observations(db: Session, watch_id: str, user_id: str, days: int = 365) -> list[FlightOffer]:
    get_watch_record(db, watch_id, user_id)
    cutoff = now() - timedelta(days=days)
    records = db.scalars(select(FlightObservationRecord).where(FlightObservationRecord.watch_id == watch_id, FlightObservationRecord.observed_at >= cutoff).order_by(FlightObservationRecord.observed_at)).all()
    return [FlightOffer.model_validate(item) for item in records]


def watch_summary(db: Session, watch: FlightWatchRecord) -> FlightWatchSummary:
    records = list(db.scalars(select(FlightObservationRecord).where(FlightObservationRecord.watch_id == watch.id).order_by(FlightObservationRecord.observed_at.desc())).all())
    latest = records[0] if records else None
    current_batch = [item for item in records if latest and abs((as_aware(latest.observed_at) - as_aware(item.observed_at)).total_seconds()) <= 300 and item.provider == latest.provider]
    current = min(current_batch, key=lambda item: item.total_price_krw) if current_batch else None
    comparable = _comparable(records, current)
    baseline = round(median(item.total_price_krw for item in comparable)) if len(comparable) >= 3 else None
    cutoff30 = now() - timedelta(days=30)
    last30 = [item.total_price_krw for item in records if as_aware(item.observed_at) >= cutoff30 and (current is None or item.currency == current.currency)]
    current_price = current.total_price_krw if current else None
    difference = current_price - baseline if current_price is not None and baseline is not None else None
    drop_pct = round((baseline - current_price) / baseline * 100, 1) if baseline and current_price is not None else None
    confidence = "high" if len(comparable) >= 10 else ("medium" if len(comparable) >= 5 else ("low" if len(comparable) >= 3 else "insufficient"))
    base = FlightWatch.model_validate(watch).model_dump()
    return FlightWatchSummary(**base, current_lowest_price_krw=current_price, baseline_price_krw=baseline, difference_krw=difference, drop_pct=drop_pct, lowest_30d_krw=min(last30) if last30 else None, median_30d_krw=round(median(last30)) if last30 else None, sample_count=len(comparable), confidence=confidence, current_offer=FlightOffer.model_validate(current) if current else None)
