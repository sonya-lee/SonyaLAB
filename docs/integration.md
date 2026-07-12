# Future integration

이번 구현은 다른 Sonya 저장소나 프로세스를 호출하지 않습니다. 내부 이벤트는 `notification_events`에 공통 구조로 기록합니다.

```json
{"event_type":"flight_price_drop","source":"sonya-lab","severity":"important","title":"...","message":"...","data_json":{},"dedupe_key":"..."}
```

향후 별도 notification relay가 이 outbox를 읽어 OS/Life로 전달할 수 있습니다. 비즈니스 service는 수신 앱 DB, Push subscription, 로그인 구현을 알지 않습니다. 공통 인증도 외부 service가 검증한 user ID를 request context로 주입하는 방식으로 교체합니다.
