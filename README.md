# Sonya Lab

항공권, 논문과 외부 정보를 독립적으로 수집·분석하는 개인용 서비스입니다. Sonya OS 및 Sonya Life와 저장소, 포트, 프로세스, 데이터베이스를 공유하지 않습니다.

## 현재 실제 동작

- PostgreSQL/SQLite repository, Alembic migration
- watch별 항공권 수집 주기, 일시정지, 다음/마지막 실행 시각
- Mock 항공권 provider 수동·자동 수집, 현재가·30일 통계·장기 이력
- 검증된 provider URL만 허용하는 외부 구매 링크 구조
- Crossref 실제 논문 검색과 설명 가능한 랭킹
- 논문 즐겨찾기, 읽기 상태, 태그, 메모, 컬렉션 데이터 모델/API
- 항공권·논문 독립 scheduler job과 실행 이력
- 내부 notification event와 dedupe
- OpenAI 키 설정 시 초록 범위 기반 한국어 요약

실제 항공권 가격은 아직 Mock입니다. 유료 계약/API 키 없이 실제 가격이나 구매 링크가 있다고 표시하지 않습니다.

## 독립 포트

| 구성요소 | 포트 |
|---|---:|
| Frontend | 5175 |
| Backend | 8002 |
| PostgreSQL host | 55432 |
| PostgreSQL container | 5432 |

## Windows 빠른 시작

```powershell
cd C:\dev\SonyaLAB
docker compose -p sonya-lab up -d postgres
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m alembic upgrade head
cd ..\frontend
npm.cmd install
cd ..
.\scripts\start-all.ps1
```

웹: `http://localhost:5175`, API 문서: `http://localhost:8002/docs`

개별 실행은 `start-backend.ps1`, `start-frontend.ps1`, `start-scheduler.ps1`을 사용합니다. `stop-lab.ps1`은 Sonya Lab runtime PID로 시작한 프로세스만 종료하며 포트 기준 kill을 하지 않습니다.

## 주요 환경변수

```env
DATABASE_URL=postgresql+psycopg://sonya_lab_app:sonya_lab_dev@localhost:55432/sonya_lab
FLIGHT_PROVIDER=mock
PAPER_PROVIDER=crossref
MINIMUM_COLLECTION_INTERVAL_MINUTES=60
OPENAI_API_KEY=
FLIGHT_BOOKING_ALLOWED_DOMAINS=
SINGLE_USER_MODE=true
SINGLE_USER_ID=local-user
```

API 키 값은 설정 API나 프런트에 반환하지 않고 설정 여부만 표시합니다. 개발용 비밀번호는 개인 PC용 기본값이며 외부 배포 전에 변경해야 합니다.

## 데이터 위치

- 운영 데이터: `sonya_lab` PostgreSQL DB
- Docker 미설치 로컬 fallback: `backend/data/sonya_lab.db` SQLite
- 즐겨찾기: `paper_library_items`
- 실행 이력: `scheduler_runs`
- 내부 알림: `notification_events`
- 프로세스 PID: `runtime/`
- 로그: `logs/`

Mock/실제 provider, 수집 주기, 가격 방법론은 `docs/`를 확인하세요.

## 안전한 실행 점검

Windows에서 실행 전 다음 명령으로 필수 파일과 포트 상태를 확인할 수 있습니다.

```powershell
.\scripts\preflight.ps1
.\scripts\status.ps1
```

- `preflight.ps1`은 포트를 점유한 프로세스를 종료하지 않고, PID와 프로세스 이름만 안내합니다.
- backend 시작 시 Alembic migration을 먼저 적용합니다. DB 연결 또는 migration이 실패하면 서버를 시작하지 않습니다.
- frontend/backend는 `0.0.0.0`에 바인딩되므로 같은 내부망의 다른 기기에서도 접속할 수 있습니다. Windows 방화벽에서 5175와 8002의 인바운드 허용이 필요할 수 있습니다.
- 로컬 접속: `http://localhost:5175`
- 내부망 접속: `http://<PC의 내부 IP>:5175`

## 보안 주의

실제 `backend/.env`, `runtime/`, `logs/`, `backend/data/`, `.venv/`, `node_modules/`는 저장소나 공유 ZIP에 포함하지 마세요. 공유용 압축은 아래 스크립트를 사용합니다.

```powershell
.\scripts\export-source.ps1
```

