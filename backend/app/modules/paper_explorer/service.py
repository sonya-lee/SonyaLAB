import json
import re
from datetime import datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import PaperCollectionRecord, PaperLibraryItemRecord, PaperRecord, SavedPaperSearchRecord
from app.modules.paper_explorer.models import PaperLibraryPatch, PaperLibraryUpsert, PaperSearchRequest, PaperSummaryRequest, PaperSummaryResponse, SavedPaperSearchCreate
from app.modules.paper_explorer.providers.factory import get_paper_provider


def rank_components(item: dict, query: str) -> dict:
    query_terms = {term.lower() for term in query.split() if len(term) > 2}
    title = item.get("title", "").lower()
    relevance = min(1.0, sum(term in title for term in query_terms) / max(len(query_terms), 1))
    current_year = datetime.now().year
    recency = max(0.0, 1 - ((current_year - (item.get("year") or current_year)) / 10))
    citations = min(1.0, item.get("citation_count", 0) / 100)
    completeness = sum(bool(item.get(key)) for key in ("doi", "abstract", "authors", "journal")) / 4
    total = round(relevance * .45 + recency * .2 + citations * .2 + completeness * .15, 3)
    return {"total": total, "relevance": round(relevance, 3), "recency": round(recency, 3), "citations": round(citations, 3), "completeness": round(completeness, 3), "note": "Impact Factor 단일 지표를 사용하지 않음"}


async def search_papers(payload: PaperSearchRequest) -> tuple[list[dict], str, str | None]:
    try:
        provider = get_paper_provider()
        results = await provider.search(payload)
        for item in results:
            item["ranking_components"] = rank_components(item, payload.query)
            item["score"] = item["ranking_components"]["total"]
        return results, provider.name, None
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        return [], settings.paper_provider, str(exc)


def persist_search_results(db: Session, results: list[dict]) -> tuple[int, int]:
    created = updated = 0
    for item in results:
        record = db.scalar(select(PaperRecord).where(PaperRecord.doi == item["doi"])) if item.get("doi") else db.scalar(select(PaperRecord).where(PaperRecord.provider == item["provider"], PaperRecord.external_id == item["external_id"]))
        if not record:
            record = PaperRecord(provider=item["provider"], external_id=item["external_id"], doi=item.get("doi") or None, title=item["title"])
            db.add(record); created += 1
        else:
            updated += 1
        record.abstract = item.get("abstract", ""); record.authors_json = item.get("authors", []); record.journal = item.get("journal", ""); record.published_year = item.get("year"); record.url = item.get("url", ""); record.citation_count = item.get("citation_count", 0); record.metadata_sources_json = item.get("metadata_sources", {}); record.ranking_components_json = item.get("ranking_components", {})
        db.flush(); item["id"] = record.id
    db.commit()
    return created, updated


SCHEDULE_MINUTES = {"manual": None, "daily": 1440, "every_3_days": 4320, "weekly": 10080}


def save_search(db: Session, payload: SavedPaperSearchCreate, user_id: str):
    interval = SCHEDULE_MINUTES[payload.schedule]
    filters = payload.model_dump(exclude={"query", "name", "schedule", "notify_new_results"})
    record = SavedPaperSearchRecord(user_id=user_id, name=payload.name or payload.query, query=payload.query, filters_json=filters, collection_interval_minutes=interval, collection_enabled=interval is not None, next_run_at=datetime.now().astimezone() + timedelta(minutes=interval) if interval else None, provider=settings.paper_provider)
    db.add(record); db.commit(); db.refresh(record); return record


def _paper_dict(paper: PaperRecord) -> dict:
    return {"id": paper.id, "doi": paper.doi, "title": paper.title, "abstract": paper.abstract, "authors": paper.authors_json, "journal": paper.journal, "year": paper.published_year, "url": paper.url, "citation_count": paper.citation_count, "metadata_sources": paper.metadata_sources_json, "ranking_components": paper.ranking_components_json}


def upsert_library(db: Session, payload: PaperLibraryUpsert, user_id: str):
    paper = db.get(PaperRecord, payload.paper_id)
    if not paper: raise LookupError("paper not found")
    item = db.scalar(select(PaperLibraryItemRecord).where(PaperLibraryItemRecord.user_id == user_id, PaperLibraryItemRecord.paper_id == payload.paper_id))
    if not item: item = PaperLibraryItemRecord(user_id=user_id, paper_id=payload.paper_id); db.add(item)
    for key, value in payload.model_dump(exclude={"paper_id", "tags"}).items(): setattr(item, key, value)
    item.tags_json = payload.tags; db.commit(); db.refresh(item); return library_dict(item)


def patch_library(db: Session, item_id: str, payload: PaperLibraryPatch, user_id: str):
    item = db.scalar(select(PaperLibraryItemRecord).where(PaperLibraryItemRecord.id == item_id, PaperLibraryItemRecord.user_id == user_id))
    if not item: raise LookupError("library item not found")
    changes = payload.model_dump(exclude_none=True)
    if "tags" in changes: item.tags_json = changes.pop("tags")
    for key, value in changes.items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return library_dict(item)


def library_dict(item: PaperLibraryItemRecord) -> dict:
    return {"id": item.id, "paper_id": item.paper_id, "favorite": item.favorite, "reading_status": item.reading_status, "priority": item.priority, "note": item.note, "tags_json": item.tags_json, "collection_id": item.collection_id, "created_at": item.created_at, "updated_at": item.updated_at, "paper": _paper_dict(item.paper)}


def _response_text(response: dict) -> str:
    for output in response.get("output", []):
        for content in output.get("content", []):
            if content.get("type") == "output_text" and content.get("text"): return content["text"]
    raise ValueError("OpenAI response did not contain output text")


async def summarize_paper(payload: PaperSummaryRequest) -> PaperSummaryResponse:
    if not settings.openai_api_key: raise RuntimeError("OPENAI_API_KEY is not configured")
    scope = "abstract_only" if payload.abstract.strip() else "metadata_only"
    mode_instruction = {"key": "핵심만 정확하게", "story": "문제-기존 한계-가정-검증-결과-의미-한계 순서의 자연스러운 이야기형", "engineer": "측정 조건과 공정 관점", "practical": "실무 적용 가능성과 전제조건 중심", "critical": "근거, 한계, 재현성, 과도한 해석 가능성을 비판적으로"}[payload.mode]
    instructions = f"학술 자료를 한국어로 번역·요약한다. {mode_instruction} 설명한다. 제공된 자료만 사용하고 논문에 없는 내용, 감정, 대화, 유치한 비유를 만들지 않는다. 초록이 없으면 세부 내용을 확인할 수 없다고 명시한다. JSON만 반환하며 korean_title, overview, key_points(3~5개), limitations, practical_implications, confidence_note 키를 사용한다."
    source = payload.model_dump()
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post("https://api.openai.com/v1/responses", headers={"authorization": f"Bearer {settings.openai_api_key}"}, json={"model": settings.paper_summary_model, "instructions": instructions, "input": json.dumps(source, ensure_ascii=False)})
        response.raise_for_status()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", _response_text(response.json()).strip()); result = json.loads(raw)
    return PaperSummaryResponse(title=payload.title, mode=payload.mode, model_name=settings.paper_summary_model, source_scope=scope, **result)
