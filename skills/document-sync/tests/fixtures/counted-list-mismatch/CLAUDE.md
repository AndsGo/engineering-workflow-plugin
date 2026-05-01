# Test Fixture — Counted-List Mismatch

This fixture tests F2 (counted enumerations check). The heading says "5 total" but only 4 bullets follow.

## API Endpoints (5 total)

- `GET /api/v1/health` — public health
- `GET /api/v1/status` — service status
- `POST /api/v1/echo` — debug echo
- `DELETE /api/v1/cache` — clear cache

(Expected document-sync behavior: surface the count mismatch with line ref + suggested fix — either change "5" to "4" or add a missing bullet.)
