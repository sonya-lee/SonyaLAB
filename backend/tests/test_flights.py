from datetime import date
import pytest
from app.core.config import settings
from app.db.models import FlightWatchRecord
from app.modules.flight_watcher.models import FlightPriceObservationCreate, FlightWatchCreate, FlightWatchUpdate
from app.modules.flight_watcher.service import add_observation, create_watch, list_observations, update_watch, watch_summary
from app.scheduler.jobs.flight_collection import collect_flight_watch

def payload(interval=360):
    return FlightWatchCreate(origin="ICN",destination="LHR",departure_date_from=date(2026,10,1),departure_date_to=date(2026,10,15),trip_nights_min=5,trip_nights_max=9,collection_interval_minutes=interval)

def test_watch_interval_and_next_run(db):
    watch=create_watch(db,payload(),settings.single_user_id); assert watch.next_run_at
    changed=update_watch(db,watch.id,FlightWatchUpdate(collection_interval_minutes=720),settings.single_user_id)
    assert changed.collection_interval_minutes==720 and changed.next_run_at>watch.next_run_at

def test_minimum_interval(db):
    with pytest.raises(ValueError): create_watch(db,payload(30),settings.single_user_id)

def test_price_statistics_and_insufficient_data(db):
    watch=create_watch(db,payload(),settings.single_user_id); record=db.get(FlightWatchRecord,watch.id)
    add_observation(db,watch.id,FlightPriceObservationCreate(total_price_krw=1_500_000),settings.single_user_id)
    assert watch_summary(db,record).confidence=="insufficient"
    for price in (1_600_000,1_550_000,1_100_000): result=add_observation(db,watch.id,FlightPriceObservationCreate(total_price_krw=price),settings.single_user_id)
    summary=watch_summary(db,record)
    assert summary.current_lowest_price_krw==1_100_000 and summary.baseline_price_krw==1_550_000 and result.is_price_drop
    assert len(list_observations(db,watch.id,settings.single_user_id))==4

def test_untrusted_booking_url_is_rejected(db):
    watch=create_watch(db,payload(),settings.single_user_id)
    with pytest.raises(ValueError): add_observation(db,watch.id,FlightPriceObservationCreate(total_price_krw=500_000,booking_url="https://suspicious.example/buy"),settings.single_user_id)

def test_duplicate_offer_is_not_created_twice(db):
    watch=create_watch(db,payload(),settings.single_user_id)
    offer=FlightPriceObservationCreate(total_price_krw=500_000,provider="mock",external_offer_id="same")
    add_observation(db,watch.id,offer,settings.single_user_id); add_observation(db,watch.id,offer,settings.single_user_id)
    assert len(list_observations(db,watch.id,settings.single_user_id))==1

@pytest.mark.asyncio
async def test_manual_mock_collection(db):
    watch=create_watch(db,payload(),settings.single_user_id); record=db.get(FlightWatchRecord,watch.id)
    run=await collect_flight_watch(db,record,"manual")
    assert run.status=="success" and run.created_count==1

@pytest.mark.asyncio
async def test_failed_provider_does_not_block_other_watch(db):
    first=create_watch(db,payload(),settings.single_user_id); second=create_watch(db,payload(),settings.single_user_id)
    one=db.get(FlightWatchRecord,first.id); two=db.get(FlightWatchRecord,second.id); one.provider="missing"; db.commit()
    skipped=await collect_flight_watch(db,one,"manual"); success=await collect_flight_watch(db,two,"manual")
    assert skipped.status=="skipped" and success.status=="success"
