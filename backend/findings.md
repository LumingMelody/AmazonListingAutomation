# Findings & Decisions

## Requirements
- Execute P3 Task 2 from `2026-03-04-p3-database-engine-integration.md`.
- Follow TDD workflow: failing tests first, then implementation, then integration, then all tests passing.
- Implement:
  - `EngineAdapter` interface
  - `BU2AmaAdapter`
  - `LocalFallbackAdapter`
  - Adapter factory selection
  - Excel/FollowSell endpoint integration to adapter abstraction
  - Integration tests
- Reference BU2Ama backend implementation for behavior alignment.

## Research Findings
- Original `app/api/excel.py` and `app/api/followsell.py` were hardcoded local placeholders with no adapter abstraction.
- Existing endpoint contracts are JSON-based:
  - `POST /api/process`
  - `POST /api/followsell/process`
- Existing workflow tests verify compliance block/pass behavior for both endpoints and had to remain green.
- There was no `app/services/bu2ama` package in this repo before implementation.
- BU2Ama reference project uses internal `app.*` imports; direct in-process import into this project risks namespace conflicts.
- HTTP adapter boundary is safer for decoupling and aligns with “API layer should not couple to BU2Ama file structure”.

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Keep adapter contract sync (`EngineAdapter` protocol with DTOs) | Matches current processing pattern and simplifies endpoint use |
| Implement `BU2AmaAdapter` via HTTP API calls | Avoids Python package namespace conflict and file-structure coupling |
| Normalize output fields (`output_file`/`output_filename`/nested `data`) | BU2Ama-style responses can vary by endpoint |
| Use factory mode `auto/local/external` | Supports explicit control and production fallback behavior |
| In `auto` mode, add external API health probe before selecting external | Avoids runtime 503 regressions when BU2Ama path exists but service is down |
| Preserve compliance precheck before adapter invocation | Required by existing contract and tests |
| Map `EngineNotAvailableError -> 503`, `EngineExecutionError -> 500` | Matches P3 plan error-handling guidance |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| BU2Ama in-process import risks module namespace collision (`app.*`) | Use remote API adapter boundary instead |
| Full-suite regressions: clean workflow endpoints returned `503` due external not running | Added health-check gating in factory `auto` mode and fallback to local |

## Resources
- `../docs/plans/2026-03-04-p3-database-engine-integration.md`
- `app/api/excel.py`
- `app/api/followsell.py`
- `app/config.py`
- `tests/test_workflow_integration_api.py`
- `tests/test_bu2ama_adapter.py`
- `tests/test_bu2ama_factory.py`
- `tests/test_excel_api_adapter_integration.py`
- `tests/test_followsell_api_adapter_integration.py`
- `/Users/melodylu/PycharmProjects/BU2Ama/backend/app/api/excel.py`
- `/Users/melodylu/PycharmProjects/BU2Ama/backend/app/api/followsell.py`

## Visual/Browser Findings
- N/A
