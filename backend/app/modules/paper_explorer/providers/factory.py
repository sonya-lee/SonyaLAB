from app.core.config import settings
from app.modules.paper_explorer.providers.base import PaperSearchProvider
from app.modules.paper_explorer.providers.crossref import CrossrefPaperProvider


def get_paper_provider(name: str | None = None) -> PaperSearchProvider:
    provider_name = (name or settings.paper_provider).lower()
    if provider_name == "crossref":
        return CrossrefPaperProvider()
    raise ValueError(f"Paper provider '{provider_name}' is not implemented")
