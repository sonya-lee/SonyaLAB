from typing import Protocol

class PaperSearchProvider(Protocol):
    async def search(self, *, query: str, limit: int) -> list[dict]:
        ...
