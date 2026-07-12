from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SummaryMode = Literal["key", "story", "engineer", "practical", "critical"]
ReadingStatus = Literal["unread", "reading", "read", "archived"]


class PaperSearchRequest(BaseModel):
    query: str = Field(min_length=2)
    field: str = ""
    author: str = ""
    journal: str = ""
    published_within_years: int = Field(default=2, ge=1, le=20)
    open_access_only: bool = False
    minimum_citations: int = Field(default=0, ge=0)
    sort_by: Literal["relevance", "newest", "citations"] = "relevance"
    limit: int = Field(default=10, ge=1, le=50)
    notify_new_results: bool = False


class SavedPaperSearchCreate(PaperSearchRequest):
    name: str = ""
    schedule: Literal["manual", "daily", "every_3_days", "weekly"] = "manual"


class SavedPaperSearch(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    name: str
    query: str
    filters_json: dict
    collection_interval_minutes: int | None
    collection_enabled: bool
    next_run_at: datetime | None
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    provider: str


class PaperSummaryRequest(BaseModel):
    title: str
    abstract: str = ""
    authors: list[str] = Field(default_factory=list)
    journal: str = ""
    year: int | None = None
    doi: str = ""
    mode: SummaryMode = "key"


class PaperSummaryResponse(BaseModel):
    title: str
    mode: SummaryMode
    model_name: str
    source_scope: Literal["abstract_only", "metadata_only"]
    korean_title: str
    overview: str
    key_points: list[str]
    limitations: str
    practical_implications: str
    confidence_note: str


class PaperLibraryUpsert(BaseModel):
    paper_id: str
    favorite: bool = True
    reading_status: ReadingStatus = "unread"
    priority: int = Field(default=0, ge=0, le=5)
    note: str = ""
    tags: list[str] = Field(default_factory=list)
    collection_id: str | None = None


class PaperLibraryPatch(BaseModel):
    favorite: bool | None = None
    reading_status: ReadingStatus | None = None
    priority: int | None = Field(default=None, ge=0, le=5)
    note: str | None = None
    tags: list[str] | None = None
    collection_id: str | None = None


class PaperLibraryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    paper_id: str
    favorite: bool
    reading_status: str
    priority: int
    note: str
    tags_json: list
    collection_id: str | None
    created_at: datetime
    updated_at: datetime
    paper: dict


class PaperCollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""
