from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.modules.flight_watcher.airports import search_airports
from app.modules.flight_watcher.models import FlightOffer, FlightPriceObservationCreate, FlightWatch, FlightWatchCreate, FlightWatchSummary, FlightWatchUpdate, PriceDropEvaluation
from app.modules.flight_watcher.service import add_observation, create_watch, get_watch_record, list_observations, list_watches, update_watch, watch_summary

router = APIRouter()


@router.get("/airports")
def get_airports(q: str = "") -> list[dict[str, str]]:
    return search_airports(q)


@router.post("/watches", response_model=FlightWatch)
def add_watch(payload: FlightWatchCreate, db: Session = Depends(get_db)):
    try:
        return create_watch(db, payload, settings.single_user_id)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/watches", response_model=list[FlightWatchSummary])
def get_watches(db: Session = Depends(get_db)):
    return list_watches(db, settings.single_user_id)


@router.get("/watches/{watch_id}", response_model=FlightWatchSummary)
def get_watch(watch_id: str, db: Session = Depends(get_db)):
    try:
        return watch_summary(db, get_watch_record(db, watch_id, settings.single_user_id))
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.patch("/watches/{watch_id}", response_model=FlightWatch)
def patch_watch(watch_id: str, payload: FlightWatchUpdate, db: Session = Depends(get_db)):
    try:
        return update_watch(db, watch_id, payload, settings.single_user_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/watches/{watch_id}/observations", response_model=list[FlightOffer])
def get_observations(watch_id: str, days: int = Query(365, ge=1, le=365), db: Session = Depends(get_db)):
    try:
        return list_observations(db, watch_id, settings.single_user_id, days)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/watches/{watch_id}/observations", response_model=PriceDropEvaluation)
def post_observation(watch_id: str, payload: FlightPriceObservationCreate, db: Session = Depends(get_db)):
    try:
        return add_observation(db, watch_id, payload, settings.single_user_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
