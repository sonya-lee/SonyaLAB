import html
import re
from datetime import date
from typing import Any

import httpx

from app.core.config import settings
from app.modules.paper_explorer.models import PaperSearchRequest


def _first(value: Any, default: str = "") -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    return str(value) if value else default


def _plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(value))).strip()


def _published_year(item: dict[str, Any]) -> int | None:
    for key in ("published-online", "published-print", "published", "issued"):
        parts = item.get(key, {}).get("date-parts", [])
        if parts and parts[0]:
            return int(parts[0][0])
    return None


class CrossrefPaperProvider:
    name = "crossref"
    base_url = "https://api.crossref.org/works"

    async def search(self, payload: PaperSearchRequest) -> list[dict]:
        from_year = date.today().year - payload.published_within_years + 1
        query = " ".join(filter(None, [payload.query, payload.field, payload.author, payload.journal]))
        params = {
            "query.bibliographic": query,
            "filter": f"from-pub-date:{from_year}-01-01,type:journal-article",
            "rows": payload.limit,
            "sort": {"relevance": "relevance", "newest": "published", "citations": "is-referenced-by-count"}[payload.sort_by],
            "order": "desc",
            "select": "DOI,title,abstract,author,container-title,published,published-online,published-print,issued,URL,is-referenced-by-count,license,score",
        }
        if settings.crossref_mailto:
            params["mailto"] = settings.crossref_mailto

        headers = {"user-agent": "SonyaLab/0.1 (personal research discovery service)"}
        async with httpx.AsyncClient(timeout=settings.paper_api_timeout_seconds, headers=headers) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
        items = response.json().get("message", {}).get("items", [])
        if not items:
            return []

        top_score = max(float(item.get("score") or 0) for item in items) or 1
        results = []
        for item in items:
            doi = item.get("DOI", "")
            authors = [
                " ".join(filter(None, (author.get("given"), author.get("family"))))
                for author in item.get("author", [])
            ]
            results.append({
                "external_id": doi or item.get("URL", ""),
                "provider": self.name,
                "doi": doi,
                "title": _plain_text(_first(item.get("title"), "제목 없음")),
                "authors": authors,
                "journal": _plain_text(_first(item.get("container-title"), "학술지 정보 없음")),
                "year": _published_year(item),
                "abstract": _plain_text(item.get("abstract", "")),
                "citation_count": int(item.get("is-referenced-by-count") or 0),
                "url": item.get("URL") or (f"https://doi.org/{doi}" if doi else ""),
                "license_available": bool(item.get("license")),
                "score": round(float(item.get("score") or 0) / top_score, 3),
                "source_scope": "abstract" if item.get("abstract") else "metadata_only",
                "metadata_sources": {"bibliographic": "crossref", "citations": "crossref", "open_access": None, "full_text": "doi"},
            })
        return [item for item in results if item["citation_count"] >= payload.minimum_citations]

    async def health_check(self) -> tuple[bool, str | None]:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(self.base_url, params={"rows": 0})
            return response.is_success, None if response.is_success else f"HTTP {response.status_code}"
        except httpx.HTTPError as exc:
            return False, str(exc)
