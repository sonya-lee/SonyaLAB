from app.modules.paper_explorer.models import (
    PaperSearchRequest,
    PaperSummaryRequest,
    PaperSummaryResponse,
)

def search_papers(payload: PaperSearchRequest) -> list[dict]:
    return [
        {
            "title": f"Mock paper about {payload.query}",
            "journal": "Example Journal",
            "year": 2026,
            "abstract": "실제 논문 검색 API 연결 전의 예시 데이터입니다.",
            "score": 0.95,
        }
    ]

def summarize_paper(payload: PaperSummaryRequest) -> PaperSummaryResponse:
    if payload.mode == "comic":
        text = (
            "1컷: 연구자가 문제를 발견합니다.\n"
            "2컷: 실험으로 원인을 추적합니다.\n"
            "3컷: 핵심 메커니즘이 드러납니다.\n"
            "4컷: 현장 적용 가능성과 한계를 정리합니다."
        )
    elif payload.mode == "engineer":
        text = "문제 정의, 실험 조건, 핵심 결과, 공정 적용성, 한계 순서로 정리할 예정입니다."
    elif payload.mode == "story":
        text = "표면이라는 작은 도시에서 오염원과 작용기가 만나며 벌어지는 이야기로 재구성할 예정입니다."
    else:
        text = "배경, 방법, 결과, 결론 순서의 일반 요약을 생성할 예정입니다."

    return PaperSummaryResponse(title=payload.title, mode=payload.mode, summary=text)
