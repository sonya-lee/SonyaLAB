import pytest
from app.api import system

class Healthy:
    async def health_check(self): return True, None

@pytest.mark.asyncio
async def test_database_failure_is_reported(monkeypatch):
    monkeypatch.setattr(system,"database_health",lambda:(False,"database unavailable"))
    monkeypatch.setattr(system,"get_flight_provider",lambda:Healthy())
    monkeypatch.setattr(system,"get_paper_provider",lambda:Healthy())
    result=await system.public_settings()
    assert result["database"]=={"connected":False,"error":"database unavailable"}

def test_health_does_not_require_database():
    from fastapi.testclient import TestClient
    from app.main import app
    response=TestClient(app).get("/health")
    assert response.status_code==200 and response.json()["port"]==8002
