from fastapi import APIRouter

from app.modules.paper_explorer.models import (
    PaperSearchRequest,
    PaperSummaryRequest,
    PaperSummaryResponse,
)
from app.modules.paper_explorer.service import search_papers, summarize_paper

router = APIRouter()

@router.post("/search")
def search(payload: PaperSearchRequest) -> list[dict]:
    return search_papers(payload)

@router.post("/summarize", response_model=PaperSummaryResponse)
def summarize(payload: PaperSummaryRequest) -> PaperSummaryResponse:
    return summarize_paper(payload)
