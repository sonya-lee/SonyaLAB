# Windows setup

## PostgreSQL만 실행

```powershell
cd C:\dev\SonyaLAB
docker compose -p sonya-lab up -d postgres
```

Docker가 아직 없다면 로컬 영구 SQLite로 먼저 사용할 수 있습니다.

```env
DATABASE_URL=sqlite:///./data/sonya_lab.db
```

SQLite도 서버 재시작 후 데이터가 유지됩니다. PostgreSQL 전환 시 `.env`의 URL을 원래 값으로 되돌리고 `alembic upgrade head`를 실행합니다.

## Backend만 실행

```powershell
cd C:\dev\SonyaLAB\backend
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

## Frontend만 실행

```powershell
cd C:\dev\SonyaLAB\frontend
npm.cmd install
npm.cmd run dev
```

## Scheduler만 실행

```powershell
cd C:\dev\SonyaLAB\backend
.\.venv\Scripts\python.exe -m app.scheduler.runner
```

## 스크립트

```powershell
.\scripts\start-all.ps1
.\scripts\status.ps1
.\scripts\stop-lab.ps1
```

PowerShell 정책이 스크립트를 막으면 현재 세션에만 `Set-ExecutionPolicy -Scope Process Bypass`를 적용합니다. 다른 Sonya 프로젝트는 종료하거나 검사할 필요가 없습니다.

수집 주기는 각 watch 화면에서 변경합니다. 항공권 기본 옵션은 1/3/6/12/24시간이며 최소 60분입니다. Provider는 backend `.env`의 `FLIGHT_PROVIDER`, `PAPER_PROVIDER`로 선택합니다.
