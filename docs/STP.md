# Software Test Plan (STP)
## Favorite Pokemon Ranking Application

Version: 1.0
Date: 2026-03-04

---

# 1. Introduction

## 1.1 Purpose

This document defines the test strategy, test cases, and test infrastructure for the Favorite Pokemon Ranking Application. The project follows **Test-Driven Development (TDD)** methodology: tests are written before implementation code.

## 1.2 Scope

Testing is divided into two layers:

- **Unit and Component Tests** -- Vitest + React Testing Library (JavaScript, runs in Node)
- **End-to-End Tests** -- pytest + Playwright (Python, runs a real browser against the app)

Both layers run inside Docker containers.

## 1.3 References

- [SRS](SRS.md) -- Software Requirements Specification (FR-1 through FR-25)
- [PLAN](PLAN.md) -- Implementation Plan

## 1.4 TDD Workflow

For every feature, the development cycle is:

1. **Red** -- Write a failing test (pytest E2E or Vitest unit test)
2. **Green** -- Write the minimum code to make the test pass
3. **Refactor** -- Clean up while keeping tests green

---

# 2. Test Environment

## 2.1 Test Infrastructure in Docker

### Directory Structure

```
tests/
  e2e/
    conftest.py               # Shared pytest fixtures
    test_home_page.py         # Home screen tests (FR-1 to FR-4)
    test_phase_a.py           # Discovery phase tests (FR-5 to FR-10)
    test_phase_b.py           # Pairwise ranking tests (FR-11 to FR-16)
    test_championship.py      # Championship tests (FR-17 to FR-21)
    test_persistence.py       # LocalStorage tests (FR-22 to FR-25)
    test_performance.py       # Non-functional: performance
    test_responsive.py        # Non-functional: compatibility
  requirements.txt            # Python dependencies
  pytest.ini                  # pytest configuration
src/
  utils/__tests__/
    elo.test.js               # Elo algorithm unit tests
    ranking.test.js           # Discovery scoring unit tests
    storage.test.js           # LocalStorage helper unit tests
    generations.test.js       # Generation data unit tests
  components/__tests__/
    PokemonCard.test.jsx      # PokemonCard component tests
    GenerationCard.test.jsx   # GenerationCard component tests
    TopList.test.jsx          # TopList component tests
    ProgressBar.test.jsx      # ProgressBar component tests
  hooks/__tests__/
    useLocalStorage.test.js   # useLocalStorage hook tests
    usePokemon.test.js        # usePokemon hook tests
```

### Python Dependencies (`tests/requirements.txt`)

```
pytest>=8.0
pytest-playwright>=0.5
playwright>=1.49
pytest-html>=4.0
pytest-xdist>=3.5
```

### pytest Configuration (`tests/pytest.ini`)

```ini
[pytest]
testpaths = e2e
markers =
    smoke: Quick sanity checks
    fr1: FR-1 Display available generations
    fr2: FR-2 Start ranking a generation
    fr3: FR-3 Display completion status
    fr4: FR-4 Resume incomplete sessions
    fr5: FR-5 Display four Pokemon
    fr6: FR-6 Select preferred Pokemon
    fr7: FR-7 Record selection
    fr8: FR-8 Repeat selections
    fr9: FR-9 Assign scores
    fr10: FR-10 Create candidate pool
    fr11: FR-11 Present two Pokemon
    fr12: FR-12 Select preferred (pairwise)
    fr13: FR-13 Update Elo ratings
    fr14: FR-14 Repeat until stability
    fr15: FR-15 Generate Top 10
    fr16: FR-16 Mark generation completed
    fr17: FR-17 Collect Top 10 from each gen
    fr18: FR-18 Create global candidate pool
    fr19: FR-19 Run global pairwise comparisons
    fr20: FR-20 Generate global Top 10
    fr21: FR-21 Display final ranking
    fr22: FR-22 Store progress in LocalStorage
    fr23: FR-23 Auto-save after each selection
    fr24: FR-24 Restore progress on return
    fr25: FR-25 Reset stored progress
    nfr_perf: Non-functional performance tests
    nfr_compat: Non-functional compatibility tests
```

### Docker Compose Services

```yaml
services:
  app:
    build:
      context: .
      target: dev
    ports:
      - "5173:5173"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development

  test-unit:
    build:
      context: .
      target: dev
    volumes:
      - .:/app
      - /app/node_modules
    command: npx vitest run
    profiles: ["test"]

  test-e2e:
    build:
      context: ./tests
      dockerfile: Dockerfile.e2e
    depends_on:
      - app
    environment:
      - BASE_URL=http://app:5173
    volumes:
      - ./tests:/tests
      - ./test-results:/test-results
    profiles: ["test"]
```

### E2E Test Dockerfile (`tests/Dockerfile.e2e`)

```dockerfile
FROM python:3.12-slim
WORKDIR /tests
COPY requirements.txt .
RUN pip install -r requirements.txt && playwright install --with-deps chromium
COPY . .
CMD ["pytest", "--html=/test-results/report.html", "-v"]
```

### Running Tests

```bash
# Unit tests (Vitest)
docker compose --profile test run --rm test-unit

# E2E tests (pytest + Playwright)
docker compose --profile test run --rm test-e2e

# Single marker
docker compose --profile test run --rm test-e2e pytest -m fr1 -v

# Smoke tests only
docker compose --profile test run --rm test-e2e pytest -m smoke -v
```

---

# 3. Shared Fixtures (`tests/e2e/conftest.py`)

```python
import pytest
from playwright.sync_api import Page, Browser


@pytest.fixture(scope="session")
def base_url():
    return "http://app:5173"


@pytest.fixture
def page(browser: Browser, base_url: str):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def clean_page(page: Page, base_url: str):
    """Page with cleared LocalStorage."""
    page.goto(base_url)
    page.evaluate("window.localStorage.clear()")
    page.reload()
    return page


@pytest.fixture
def seeded_page(page: Page, base_url: str):
    """Page with pre-seeded LocalStorage (Gen 1 completed)."""
    page.goto(base_url)
    page.evaluate("""
        window.localStorage.setItem('favpoke_v1', JSON.stringify({
            gens: {
                "1": {
                    status: "completed",
                    top10: [
                        { id: 25, name: "pikachu", rating: 1620 },
                        { id: 6, name: "charizard", rating: 1590 },
                        { id: 150, name: "mewtwo", rating: 1570 },
                        { id: 131, name: "lapras", rating: 1550 },
                        { id: 143, name: "snorlax", rating: 1530 },
                        { id: 9, name: "blastoise", rating: 1510 },
                        { id: 3, name: "venusaur", rating: 1495 },
                        { id: 130, name: "gyarados", rating: 1480 },
                        { id: 149, name: "dragonite", rating: 1470 },
                        { id: 94, name: "gengar", rating: 1460 }
                    ]
                }
            },
            global: { status: "not_started", top10: null }
        }))
    """)
    page.reload()
    return page
```

---

# 4. Test Cases -- Unit Tests (Vitest)

## 4.1 Elo Algorithm (`src/utils/__tests__/elo.test.js`)

| ID | Test Name | Description |
|----|-----------|-------------|
| UT-ELO-01 | calculates expected score | Given two ratings, expected score follows the Elo formula |
| UT-ELO-02 | winner gains rating | Winner's new rating > old rating |
| UT-ELO-03 | loser loses rating | Loser's new rating < old rating |
| UT-ELO-04 | zero-sum updates | Winner's gain equals loser's loss |
| UT-ELO-05 | upset produces larger swing | Lower-rated winner gains more than higher-rated winner |
| UT-ELO-06 | equal ratings produce equal expected scores | Two players at 1500 each get 0.5 expected |
| UT-ELO-07 | K-factor controls magnitude | Higher K produces larger rating changes |

## 4.2 Ranking / Discovery (`src/utils/__tests__/ranking.test.js`)

| ID | Test Name | Description |
|----|-----------|-------------|
| UT-RNK-01 | groups Pokemon into sets of 4 | Given 12 IDs, produces 3 groups of 4 |
| UT-RNK-02 | handles remainder group | Given 14 IDs, last group has 2 |
| UT-RNK-03 | shuffles Pokemon | Two calls produce different orderings (probabilistic) |
| UT-RNK-04 | increments score on selection | Selecting a Pokemon increases its score by 1 |
| UT-RNK-05 | builds candidate pool from top scores | Top N scorers are selected for the pool |
| UT-RNK-06 | candidate pool size scales with gen | Smaller gens produce smaller pools (min 20) |
| UT-RNK-07 | candidate pool capped at 30 | Even for large gens, pool does not exceed 30 |
| UT-RNK-08 | matchmaking pairs similar ratings | Next pair has the smallest rating gap among least-compared |
| UT-RNK-09 | stability detection triggers | Returns true when avg change < threshold over last N rounds |
| UT-RNK-10 | max comparisons enforced | Stops after candidatePoolSize * 5 comparisons |
| UT-RNK-11 | extracts Top 10 from ratings | Sorted descending, returns exactly 10 |

## 4.3 Storage Helpers (`src/utils/__tests__/storage.test.js`)

| ID | Test Name | Description |
|----|-----------|-------------|
| UT-STR-01 | initializes empty state | Returns default structure when no data exists |
| UT-STR-02 | saves and loads state | Round-trip write then read matches |
| UT-STR-03 | updates generation status | Sets gen status without corrupting other data |
| UT-STR-04 | resets all progress | After reset, state matches initial default |
| UT-STR-05 | handles corrupted data | Returns default state if JSON is invalid |
| UT-STR-06 | stores Top 10 for generation | Saves Top 10 array under the correct gen key |

## 4.4 Generation Data (`src/utils/__tests__/generations.test.js`)

| ID | Test Name | Description |
|----|-----------|-------------|
| UT-GEN-01 | contains 9 generations | Array length is 9 |
| UT-GEN-02 | Gen 1 range is 1-151 | startId=1, endId=151 |
| UT-GEN-03 | no ID gaps between gens | Gen N endId + 1 = Gen N+1 startId |
| UT-GEN-04 | each gen has required fields | id, name, startId, endId all present |
| UT-GEN-05 | Pokemon count per gen | endId - startId + 1 matches expected count |

## 4.5 Component Tests (Vitest + React Testing Library)

### PokemonCard (`src/components/__tests__/PokemonCard.test.jsx`)

| ID | Test Name | Description |
|----|-----------|-------------|
| CT-PC-01 | renders name and sprite | Displays Pokemon name and img with correct src |
| CT-PC-02 | calls onClick when clicked | Click handler fires with Pokemon ID |
| CT-PC-03 | shows loading state | Displays placeholder while image loads |

### GenerationCard (`src/components/__tests__/GenerationCard.test.jsx`)

| ID | Test Name | Description |
|----|-----------|-------------|
| CT-GC-01 | renders generation name | Displays "Gen 1 - Kanto" |
| CT-GC-02 | shows not started status | Badge shows "Not Started" |
| CT-GC-03 | shows in progress status | Badge shows "In Progress" |
| CT-GC-04 | shows completed status | Badge shows "Completed" |
| CT-GC-05 | click navigates to ranking | onClick fires with gen ID |

### TopList (`src/components/__tests__/TopList.test.jsx`)

| ID | Test Name | Description |
|----|-----------|-------------|
| CT-TL-01 | renders 10 ranked items | Shows ranks 1 through 10 |
| CT-TL-02 | displays names and sprites | Each item shows Pokemon name and image |
| CT-TL-03 | items ordered by rank | First item has highest rating |

### ProgressBar (`src/components/__tests__/ProgressBar.test.jsx`)

| ID | Test Name | Description |
|----|-----------|-------------|
| CT-PB-01 | renders at 0% | Bar width is 0% initially |
| CT-PB-02 | renders at 50% | Bar width matches 50% |
| CT-PB-03 | renders at 100% | Bar is fully filled |

## 4.6 Hook Tests (Vitest + React Testing Library)

### useLocalStorage (`src/hooks/__tests__/useLocalStorage.test.js`)

| ID | Test Name | Description |
|----|-----------|-------------|
| HT-LS-01 | returns initial state | When empty, returns default structure |
| HT-LS-02 | persists state update | After setState, localStorage contains new value |
| HT-LS-03 | restores on remount | Unmount and remount reads saved value |
| HT-LS-04 | reset clears storage | After reset, returns to default |

### usePokemon (`src/hooks/__tests__/usePokemon.test.js`)

| ID | Test Name | Description |
|----|-----------|-------------|
| HT-PK-01 | fetches Pokemon by ID | Returns name and sprite URL |
| HT-PK-02 | caches fetched data | Second call does not trigger network request |
| HT-PK-03 | handles fetch error | Returns error state on network failure |
| HT-PK-04 | fetches batch of Pokemon | Multiple IDs resolved concurrently |

---

# 5. Test Cases -- E2E Tests (pytest + Playwright)

## 5.1 Home Page (`tests/e2e/test_home_page.py`)

```python
import pytest

@pytest.mark.smoke
@pytest.mark.fr1
class TestGenerationDisplay:
    def test_displays_all_nine_generations(self, clean_page):
        """FR-1: All 9 generation cards are visible on the home screen."""

    def test_each_gen_shows_name_and_region(self, clean_page):
        """FR-1: Each card displays generation number and region name."""

@pytest.mark.fr2
class TestStartRanking:
    def test_clicking_gen_navigates_to_ranking(self, clean_page):
        """FR-2: Clicking a generation card navigates to /rank/:genId."""

    def test_start_ranking_initializes_state(self, clean_page):
        """FR-2: Starting a generation creates an in_progress entry in storage."""

@pytest.mark.fr3
class TestCompletionStatus:
    def test_not_started_badge_by_default(self, clean_page):
        """FR-3: Unranked generations show 'Not Started' badge."""

    def test_in_progress_badge(self, seeded_page):
        """FR-3: Partially ranked generations show 'In Progress' badge."""

    def test_completed_badge(self, seeded_page):
        """FR-3: Fully ranked generations show 'Completed' badge."""

@pytest.mark.fr4
class TestResumeSession:
    def test_resume_incomplete_ranking(self, seeded_page):
        """FR-4: Clicking an in-progress generation resumes from saved state."""
```

## 5.2 Phase A -- Discovery (`tests/e2e/test_phase_a.py`)

```python
import pytest

@pytest.mark.fr5
class TestDiscoveryDisplay:
    def test_shows_four_pokemon(self, clean_page):
        """FR-5: Ranking screen displays exactly 4 Pokemon cards."""

    def test_pokemon_have_sprites_and_names(self, clean_page):
        """FR-5: Each of the 4 cards shows a sprite image and a name."""

@pytest.mark.fr6
@pytest.mark.fr7
class TestDiscoverySelection:
    def test_clicking_pokemon_selects_it(self, clean_page):
        """FR-6/FR-7: Clicking a Pokemon card records the selection and advances."""

    def test_only_one_selectable_per_group(self, clean_page):
        """FR-6: After selecting one, the group advances (no double pick)."""

@pytest.mark.fr8
class TestDiscoveryRepetition:
    def test_new_group_after_selection(self, clean_page):
        """FR-8: After selecting, a new group of 4 Pokemon appears."""

    def test_progress_bar_advances(self, clean_page):
        """FR-8: Progress bar increases after each selection."""

@pytest.mark.fr9
@pytest.mark.fr10
class TestCandidatePoolCreation:
    def test_transitions_to_phase_b(self, clean_page):
        """FR-9/FR-10: After all groups shown, transitions to pairwise phase."""

    def test_candidate_pool_stored(self, clean_page):
        """FR-10: LocalStorage contains candidatePool after Phase A completes."""
```

## 5.3 Phase B -- Pairwise Ranking (`tests/e2e/test_phase_b.py`)

```python
import pytest

@pytest.mark.fr11
class TestPairwiseDisplay:
    def test_shows_two_pokemon(self, clean_page):
        """FR-11: Pairwise screen displays exactly 2 Pokemon cards."""

    def test_both_have_sprites_and_names(self, clean_page):
        """FR-11: Both cards show sprite and name."""

@pytest.mark.fr12
class TestPairwiseSelection:
    def test_clicking_selects_winner(self, clean_page):
        """FR-12: Clicking a Pokemon picks it as the winner."""

@pytest.mark.fr13
class TestEloUpdate:
    def test_ratings_change_after_selection(self, clean_page):
        """FR-13: After selection, ratings in LocalStorage are updated."""

@pytest.mark.fr14
class TestStabilityDetection:
    def test_ranking_eventually_ends(self, clean_page):
        """FR-14: Phase B terminates after stability or max comparisons."""

@pytest.mark.fr15
class TestTopTenGeneration:
    def test_produces_top_10(self, clean_page):
        """FR-15: After Phase B, result screen shows exactly 10 ranked Pokemon."""

    def test_top_10_ordered_by_rating(self, clean_page):
        """FR-15: Pokemon are ordered from highest to lowest rating."""

@pytest.mark.fr16
class TestGenerationCompletion:
    def test_generation_marked_completed(self, clean_page):
        """FR-16: After Phase B, generation status is 'completed' in storage."""

    def test_home_shows_completed_badge(self, clean_page):
        """FR-16: Returning to home shows 'Completed' badge for that gen."""
```

## 5.4 Championship (`tests/e2e/test_championship.py`)

```python
import pytest

@pytest.fixture
def all_gens_completed_page(page, base_url):
    """Page with all 9 generations completed (mocked Top 10s)."""
    # Seeds LocalStorage with 9 completed generations
    ...

@pytest.mark.fr17
class TestChampionshipCollection:
    def test_championship_button_visible_when_all_complete(self, all_gens_completed_page):
        """FR-17: 'Start Championship' button appears when all 9 gens are done."""

    def test_championship_button_hidden_when_incomplete(self, seeded_page):
        """FR-17: Button is not visible when some gens are not completed."""

@pytest.mark.fr18
class TestGlobalPool:
    def test_championship_starts_pairwise(self, all_gens_completed_page):
        """FR-18: Clicking championship starts pairwise comparisons."""

@pytest.mark.fr19
class TestGlobalPairwise:
    def test_shows_two_pokemon_from_different_gens(self, all_gens_completed_page):
        """FR-19: Pairwise screen shows Pokemon that may be from different gens."""

@pytest.mark.fr20
class TestGlobalTopTen:
    def test_produces_global_top_10(self, all_gens_completed_page):
        """FR-20: Championship result shows 10 ranked Pokemon."""

@pytest.mark.fr21
class TestFinalRanking:
    def test_displays_final_ranking_screen(self, all_gens_completed_page):
        """FR-21: Final result screen shows names, sprites, and ranks."""

    def test_ranking_summary_present(self, all_gens_completed_page):
        """FR-21: A ranking summary section is visible."""
```

## 5.5 Persistence (`tests/e2e/test_persistence.py`)

```python
import pytest

@pytest.mark.fr22
class TestLocalStorageUsage:
    def test_data_stored_under_correct_key(self, clean_page):
        """FR-22: Data is stored under 'favpoke_v1' key in LocalStorage."""

@pytest.mark.fr23
class TestAutoSave:
    def test_save_after_discovery_selection(self, clean_page):
        """FR-23: LocalStorage updates immediately after picking a Pokemon in Phase A."""

    def test_save_after_pairwise_selection(self, clean_page):
        """FR-23: LocalStorage updates immediately after picking in Phase B."""

@pytest.mark.fr24
class TestRestoreProgress:
    def test_reload_restores_discovery_progress(self, clean_page):
        """FR-24: After page reload during Phase A, user resumes at correct group."""

    def test_reload_restores_pairwise_progress(self, clean_page):
        """FR-24: After page reload during Phase B, user resumes with correct ratings."""

@pytest.mark.fr25
class TestResetProgress:
    def test_reset_clears_all_data(self, seeded_page):
        """FR-25: Reset button clears LocalStorage and returns to initial state."""

    def test_reset_requires_confirmation(self, seeded_page):
        """FR-25: Reset shows a confirmation dialog before clearing."""
```

## 5.6 Non-Functional: Performance (`tests/e2e/test_performance.py`)

```python
import pytest

@pytest.mark.nfr_perf
class TestPerformance:
    def test_app_loads_under_2_seconds(self, page, base_url):
        """NFR: Application startup completes within 2 seconds."""

    def test_sprites_load_under_1_second(self, clean_page):
        """NFR: Pokemon sprite images load within 1 second."""

    def test_selection_updates_instantly(self, clean_page):
        """NFR: UI updates within 100ms of a selection click."""
```

## 5.7 Non-Functional: Compatibility (`tests/e2e/test_responsive.py`)

```python
import pytest

VIEWPORTS = [
    {"width": 375, "height": 812, "name": "mobile"},
    {"width": 768, "height": 1024, "name": "tablet"},
    {"width": 1440, "height": 900, "name": "desktop"},
]

@pytest.mark.nfr_compat
class TestResponsive:
    @pytest.mark.parametrize("viewport", VIEWPORTS, ids=lambda v: v["name"])
    def test_home_page_renders_correctly(self, browser, base_url, viewport):
        """NFR: Home page is usable at mobile, tablet, and desktop widths."""

    @pytest.mark.parametrize("viewport", VIEWPORTS, ids=lambda v: v["name"])
    def test_ranking_screen_renders_correctly(self, browser, base_url, viewport):
        """NFR: Ranking screen cards are visible and clickable at all viewports."""
```

---

# 6. Requirements Traceability Matrix

| SRS Requirement | Unit Tests | Component Tests | E2E Tests |
|-----------------|-----------|-----------------|-----------|
| FR-1 Display generations | UT-GEN-01..05 | CT-GC-01 | test_home_page::TestGenerationDisplay |
| FR-2 Start ranking | -- | CT-GC-05 | test_home_page::TestStartRanking |
| FR-3 Completion status | -- | CT-GC-02..04 | test_home_page::TestCompletionStatus |
| FR-4 Resume sessions | UT-STR-02, HT-LS-03 | -- | test_home_page::TestResumeSession |
| FR-5 Display four Pokemon | -- | CT-PC-01 | test_phase_a::TestDiscoveryDisplay |
| FR-6 Select preferred | -- | CT-PC-02 | test_phase_a::TestDiscoverySelection |
| FR-7 Record selection | UT-RNK-04 | -- | test_phase_a::TestDiscoverySelection |
| FR-8 Repeat selections | UT-RNK-01..03 | CT-PB-01..03 | test_phase_a::TestDiscoveryRepetition |
| FR-9 Assign scores | UT-RNK-04..05 | -- | test_phase_a::TestCandidatePoolCreation |
| FR-10 Create candidate pool | UT-RNK-05..07 | -- | test_phase_a::TestCandidatePoolCreation |
| FR-11 Present two Pokemon | -- | CT-PC-01 | test_phase_b::TestPairwiseDisplay |
| FR-12 Select preferred (pairwise) | -- | CT-PC-02 | test_phase_b::TestPairwiseSelection |
| FR-13 Update Elo ratings | UT-ELO-01..07 | -- | test_phase_b::TestEloUpdate |
| FR-14 Repeat until stability | UT-RNK-09..10 | -- | test_phase_b::TestStabilityDetection |
| FR-15 Generate Top 10 | UT-RNK-11 | CT-TL-01..03 | test_phase_b::TestTopTenGeneration |
| FR-16 Mark gen completed | UT-STR-03 | -- | test_phase_b::TestGenerationCompletion |
| FR-17 Collect Top 10 per gen | UT-STR-06 | -- | test_championship::TestChampionshipCollection |
| FR-18 Create global pool | -- | -- | test_championship::TestGlobalPool |
| FR-19 Run global pairwise | UT-ELO-01..07 | -- | test_championship::TestGlobalPairwise |
| FR-20 Generate global Top 10 | UT-RNK-11 | CT-TL-01..03 | test_championship::TestGlobalTopTen |
| FR-21 Display final ranking | -- | CT-TL-01..03 | test_championship::TestFinalRanking |
| FR-22 Store in LocalStorage | UT-STR-01..02 | -- | test_persistence::TestLocalStorageUsage |
| FR-23 Auto-save | UT-STR-03, HT-LS-02 | -- | test_persistence::TestAutoSave |
| FR-24 Restore progress | UT-STR-02, HT-LS-03 | -- | test_persistence::TestRestoreProgress |
| FR-25 Reset progress | UT-STR-04, HT-LS-04 | -- | test_persistence::TestResetProgress |
| NFR Performance | -- | -- | test_performance::TestPerformance |
| NFR Compatibility | -- | -- | test_responsive::TestResponsive |

---

# 7. Test Execution Strategy

## 7.1 TDD Phase Order

Tests and features should be built in this sequence:

1. **Utility unit tests first** -- Elo, ranking, storage, generations (pure logic, no UI)
2. **Hook tests** -- useLocalStorage, usePokemon (data layer)
3. **Component tests** -- PokemonCard, GenerationCard, TopList, ProgressBar (UI atoms)
4. **E2E Home Page** -- FR-1 through FR-4
5. **E2E Phase A** -- FR-5 through FR-10
6. **E2E Phase B** -- FR-11 through FR-16
7. **E2E Persistence** -- FR-22 through FR-25
8. **E2E Championship** -- FR-17 through FR-21
9. **E2E Non-functional** -- Performance and compatibility

## 7.2 Continuous Testing Commands

```bash
# Watch mode during development (unit tests)
docker compose --profile test run --rm test-unit npx vitest

# Run all tests
docker compose --profile test run --rm test-unit
docker compose --profile test run --rm test-e2e

# Run by SRS requirement
docker compose --profile test run --rm test-e2e pytest -m fr5 -v

# Run smoke tests
docker compose --profile test run --rm test-e2e pytest -m smoke -v

# Generate HTML report
docker compose --profile test run --rm test-e2e pytest --html=/test-results/report.html
```

## 7.3 Pass/Fail Criteria

- **Unit tests**: 100% pass rate required before merging
- **Component tests**: 100% pass rate required before merging
- **E2E tests**: 100% pass rate for smoke-marked tests; full suite must pass before release
- **Performance tests**: Thresholds as defined in SRS Section 6 (startup < 2s, images < 1s)
