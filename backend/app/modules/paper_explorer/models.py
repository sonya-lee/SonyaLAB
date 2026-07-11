from typing import Literal
from pydantic import BaseModel, Field

SummaryMode = Literal["standard", "engineer", "story", "comic"]

class PaperSearchRequest(BaseModel):
    query: str = Field(min_length=2)
    published_within_years: int = Field(default=1, ge=1, le=20)
    limit: int = Field(default=10, ge=1, le=50)

class PaperSummaryRequest(BaseModel):
    title: str
    abstract: str
    mode: SummaryMode = "story"

class PaperSummaryResponse(BaseModel):
    title: str
    mode: SummaryMode
    summary: str
