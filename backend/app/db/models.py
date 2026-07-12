from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def uuid_string() -> str:
    return str(uuid4())


def now() -> datetime:
    return datetime.now().astimezone()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class FlightWatchRecord(TimestampMixin, Base):
    __tablename__ = "flight_watches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(160), default="")
    origin: Mapped[str] = mapped_column(String(3))
    destination: Mapped[str] = mapped_column(String(3))
    destination_region: Mapped[str] = mapped_column(String(32), default="other")
    departure_date_from: Mapped[date] = mapped_column(Date)
    departure_date_to: Mapped[date] = mapped_column(Date)
    trip_nights_min: Mapped[int] = mapped_column(Integer)
    trip_nights_max: Mapped[int] = mapped_column(Integer)
    drop_threshold_pct: Mapped[float] = mapped_column(Float, default=25)
    direct_only: Mapped[bool] = mapped_column(Boolean, default=True)
    baggage_required: Mapped[bool] = mapped_column(Boolean, default=True)
    collection_interval_minutes: Mapped[int] = mapped_column(Integer, default=360)
    collection_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Seoul")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    provider: Mapped[str] = mapped_column(String(64), default="mock")
    observations: Mapped[list["FlightObservationRecord"]] = relationship(back_populates="watch", cascade="all, delete-orphan")


class FlightObservationRecord(Base):
    __tablename__ = "flight_price_observations"
    __table_args__ = (UniqueConstraint("watch_id", "provider", "external_offer_id", "observed_at", name="uq_flight_offer_observation"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    watch_id: Mapped[str] = mapped_column(ForeignKey("flight_watches.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(64), default="mock")
    external_offer_id: Mapped[str] = mapped_column(String(255), default="")
    airline: Mapped[str] = mapped_column(String(160), default="")
    flight_numbers_json: Mapped[list] = mapped_column(JSON, default=list)
    departure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    arrival_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    return_departure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    return_arrival_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    stops: Mapped[int] = mapped_column(Integer, default=0)
    stop_places_json: Mapped[list] = mapped_column(JSON, default=list)
    direct: Mapped[bool] = mapped_column(Boolean, default=True)
    baggage_included: Mapped[bool] = mapped_column(Boolean, default=True)
    baggage_summary: Mapped[str] = mapped_column(Text, default="")
    total_price_krw: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="KRW")
    booking_url: Mapped[str] = mapped_column(Text, default="")
    seller_name: Mapped[str] = mapped_column(String(160), default="")
    seller_domain: Mapped[str] = mapped_column(String(255), default="")
    offer_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    price_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    taxes_included: Mapped[bool | None] = mapped_column(Boolean)
    fees_included: Mapped[bool | None] = mapped_column(Boolean)
    refundable: Mapped[bool | None] = mapped_column(Boolean)
    changeable: Mapped[bool | None] = mapped_column(Boolean)
    fare_type: Mapped[str] = mapped_column(String(100), default="")
    fare_conditions_json: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[str] = mapped_column(String(32), default="low")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    watch: Mapped[FlightWatchRecord] = relationship(back_populates="observations")


class SchedulerRunRecord(Base):
    __tablename__ = "scheduler_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    job_type: Mapped[str] = mapped_column(String(64), index=True)
    trigger_type: Mapped[str] = mapped_column(String(16))
    target_id: Mapped[str | None] = mapped_column(String(36), index=True)
    provider: Mapped[str] = mapped_column(String(64), default="")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(16), default="running")
    processed_count: Mapped[int] = mapped_column(Integer, default=0)
    created_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class PaperRecord(TimestampMixin, Base):
    __tablename__ = "papers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    provider: Mapped[str] = mapped_column(String(64))
    external_id: Mapped[str] = mapped_column(String(255))
    doi: Mapped[str | None] = mapped_column(String(255), unique=True)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str] = mapped_column(Text, default="")
    authors_json: Mapped[list] = mapped_column(JSON, default=list)
    journal: Mapped[str] = mapped_column(String(500), default="")
    published_year: Mapped[int | None] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(Text, default="")
    open_access: Mapped[bool | None] = mapped_column(Boolean)
    citation_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_sources_json: Mapped[dict] = mapped_column(JSON, default=dict)
    ranking_components_json: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_data_json: Mapped[dict] = mapped_column(JSON, default=dict)
    library_items: Mapped[list["PaperLibraryItemRecord"]] = relationship(back_populates="paper", cascade="all, delete-orphan")


class PaperCollectionRecord(TimestampMixin, Base):
    __tablename__ = "paper_collections"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")


class PaperLibraryItemRecord(TimestampMixin, Base):
    __tablename__ = "paper_library_items"
    __table_args__ = (UniqueConstraint("user_id", "paper_id", name="uq_user_paper_library"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    paper_id: Mapped[str] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), index=True)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    reading_status: Mapped[str] = mapped_column(String(16), default="unread")
    priority: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str] = mapped_column(Text, default="")
    tags_json: Mapped[list] = mapped_column(JSON, default=list)
    collection_id: Mapped[str | None] = mapped_column(ForeignKey("paper_collections.id", ondelete="SET NULL"))
    paper: Mapped[PaperRecord] = relationship(back_populates="library_items")


class SavedPaperSearchRecord(TimestampMixin, Base):
    __tablename__ = "saved_paper_searches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(160), default="")
    query: Mapped[str] = mapped_column(Text)
    filters_json: Mapped[dict] = mapped_column(JSON, default=dict)
    collection_interval_minutes: Mapped[int | None] = mapped_column(Integer)
    collection_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(64), default="crossref")


class NotificationEventRecord(Base):
    __tablename__ = "notification_events"
    __table_args__ = (UniqueConstraint("user_id", "dedupe_key", name="uq_notification_dedupe"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(64), default="sonya-lab")
    severity: Mapped[str] = mapped_column(String(16), default="info")
    title: Mapped[str] = mapped_column(String(300))
    message: Mapped[str] = mapped_column(Text)
    data_json: Mapped[dict] = mapped_column(JSON, default=dict)
    dedupe_key: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


Index("ix_flight_watch_due", FlightWatchRecord.collection_enabled, FlightWatchRecord.next_run_at)
Index("ix_saved_paper_search_due", SavedPaperSearchRecord.collection_enabled, SavedPaperSearchRecord.next_run_at)
