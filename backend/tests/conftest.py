import os
from pathlib import Path
test_data = Path(__file__).resolve().parents[1] / "data"
test_data.mkdir(parents=True, exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{(test_data / 'test_sonya_lab.db').as_posix()}"
os.environ["FLIGHT_PROVIDER"] = "mock"
os.environ["PAPER_PROVIDER"] = "crossref"
os.environ["OPENAI_API_KEY"] = ""
import pytest
from app.db.models import Base
from app.db.session import SessionLocal, engine

@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine); yield

@pytest.fixture
def db():
    with SessionLocal() as session: yield session
