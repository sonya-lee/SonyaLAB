# Sonya Lab

외부 정보를 수집·분석·요약하고 조건에 따라 알림을 보내는 개인용 탐색 비서입니다.

## 1. 주요 모듈

- Flight Watcher
  - 항공권 검색 조건 저장
  - 가격 이력 저장
  - 기준 가격 대비 하락률 계산
  - 조건 충족 시 알림 이벤트 생성

- Paper Explorer
  - 키워드 기반 논문 검색
  - 저널 및 논문 메타데이터 저장
  - 일반 요약 / 엔지니어 요약 / 이야기형 요약
  - 향후 만화 컷 구성 및 이미지 생성 연동

## 2. 기술 구조

- Frontend: Vue 3 + Vite
- Backend: FastAPI
- Database: PostgreSQL 예정
- Scheduler: Python 기반 주기 실행
- AI: 공급자 독립형 adapter 구조
- Notification: Sonya OS / Sonya Life 연동을 고려한 event 구조

## 3. 실행

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## 4. 초기 API

- `GET /health`
- `GET /api/modules`
- `POST /api/flights/watches`
- `GET /api/flights/watches`
- `POST /api/papers/search`
- `POST /api/papers/summarize`

현재는 메모리 기반 mock 구조이며, 다음 단계에서 PostgreSQL과 실제 외부 API를 연결합니다.

## 5. 개발 원칙

1. sonya-os와 sonya-life 저장소는 직접 수정하지 않습니다.
2. 연동은 HTTP API 또는 webhook event로만 합니다.
3. 외부 API 호출 코드는 provider 폴더에 격리합니다.
4. 수집 원본과 AI가 생성한 결과를 구분해 저장합니다.
5. 가격 비교 기준과 논문 평가 기준은 설명 가능하게 기록합니다.
