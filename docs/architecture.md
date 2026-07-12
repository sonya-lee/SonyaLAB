# Architecture

```text
Vue :5175 ─proxy─> FastAPI :8002 ─> PostgreSQL localhost:55432
                         │
                         ├─ flight_watcher ─ provider factory
                         ├─ paper_explorer ─ provider factory
                         ├─ internal notification events
                         └─ scheduler API/history

Independent scheduler process ─> flight_collection job
                              └─> paper_collection job
```

Frontend, backend, scheduler, PostgreSQL은 각각 독립 프로세스입니다. Backend 시작 시 scheduler를 등록하지 않으므로 uvicorn worker/reload 수와 무관하게 중복 scheduler가 생기지 않습니다.

현재 인증은 `SINGLE_USER_ID=local-user`를 주입합니다. 모든 사용자 소유 테이블은 `user_id`를 가지며 service 함수는 인증 공급자가 아닌 user ID만 받습니다. 향후 공통 인증 API가 user ID를 제공하도록 교체할 수 있습니다.

다른 Sonya 저장소를 import하거나 DB를 읽지 않습니다. 통합은 향후 공통 notification/auth 인터페이스로만 수행합니다.
