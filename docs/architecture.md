# Architecture

```text
Frontend
   |
   v
FastAPI
   |
   +-- Flight Watcher
   |     +-- Search Provider
   |     +-- Price History
   |     +-- Drop Detector
   |
   +-- Paper Explorer
   |     +-- Paper Provider
   |     +-- Ranking
   |     +-- Summary Generator
   |
   +-- Notification Service
   |
   +-- Scheduler
```

## Sonya 연동 방식

```text
Sonya Lab
  └─ notification event
       ├─ Sonya OS: Windows popup
       └─ Sonya Life: 모바일 웹 기록 및 대시보드
```

권장 이벤트 예시:

```json
{
  "event_type": "flight_price_drop",
  "source": "sonya-lab",
  "created_at": "2026-07-11T20:00:00+09:00",
  "title": "도쿄 항공권 가격 하락",
  "message": "최근 기준 가격보다 31.2% 저렴합니다.",
  "data": {
    "origin": "ICN",
    "destination": "NRT",
    "current_price_krw": 289000,
    "baseline_price_krw": 420000
  }
}
```
