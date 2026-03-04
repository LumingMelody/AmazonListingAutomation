# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Amazon Listing Automation System - 亚马逊上新跟卖自动化系统

A platform for automating Amazon e-commerce operations from product selection to iterative testing. The system implements risk prevention, quality assurance, data analytics, alerting, auto-tiering, and competitor monitoring.

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, PostgreSQL, Redis, Celery
- Frontend: React 18 + TypeScript, Vite, Tailwind CSS, React Query, Zustand

## Development Workflow (CRITICAL)

**Role Division:**
- **Codex**: Implements all code changes
- **Claude**: Reviews code, provides feedback, and validates implementation

**Process for New Requirements:**
1. Discuss requirements with Codex first
2. Codex proposes implementation approach
3. Claude reviews and provides feedback
4. Finalize solution together before implementation
5. Codex implements the code
6. Claude reviews the implementation

**Never:**
- Claude should NOT write implementation code directly
- Claude should NOT skip the discussion phase with Codex
- Start coding without a reviewed plan

**Using Codex:**
```bash
# Delegate implementation to Codex
~/.claude/skills/codex/scripts/ask_codex.sh "Your task description" \
  --file path/to/relevant/file.py \
  --reasoning medium
```

## Development Commands

### Backend

```bash
cd backend

# Run tests (CRITICAL: Always set PYTHONPATH)
PYTHONPATH=. pytest tests/ -v

# Run specific test
PYTHONPATH=. pytest tests/test_compliance_service.py -v

# Run tests with coverage
PYTHONPATH=. pytest --cov=app --cov-report=html

# Start development server
uvicorn app.main:app --reload --port 8000

# Start with custom host/port
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

## Architecture

### Three-Layer Service Architecture

1. **API Layer** (`backend/app/api/`)
   - FastAPI routers handling HTTP requests
   - Request/response validation with Pydantic
   - Error handling with HTTPException
   - Files: `compliance.py`, `experiments.py`, `competitor_monitor.py`, `analytics.py`, `alerts.py`, `excel.py`, `followsell.py`

2. **Service Layer** (`backend/app/core/`)
   - Business logic and domain services
   - Stateless, reusable components
   - Files: `compliance_service.py`, `listing_qa_service.py`, `experiment_service.py`, `competitor_monitor_service.py`, `data_import_service.py`, `alert_service.py`

3. **Model Layer** (`backend/app/models/`)
   - Pydantic models for data validation
   - Database schema definitions
   - Files: `compliance.py`, `experiment.py`, `analytics.py`

### Key Design Patterns

**In-Memory Storage for Testing:**
- API endpoints use in-memory dictionaries (e.g., `_lifecycle_store`) for development/testing
- Production requires database integration
- Example: `experiments.py` line 15

**Service Composition:**
- API endpoints instantiate and call service methods
- Services are stateless and can be reused
- Example: `ExperimentService` used by both `experiments.py` and tests

**TDD Workflow:**
- All features developed test-first
- Test files mirror source structure: `app/core/X.py` → `tests/test_X.py`
- API tests use FastAPI TestClient

### Phase-Based Development

**P0 (Completed):** Risk Prevention & QA
- Compliance checking (trademarks, IP words, forbidden words)
- Listing QA (field completeness, title/bullet validation)
- Workflow integration (Excel/FollowSell processing)
- Database: `001_compliance_tables.sql` (5 tables)

**P1 (Completed):** Data Pipeline & Alerts
- Data import (ad performance, listing metrics)
- Alert service (CVR drop, refund rate spike, chargeback rate)
- Analytics API and monitoring dashboard
- Database: `002_data_pipeline_tables.sql` (4 tables)

**P2 (Completed):** Auto-Tiering & Competitor Monitoring
- Experiment service (auto-tiering algorithm, stage determination)
- Competitor monitor (price analysis, rank detection, recommendations)
- Experiment dashboard frontend
- Database: `003_experiment_tables.sql` (4 tables)

### Critical Implementation Details

**Auto-Tiering Algorithm** (`experiment_service.py`):
- Score calculation (0-100): CVR (40pts) + Refund Rate (30pts) + Sales (30pts)
- Stage determination: test (<40), observe (40-60), scale (60-80), eliminate (>80)
- Decision mapping: continue_test, continue_monitor, add_variants, discontinue
- Minimum sample size: 100 sessions, 10 orders

**Competitor Monitoring** (`competitor_monitor_service.py`):
- Price analysis: 7-day average comparison, trend detection (±5% threshold)
- Rank analysis: Average rank comparison, status detection (±100 rank threshold)
- Recommendation generation: adjust_price (high priority), increase_ads (medium priority)

**Risk Assessment** (`compliance_service.py`):
- Multi-level risk scoring: safe, low, medium, high, critical
- Trademark detection: Nike, Adidas, Apple, etc.
- IP word detection: Disney, Marvel, etc.
- Forbidden word detection: fake, replica, etc.

## Database Migrations

Migrations are SQL files in `backend/migrations/`:
- `001_compliance_tables.sql` - Compliance rules, blacklist, QA checkpoints, approval records
- `002_data_pipeline_tables.sql` - Ad performance, listing metrics, alert rules, alert history
- `003_experiment_tables.sql` - Experiment configs, listing lifecycle, competitor snapshots, action recommendations

**Note:** Currently no migration runner configured. Apply manually or integrate Alembic.

## Testing Strategy

**Test Structure:**
- Service tests: Unit tests for business logic
- API tests: Integration tests using TestClient
- Frontend integration tests: Contract tests checking component existence

**Running Tests:**
```bash
# CRITICAL: Always set PYTHONPATH=. when running pytest
cd backend
PYTHONPATH=. pytest tests/ -v

# Without PYTHONPATH, you'll get: ModuleNotFoundError: No module named 'app'
```

**Test Coverage (as of 2026-03-04):**
- 46 tests passing
- Coverage: P0 (21 tests), P1 (10 tests), P2 (12 tests), Integration (3 tests)

## API Endpoints

**Base URL:** `http://localhost:8000`

**Compliance:**
- `POST /api/compliance/check-text` - Check text for violations
- `POST /api/compliance/check-listing` - Check full listing
- `POST /api/compliance/batch-check` - Batch check multiple listings

**Experiments (Auto-Tiering):**
- `POST /api/experiments/evaluate-listing` - Evaluate metrics and get decision
- `POST /api/experiments/lifecycle` - Create lifecycle record
- `GET /api/experiments/lifecycle` - List lifecycle records (filter by asin/status/stage)
- `PATCH /api/experiments/lifecycle/{asin}` - Update lifecycle status
- `POST /api/experiments/recommendations` - Generate recommendations

**Competitor Monitor:**
- `POST /api/competitor-monitor/track` - Track competitor with price/rank analysis
- `POST /api/competitor-monitor/price-analysis` - Analyze price trends
- `POST /api/competitor-monitor/recommendations` - Generate action suggestions

**Analytics:**
- `POST /api/analytics/import/ad-performance` - Import ad data
- `POST /api/analytics/import/listing-metrics` - Import listing data
- `GET /api/analytics/metrics/summary` - Get metrics summary

**Alerts:**
- `POST /api/alerts/check` - Check metrics against thresholds
- `GET /api/alerts/active` - Get active alerts
- `POST /api/alerts/{id}/resolve` - Resolve alert

**Workflow:**
- `POST /api/excel/process` - Process Excel file
- `POST /api/followsell/process` - Process follow-sell listing

## Frontend Architecture

**Pages:**
- `Dashboard.tsx` - P1 monitoring dashboard (metrics + alerts)
- `ExperimentDashboard.tsx` - P2 auto-tiering dashboard (listing stages)
- `ExcelProcessor.tsx` - Excel upload and processing

**Components:**
- `ComplianceAlert.tsx` - Risk warning display
- `MetricCard.tsx` - Metric display with trend indicators
- `AlertList.tsx` - Active alerts list
- `ListingStageCard.tsx` - Listing stage card (test/observe/scale/eliminate)

**Navigation:**
- App.tsx manages page state with simple button navigation
- Three pages: 监控看板, 自动分层, Excel 处理

## Common Issues

**ModuleNotFoundError when running tests:**
```bash
# Wrong:
pytest tests/

# Correct:
PYTHONPATH=. pytest tests/
```

**datetime.utcnow() deprecation warnings:**
- Known issue in `experiments.py` lines 53, 110
- Should be replaced with `datetime.now(datetime.UTC)` in production

**CORS errors in frontend:**
- Backend CORS configured for `http://localhost:5174` (Vite default)
- If using different port, update `backend/app/config.py` CORS_ORIGINS

## Development Workflow

1. **Feature Development (TDD):**
   - Write failing test first
   - Implement minimal code to pass
   - Refactor if needed
   - Commit with descriptive message

2. **Commit Message Format:**
   - `feat(scope): description` - New feature
   - `fix(scope): description` - Bug fix
   - `docs: description` - Documentation
   - Examples: `feat(p2-task4): add experiment API endpoints with TDD`

3. **Code Review Checklist:**
   - All tests passing with `PYTHONPATH=. pytest tests/ -v`
   - No deprecation warnings (except known datetime.utcnow)
   - API endpoints return consistent response format: `{"success": bool, "data": ...}`
   - Error handling with HTTPException
   - Pydantic models for request/response validation

## Implementation Plans

Detailed implementation plans are in `docs/plans/`:
- `2026-03-04-amazon-listing-mvp-implementation.md` - P0 phase plan
- `2026-03-04-p1-data-pipeline-implementation.md` - P1 phase plan
- `2026-03-04-p1-api-frontend-implementation.md` - P1 API/frontend plan
- `2026-03-04-p2-experiment-implementation.md` - P2 phase plan

These plans follow TDD structure: Write test → Run (fail) → Implement → Run (pass) → Commit

## Production Considerations

**Not Yet Implemented:**
- Database connection (currently in-memory storage)
- Redis integration
- Celery task queue
- Authentication/authorization
- Rate limiting
- Logging configuration
- Environment-based configuration
- Database migrations runner (Alembic)

**When Implementing Database:**
- Replace in-memory stores (e.g., `_lifecycle_store`) with database queries
- Use SQLAlchemy or asyncpg for PostgreSQL
- Apply migration files in `backend/migrations/`
- Update service layer to use database repositories
