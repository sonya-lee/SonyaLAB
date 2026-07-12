from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

TargetRegion = Literal["europe", "australia", "united_states", "canada", "other"]


class FlightWatchCreate(BaseModel):
    name: str = ""
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    departure_date_from: date
    departure_date_to: date
    trip_nights_min: int = Field(default=5, ge=1, le=60)
    trip_nights_max: int = Field(default=10, ge=1, le=60)
    drop_threshold_pct: float = Field(default=25.0, ge=1, le=90)
    direct_only: bool = True
    baggage_required: bool = True
    destination_region: TargetRegion | None = None
    collection_interval_minutes: int = Field(default=360, ge=60, le=43200)
    collection_enabled: bool = True
    timezone: str = "Asia/Seoul"

    @field_validator("origin", "destination")
    @classmethod
    def normalize_airport(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("airport must be a three-letter IATA code")
        return value.upper()

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.departure_date_to < self.departure_date_from:
            raise ValueError("departure_date_to must not be before departure_date_from")
        if self.trip_nights_max < self.trip_nights_min:
            raise ValueError("trip_nights_max must be greater than or equal to trip_nights_min")
        return self


class FlightWatchUpdate(BaseModel):
    collection_interval_minutes: int | None = Field(default=None, ge=60, le=43200)
    collection_enabled: bool | None = None
    active: bool | None = None
    drop_threshold_pct: float | None = Field(default=None, ge=1, le=90)


class FlightWatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    name: str
    origin: str
    destination: str
    destination_region: str
    departure_date_from: date
    departure_date_to: date
    trip_nights_min: int
    trip_nights_max: int
    drop_threshold_pct: float
    direct_only: bool
    baggage_required: bool
    collection_interval_minutes: int
    collection_enabled: bool
    next_run_at: datetime | None
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    timezone: str
    active: bool
    provider: str


class FlightPriceObservationCreate(BaseModel):
    total_price_krw: int = Field(gt=0)
    provider: str = "manual"
    external_offer_id: str = ""
    airline: str = ""
    flight_numbers: list[str] = Field(default_factory=list)
    departure_at: datetime | None = None
    arrival_at: datetime | None = None
    return_departure_at: datetime | None = None
    return_arrival_at: datetime | None = None
    duration_minutes: int | None = None
    stops: int = Field(default=0, ge=0)
    stop_places: list[str] = Field(default_factory=list)
    direct: bool = True
    baggage_included: bool = True
    baggage_summary: str = ""
    currency: str = "KRW"
    booking_url: str = ""
    seller_name: str = ""
    offer_expires_at: datetime | None = None
    price_verified_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    taxes_included: bool | None = None
    fees_included: bool | None = None
    refundable: bool | None = None
    changeable: bool | None = None
    fare_type: str = ""
    fare_conditions: dict = Field(default_factory=dict)
    confidence: str = "low"
    observed_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())

    @field_validator("observed_at", "price_verified_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("datetime must include a timezone offset")
        return value


class FlightOffer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    watch_id: str
    provider: str
    external_offer_id: str
    airline: str
    flight_numbers: list[str] = Field(validation_alias="flight_numbers_json")
    departure_at: datetime | None
    arrival_at: datetime | None
    return_departure_at: datetime | None
    return_arrival_at: datetime | None
    duration_minutes: int | None
    stops: int
    stop_places: list[str] = Field(validation_alias="stop_places_json")
    direct: bool
    baggage_included: bool
    baggage_summary: str
    total_price_krw: int
    currency: str
    booking_url: str
    seller_name: str
    seller_domain: str
    offer_expires_at: datetime | None
    price_verified_at: datetime
    taxes_included: bool | None
    fees_included: bool | None
    refundable: bool | None
    changeable: bool | None
    fare_type: str
    fare_conditions: dict = Field(validation_alias="fare_conditions_json")
    confidence: str
    observed_at: datetime


class FlightWatchSummary(FlightWatch):
    current_lowest_price_krw: int | None = None
    baseline_price_krw: int | None = None
    difference_krw: int | None = None
    drop_pct: float | None = None
    lowest_30d_krw: int | None = None
    median_30d_krw: int | None = None
    sample_count: int = 0
    confidence: str = "insufficient"
    current_offer: FlightOffer | None = None


class PriceDropEvaluation(BaseModel):
    watch_id: str
    destination_region: str
    current_price_krw: int
    baseline_price_krw: int | None
    sample_count: int
    drop_pct: float | None
    is_price_drop: bool
    reason: str
    notification: dict | None = None
