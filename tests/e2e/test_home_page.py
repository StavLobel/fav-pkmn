import pytest


GEN_NAMES = [
    "Kanto", "Johto", "Hoenn", "Sinnoh",
    "Unova", "Kalos", "Alola", "Galar", "Paldea",
]


@pytest.mark.smoke
@pytest.mark.fr1
class TestGenerationDisplay:
    def test_displays_all_nine_generations(self, clean_page):
        """FR-1: All 9 generation cards are visible on the home screen."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        assert cards.count() == 9

    def test_each_gen_shows_name_and_region(self, clean_page):
        """FR-1: Each card displays generation number and region name."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)

        for i, name in enumerate(GEN_NAMES):
            card = cards.nth(i)
            text = card.inner_text()
            assert name in text, f"Expected '{name}' in card {i + 1}, got '{text}'"


@pytest.mark.fr2
class TestStartRanking:
    def test_clicking_gen_navigates_to_ranking(self, clean_page):
        """FR-2: Clicking a generation card navigates to /rank/:genId."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/1", timeout=5000)
        assert "/rank/1" in clean_page.url

    def test_start_ranking_initializes_state(self, clean_page):
        """FR-2: Starting a generation creates an in_progress entry in storage."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/1", timeout=5000)
        state = clean_page.evaluate(
            "JSON.parse(window.localStorage.getItem('favpoke_v1'))"
        )
        gen1 = state.get("gens", {}).get("1", {})
        assert gen1.get("status") == "in_progress"


@pytest.mark.fr3
class TestCompletionStatus:
    def test_not_started_badge_by_default(self, clean_page):
        """FR-3: Unranked generations show 'Not Started' badge."""
        badges = clean_page.locator('[data-testid="gen-status-badge"]')
        badges.first.wait_for(state="visible", timeout=10000)

        for i in range(badges.count()):
            text = badges.nth(i).inner_text().lower()
            assert "not started" in text

    def test_completed_badge(self, seeded_page):
        """FR-3: Fully ranked generations show 'Completed' badge."""
        badges = seeded_page.locator('[data-testid="gen-status-badge"]')
        badges.first.wait_for(state="visible", timeout=10000)

        first_badge = badges.first.inner_text().lower()
        assert "completed" in first_badge

    def test_in_progress_badge(self, page, base_url):
        """FR-3: Partially ranked generations show 'In Progress' badge."""
        page.goto(base_url)
        page.evaluate("""
            window.localStorage.setItem('favpoke_v1', JSON.stringify({
                gens: {
                    "2": { status: "in_progress" }
                },
                global: { status: "not_started", top10: null }
            }))
        """)
        page.reload()

        badges = page.locator('[data-testid="gen-status-badge"]')
        badges.first.wait_for(state="visible", timeout=10000)

        second_badge = badges.nth(1).inner_text().lower()
        assert "in progress" in second_badge


@pytest.mark.fr4
class TestResumeSession:
    def test_resume_incomplete_ranking(self, page, base_url):
        """FR-4: Clicking an in-progress generation resumes from saved state."""
        page.goto(base_url)
        page.evaluate("""
            window.localStorage.setItem('favpoke_v1', JSON.stringify({
                gens: {
                    "1": {
                        status: "in_progress",
                        currentGroup: 5,
                        scores: {}
                    }
                },
                global: { status: "not_started", top10: null }
            }))
        """)
        page.reload()

        cards = page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        page.wait_for_url("**/rank/1", timeout=5000)
        assert "/rank/1" in page.url

        pokemon_cards = page.locator('[data-testid="pokemon-card"]')
        pokemon_cards.first.wait_for(state="visible", timeout=10000)
        assert pokemon_cards.count() >= 2
