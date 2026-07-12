# 2026-07-12 safety and independent-run hardening

## Changes

- Added `.gitattributes` to prevent repeated LF/CRLF noise.
- Added `scripts/common.ps1` for safe PID parsing and port-owner diagnostics.
- Added `scripts/preflight.ps1` to check prerequisites without killing processes.
- Backend startup now applies Alembic migrations before launching and binds to `0.0.0.0:8002` for LAN use.
- Frontend startup uses strict `0.0.0.0:5175` binding and reports the process occupying the port.
- Status command now shows both owned PIDs and actual port owners.
- Added `scripts/export-source.ps1` to create a source-only ZIP that excludes secrets, databases, logs, PIDs, Git metadata, virtual environments, and node modules.

## Validation

- Backend test suite: 12 passed.
- Frontend application source was not changed in this patch.
- A Linux frontend rebuild was not used as validation because the uploaded archive contained Windows-specific `node_modules`; run `npm.cmd install` and `npm.cmd run build` on Windows after applying the patch.
