# Daily Starter - Software Test Procedure (STP)

## Test Layers

| Layer | Framework | Language | Location |
|-------|-----------|----------|----------|
| Backend API | pytest + httpx | Python | `tests/` |
| Frontend Widget | Flutter test | Dart | `frontend/test/` |
| E2E (Browser) | pytest + Playwright | Python | `tests/` |

## Marker Convention

Every test is tagged with `@pytest.mark.<fr_id>` where `<fr_id>` maps to a functional requirement in the SRS.

Run a specific requirement's tests:

```bash
docker compose --profile test run --rm test-e2e pytest -m fr12 -v
```

## Test File Mapping

| File | SRS Requirements | Coverage Area |
|------|------------------|---------------|
| `test_matchup_generation.py` | FR-1, FR-2, FR-5, FR-6, FR-9 | Daily matchup generation and Pokemon metadata |
| `test_daily_challenge.py` | FR-8, FR-9, FR-10, FR-11, FR-28 | Daily challenge display and completion state |
| `test_voting.py` | FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18 | Vote submission and validation |
| `test_identity.py` | FR-19, FR-20, FR-21, FR-22 | Anonymous voter token identity |
| `test_results.py` | FR-23, FR-24, FR-25, FR-26, FR-27, FR-28 | Results display after voting |
| `test_history.py` | FR-33, FR-34, FR-35 | Historical matchup retrieval |

## Test Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `base_url` | session | Frontend app URL |
| `api_url` | session | Backend API URL |
| `browser` | session | Playwright Chromium instance |
| `clean_page` | function | Fresh browser context with no cookies |
| `seeded_page` | function | Browser context with existing voter token + completed vote |
