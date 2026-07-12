from fastapi import APIRouter

from app.api.system import router as system_router
from app.modules.flight_watcher.router import router as flight_router
from app.modules.paper_explorer.router import router as paper_router
from app.scheduler.router import router as scheduler_router

api_router = APIRouter()

@api_router.get("/modules")
def modules() -> list[dict[str, str]]:
    return [
        {"id":"flight-watcher","name":"항공권 감시","description":"현재 구매 가능한 최저가와 수집 가격 흐름을 추적합니다."},
        {"id":"paper-explorer","name":"논문 탐색","description":"논문을 검색·저장하고 근거 범위에 맞게 요약합니다."},
    ]

api_router.include_router(flight_router,prefix="/flights",tags=["flights"])
api_router.include_router(paper_router,prefix="/papers",tags=["papers"])
api_router.include_router(scheduler_router,prefix="/scheduler",tags=["scheduler"])
api_router.include_router(system_router,prefix="/system",tags=["system"])
