from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SchedulerRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    job_type: str
    trigger_type: str
    target_id: str | None
    provider: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    processed_count: int
    created_count: int
    updated_count: int
    error_message: str | None
    metadata_json: dict


class ManualRunRequest(BaseModel):
    job_type: str
    target_id: str
