import pytest
from app.scheduler.locking import JobAlreadyRunning
from app.scheduler.service import finish_run, start_run

def test_duplicate_job_lock(db):
    run=start_run(db,job_type="flight_collection",trigger_type="manual",target_id="one",provider="mock")
    with pytest.raises(JobAlreadyRunning): start_run(db,job_type="flight_collection",trigger_type="manual",target_id="one",provider="mock")
    finish_run(db,run,status="success")
    assert start_run(db,job_type="flight_collection",trigger_type="manual",target_id="one",provider="mock")
