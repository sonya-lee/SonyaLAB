# Ports and process isolation

| Resource | Sonya Lab value |
|---|---|
| Frontend | 5175 |
| Backend | 8002 |
| PostgreSQL host | 55432 |
| Compose project | sonya-lab |
| DB name | sonya_lab |
| DB user | sonya_lab_app |
| runtime PID | `runtime/{component}.pid` |
| logs | `logs/{component}.*.log` |

Vite `strictPort=true`이므로 5175가 점유되면 다른 포트로 몰래 이동하지 않고 실패합니다. 실행 스크립트는 포트 점유자를 종료하지 않습니다. `stop-lab.ps1`은 자신이 기록한 PID와 SonyaLAB 명령행을 확인합니다.
