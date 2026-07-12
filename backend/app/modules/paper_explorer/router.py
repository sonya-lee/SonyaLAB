import json
from datetime import datetime
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import NotificationEventRecord, PaperCollectionRecord, PaperLibraryItemRecord, SavedPaperSearchRecord
from app.db.session import get_db
from app.modules.paper_explorer.models import PaperCollectionCreate, PaperLibraryItem, PaperLibraryPatch, PaperLibraryUpsert, PaperSearchRequest, PaperSummaryRequest, PaperSummaryResponse, SavedPaperSearch, SavedPaperSearchCreate
from app.modules.paper_explorer.service import library_dict, patch_library, persist_search_results, save_search, search_papers, summarize_paper, upsert_library

router = APIRouter()


@router.post("/search")
async def search(payload: PaperSearchRequest, db: Session = Depends(get_db)):
    results, provider, error = await search_papers(payload)
    created, updated = persist_search_results(db, results) if results else (0, 0)
    if error:
        key=f"paper-provider-failed:{provider}:{datetime.now().astimezone().strftime('%Y%m%d%H')}"
        if not db.query(NotificationEventRecord).filter_by(user_id=settings.single_user_id,dedupe_key=key).first():
            db.add(NotificationEventRecord(user_id=settings.single_user_id,event_type="paper_provider_failed",severity="error",title="논문 검색 공급자 연결 실패",message=error,data_json={"provider":provider},dedupe_key=key)); db.commit()
    return {"results": results, "provider": provider, "provider_error": error, "is_mock": False, "created_count": created, "updated_count": updated}


@router.post("/saved-searches", response_model=SavedPaperSearch)
def create_saved_search(payload: SavedPaperSearchCreate, db: Session = Depends(get_db)):
    return save_search(db, payload, settings.single_user_id)


@router.get("/saved-searches", response_model=list[SavedPaperSearch])
def saved_searches(db: Session = Depends(get_db)):
    return list(db.scalars(select(SavedPaperSearchRecord).where(SavedPaperSearchRecord.user_id == settings.single_user_id).order_by(SavedPaperSearchRecord.created_at.desc())).all())


@router.post("/library", response_model=PaperLibraryItem)
def add_library(payload: PaperLibraryUpsert, db: Session = Depends(get_db)):
    try: return upsert_library(db, payload, settings.single_user_id)
    except LookupError as exc: raise HTTPException(404, str(exc)) from exc


@router.patch("/library/{item_id}", response_model=PaperLibraryItem)
def update_library(item_id: str, payload: PaperLibraryPatch, db: Session = Depends(get_db)):
    try: return patch_library(db, item_id, payload, settings.single_user_id)
    except LookupError as exc: raise HTTPException(404, str(exc)) from exc


@router.get("/library", response_model=list[PaperLibraryItem])
def get_library(favorites_only: bool = False, tag: str = "", collection_id: str = "", db: Session = Depends(get_db)):
    query = select(PaperLibraryItemRecord).where(PaperLibraryItemRecord.user_id == settings.single_user_id)
    if favorites_only: query = query.where(PaperLibraryItemRecord.favorite.is_(True))
    if collection_id: query = query.where(PaperLibraryItemRecord.collection_id == collection_id)
    items = list(db.scalars(query.order_by(PaperLibraryItemRecord.created_at.desc())).all())
    if tag: items = [item for item in items if tag in item.tags_json]
    return [library_dict(item) for item in items]

@router.delete("/library/{item_id}")
def delete_library(item_id: str, db: Session = Depends(get_db)):
    item=db.scalar(select(PaperLibraryItemRecord).where(PaperLibraryItemRecord.id==item_id,PaperLibraryItemRecord.user_id==settings.single_user_id))
    if not item: raise HTTPException(404,"library item not found")
    db.delete(item); db.commit(); return {"deleted":True}


@router.post("/collections")
def create_collection(payload: PaperCollectionCreate, db: Session = Depends(get_db)):
    record = PaperCollectionRecord(user_id=settings.single_user_id, **payload.model_dump()); db.add(record); db.commit(); db.refresh(record); return record


@router.get("/collections")
def collections(db: Session = Depends(get_db)):
    return list(db.scalars(select(PaperCollectionRecord).where(PaperCollectionRecord.user_id == settings.single_user_id)).all())


@router.post("/summarize", response_model=PaperSummaryResponse)
async def summarize(payload: PaperSummaryRequest, db: Session = Depends(get_db)):
    try:
        result=await summarize_paper(payload)
        key=f"paper-summary-complete:{payload.doi or payload.title}:{payload.mode}"
        if not db.query(NotificationEventRecord).filter_by(user_id=settings.single_user_id,dedupe_key=key).first():
            db.add(NotificationEventRecord(user_id=settings.single_user_id,event_type="paper_summary_completed",severity="info",title="논문 요약 완료",message=payload.title,data_json={"doi":payload.doi,"mode":payload.mode},dedupe_key=key)); db.commit()
        return result
    except RuntimeError as exc: raise HTTPException(503, "한국어 AI 요약을 사용하려면 OPENAI_API_KEY를 설정해 주세요.") from exc
    except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as exc:
        key=f"paper-summary-failed:{payload.doi or payload.title}:{datetime.now().astimezone().date()}"
        if not db.query(NotificationEventRecord).filter_by(user_id=settings.single_user_id,dedupe_key=key).first(): db.add(NotificationEventRecord(user_id=settings.single_user_id,event_type="paper_summary_failed",severity="error",title="논문 요약 실패",message=str(exc),data_json={"doi":payload.doi},dedupe_key=key)); db.commit()
        raise HTTPException(502, f"한국어 요약 생성에 실패했습니다: {exc}") from exc
