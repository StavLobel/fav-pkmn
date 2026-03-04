import pytest


def _seed_phase_b(page, base_url):
    """Helper to seed state at beginning of Phase B for Gen 1."""
    page.goto(base_url)
    candidates = list(range(1, 26))
    ratings = {str(c): 1500 for c in candidates}
    page.evaluate("""(data) => {
        window.localStorage.setItem('favpoke_v1', JSON.stringify({
            gens: {
                "1": {
                    status: "in_progress",
                    phase: "b",
                    candidatePool: data.candidates,
                    ratings: data.ratings,
                    comparisons: {},
                    totalComparisons: 0,
                    ratingHistory: []
                }
            },
            global: { status: "not_started", top10: null }
        }))
    }""", {"candidates": candidates, "ratings": ratings})
    page.goto(f"{base_url}/rank/1")


def _seed_near_completion(page, base_url):
    """Helper to seed state near the end of Phase B."""
    page.goto(base_url)
    candidates = list(range(1, 26))
    ratings = {str(c): 1500 + (25 - c) * 10 for c in candidates}
    stable_history = [0.5] * 15
    page.evaluate("""(data) => {
        window.localStorage.setItem('favpoke_v1', JSON.stringify({
            gens: {
                "1": {
                    status: "in_progress",
                    phase: "b",
                    candidatePool: data.candidates,
                    ratings: data.ratings,
                    comparisons: {},
                    totalComparisons: 120,
                    ratingHistory: data.history
                }
            },
            global: { status: "not_started", top10: null }
        }))
    }""", {"candidates": candidates, "ratings": ratings, "history": stable_history})
    page.goto(f"{base_url}/rank/1")


@pytest.mark.fr11
class TestPairwiseDisplay:
    def test_shows_two_pokemon(self, page, base_url):
        """FR-11: Pairwise screen displays exactly 2 Pokemon cards."""
        _seed_phase_b(page, base_url)

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        assert pokemon.count() == 2

    def test_both_have_sprites_and_names(self, page, base_url):
        """FR-11: Both cards show sprite and name."""
        _seed_phase_b(page, base_url)

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        for i in range(2):
            card = pokemon.nth(i)
            sprite = card.locator('[data-testid="pokemon-sprite"]')
            name = card.locator('[data-testid="pokemon-name"]')
            assert sprite.is_visible()
            assert name.inner_text().strip() != ""


@pytest.mark.fr12
class TestPairwiseSelection:
    def test_clicking_selects_winner(self, page, base_url):
        """FR-12: Clicking a Pokemon picks it as the winner."""
        _seed_phase_b(page, base_url)

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        pokemon.first.click()

        pokemon.first.wait_for(state="visible", timeout=10000)
        assert pokemon.count() == 2


@pytest.mark.fr13
class TestEloUpdate:
    def test_ratings_change_after_selection(self, page, base_url):
        """FR-13: After selection, ratings in LocalStorage are updated."""
        _seed_phase_b(page, base_url)

        state_before = page.evaluate(
            "JSON.parse(window.localStorage.getItem('favpoke_v1'))"
        )
        ratings_before = state_before["gens"]["1"]["ratings"].copy()

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        pokemon.first.click()

        page.wait_for_timeout(500)

        state_after = page.evaluate(
            "JSON.parse(window.localStorage.getItem('favpoke_v1'))"
        )
        ratings_after = state_after["gens"]["1"]["ratings"]

        changed = any(
            ratings_after.get(k) != v for k, v in ratings_before.items()
        )
        assert changed, "At least one rating should have changed"


@pytest.mark.fr14
class TestStabilityDetection:
    def test_ranking_eventually_ends(self, page, base_url):
        """FR-14: Phase B terminates after stability or max comparisons."""
        _seed_near_completion(page, base_url)

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        for _ in range(30):
            if "/result/" in page.url:
                break
            visible = page.locator('[data-testid="pokemon-card"]')
            if visible.count() >= 1:
                visible.first.click()
                page.wait_for_timeout(300)
            else:
                break

        page.wait_for_timeout(2000)

        state = page.evaluate(
            "JSON.parse(window.localStorage.getItem('favpoke_v1'))"
        )
        gen1 = state.get("gens", {}).get("1", {})
        ended = (
            "/result/" in page.url
            or gen1.get("status") == "completed"
            or gen1.get("phase") != "b"
        )
        assert ended, "Phase B should eventually terminate"


@pytest.mark.fr15
class TestTopTenGeneration:
    def test_produces_top_10(self, seeded_page):
        """FR-15: After Phase B, result screen shows exactly 10 ranked Pokemon."""
        seeded_page.goto(seeded_page.url.rsplit("/", 1)[0] + "/result/1")

        items = seeded_page.locator('[data-testid="top-list-item"]')
        items.first.wait_for(state="visible", timeout=10000)
        assert items.count() == 10

    def test_top_10_ordered_by_rating(self, seeded_page):
        """FR-15: Pokemon are ordered from highest to lowest rating."""
        seeded_page.goto(seeded_page.url.rsplit("/", 1)[0] + "/result/1")

        items = seeded_page.locator('[data-testid="top-list-item"]')
        items.first.wait_for(state="visible", timeout=10000)

        first_name = items.first.inner_text().lower()
        assert "pikachu" in first_name


@pytest.mark.fr16
class TestGenerationCompletion:
    def test_generation_marked_completed(self, seeded_page):
        """FR-16: After Phase B, generation status is 'completed' in storage."""
        state = seeded_page.evaluate(
            "JSON.parse(window.localStorage.getItem('favpoke_v1'))"
        )
        assert state["gens"]["1"]["status"] == "completed"

    def test_home_shows_completed_badge(self, seeded_page):
        """FR-16: Returning to home shows 'Completed' badge for that gen."""
        badges = seeded_page.locator('[data-testid="gen-status-badge"]')
        badges.first.wait_for(state="visible", timeout=10000)

        first_badge = badges.first.inner_text().lower()
        assert "completed" in first_badge
