# Scheduler

Scheduler는 `python -m app.scheduler.runner` 독립 프로세스입니다. Backend에 내장하지 않아 reload/multi-worker 중복 등록을 피합니다.

Job:

- `flight_collection`: watch별 provider 검색과 offer 저장
- `paper_collection`: 저장 검색별 신규 검색과 paper upsert

각 job은 `scheduler_runs`에 manual/scheduled, provider, 시작/종료, 상태, 처리·생성·수정 수, 오류, metadata를 기록합니다. 같은 job_type/target_id가 `running`이면 중복 실행을 거부합니다. 한 target 실패는 다음 target 실행을 막지 않습니다.

Provider 미구현/키 미설정은 `skipped` 또는 명시적 `failed`로 기록합니다. 화면의 “지금 검색”과 `/api/scheduler/.../run`은 동일 job을 manual trigger로 실행합니다.
