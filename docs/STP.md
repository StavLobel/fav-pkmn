# Daily Starter - Software Test Procedure (STP)

## Test Layers

| Layer | Framework | Language | Location |
|-------|-----------|----------|----------|
| Backend API | pytest + httpx | Python | `tests/` |
| Frontend Widget | Flutter test | Dart | `frontend/test/` |
| E2E (Browser) | pytest + Playwright | Python | `tests/` |

## Marker Convention

Every test is tagged with `@pytest.mark.<fr_id>` where `<fr_id>` maps to a functional requirement in the SRS.

Additionally, tests carry **suite**, **type**, and **feature** markers for targeted CI runs.

### Suite markers

| Marker | Purpose | Example usage |
|--------|---------|---------------|
| `sanity` | Minimal critical-path validation (< 30s) | `pytest -m sanity` |
| `regression` | Full functional test suite | `pytest -m regression` |
| `smoke` | Post-deploy connectivity checks | `pytest -m smoke` |

### Type markers

| Marker | Purpose | Example usage |
|--------|---------|---------------|
| `api` | httpx-based API tests (no browser) | `pytest -m api` |
| `e2e` | Playwright browser tests | `pytest -m e2e` |
| `security` | Cookie attributes, input validation | `pytest -m security` |

### Feature markers

| Marker | Feature area |
|--------|-------------|
| `matchup` | Matchup generation and metadata |
| `voting` | Vote submission, validation, duplicates |
| `identity` | Anonymous voter token and cookies |
| `results` | Results display after voting |
| `history` | Historical matchup retrieval |
| `daily_reset` | Daily challenge reset and new day unlock |

### Run examples

```bash
# Single SRS requirement
docker compose --profile test run --rm test-e2e pytest -m fr12 -v

# Quick sanity check
docker compose --profile test run --rm test-e2e pytest -m sanity -v

# All API tests (no browser)
docker compose --profile test run --rm test-e2e pytest -m api -v

# Security tests only
docker compose --profile test run --rm test-e2e pytest -m security -v

# Full regression minus E2E
docker compose --profile test run --rm test-e2e pytest -m "regression and not e2e" -v
```

## Test File Mapping

| File | SRS Requirements | Coverage Area |
|------|------------------|---------------|
| `test_matchup_generation.py` | FR-1, FR-2, FR-5, FR-6, FR-9 | Daily matchup generation and Pokemon metadata |
| `test_daily_challenge.py` | FR-8, FR-9, FR-10, FR-11, FR-28 | Daily challenge display and completion state |
| `test_voting.py` | FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-27 | Vote submission, validation, ties |
| `test_identity.py` | FR-19, FR-20, FR-21, FR-22, NFR-7, NFR-8 | Anonymous voter token identity and cookie security |
| `test_results.py` | FR-23, FR-24, FR-25, FR-26, FR-27, FR-28 | Results display after voting |
| `test_daily_reset.py` | FR-29, FR-30, FR-32 | Daily reset and re-participation |
| `test_history.py` | FR-33, FR-34, FR-35 | Historical matchup retrieval |
| `test_performance.py` | NFR-1, NFR-2 | Response time benchmarks |

## Test Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `base_url` | session | Frontend app URL |
| `api_url` | session | Backend API URL |
| `browser` | session | Playwright Chromium instance |
| `clean_page` | function | Fresh browser context with no cookies |
| `seeded_page` | function | Browser context with existing voter token + completed vote |

## Pytest Plugins

| Plugin | Purpose |
|--------|---------|
| faker | Generate realistic test data |
| pytest-ordering | Control test execution order |
| pytest-randomly | Randomize order to catch hidden dependencies |
| pytest-xdist | Parallel test execution (`pytest -n auto`) |
| pytest-cov | Code coverage reports |
| pytest-timeout | Auto-fail hanging tests (default 30s) |
| pytest-asyncio | Async test support |
| freezegun | Mock dates and times |
| respx | Mock httpx requests |
