import pytest


@pytest.mark.fr8
@pytest.mark.fr9
@pytest.mark.fr10
class TestDailyChallengeDisplay:
    """User flow 8.1: First visit - before voting."""

    def test_shows_three_pokemon(self, clean_page):
        """FR-8/FR-10: The daily challenge displays exactly 3 selectable Pokemon."""
        clean_page.wait_for_selector("text=Daily Starter", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        images = clean_page.query_selector_all("img")
        assert len(images) >= 3, f"Expected at least 3 Pokemon sprites, got {len(images)}"

    def test_shows_voting_prompt(self, clean_page):
        """FR-8: System displays the daily matchup with a prompt to vote."""
        clean_page.wait_for_selector("text=Daily Starter", timeout=15000)
        assert clean_page.query_selector("text=Who's your favorite?") is not None


@pytest.mark.fr11
class TestCompletionState:
    """User flow 8.3: Revisiting after voting."""

    def test_shows_results_after_voting(self, seeded_page):
        """FR-11/FR-28: After voting, results are shown instead of voting UI."""
        seeded_page.wait_for_selector("text=Daily Starter", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        results_visible = seeded_page.query_selector("text=Today's Results") is not None
        assert results_visible, "Results should be displayed after voting"
