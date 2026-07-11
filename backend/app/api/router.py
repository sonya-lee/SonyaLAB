from fastapi import APIRouter

from app.modules.flight_watcher.router import router as flight_router
from app.modules.paper_explorer.router import router as paper_router

api_router = APIRouter()

@api_router.get("/modules")
def modules() -> list[dict[str, str]]:
    return [
        {
            "id": "flight-watcher",
            "name": "Flight Watcher",
            "description": "항공권 가격을 기록하고 평소 대비 하락을 감지합니다.",
        },
        {
            "id": "paper-explorer",
            "name": "Paper Explorer",
            "description": "주요 논문을 검색하고 이야기형으로 요약합니다.",
        },
    ]

api_router.include_router(flight_router, prefix="/flights", tags=["flights"])
api_router.include_router(paper_router, prefix="/papers", tags=["papers"])
