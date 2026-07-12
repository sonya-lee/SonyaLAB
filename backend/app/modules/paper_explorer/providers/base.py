from typing import Protocol
from app.modules.paper_explorer.models import PaperSearchRequest


class PaperSearchProvider(Protocol):
    name: str
    async def search(self, payload: PaperSearchRequest) -> list[dict]: ...
    async def health_check(self) -> tuple[bool, str | None]: ...
