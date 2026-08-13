import re

import httpx
import pytest


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.history
@pytest.mark.fr34
class TestHistoryNavigationE2E:
    """FR-34: Browser-based navigation to history screen."""

    def test_navigate_to_history_screen(self, clean_page, base_url):
        """FR-34: Clicking the history button navigates to the history screen."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)

        clean_page.goto(f"{base_url}/#/history")
        clean_page.wait_for_selector("text=History", timeout=15000)

        heading = clean_page.query_selector("text=History")
        assert heading is not None, "History screen heading should be visible"

    def test_history_screen_has_back_navigation(self, clean_page, base_url):
        """FR-34: The history screen provides a way to navigate back."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)

        clean_page.goto(f"{base_url}/#/history")
        clean_page.wait_for_selector("text=History", timeout=15000)

        clean_page.go_back()
        clean_page.wait_for_selector("text=PokePick", timeout=15000)

        title = clean_page.query_selector("text=PokePick")
        assert title is not None, "Should navigate back to the daily challenge screen"


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.history
@pytest.mark.fr33
@pytest.mark.fr35
class TestHistoryDisplayE2E:
    """FR-33/FR-35: Historical matchups displayed in the browser."""

    def test_history_shows_entries_or_empty_state(self, clean_page, base_url, api_url):
        """FR-33: History screen shows past matchups or an empty state message."""
        httpx.get(f"{api_url}/api/matchup/today")

        clean_page.goto(f"{base_url}/#/history")
        clean_page.wait_for_selector("text=History", timeout=15000)
        clean_page.wait_for_timeout(3000)

        content = clean_page.content()
        has_entries = re.search(r"\d+ votes?", content) is not None
        has_empty = "No history yet" in content

        assert has_entries or has_empty, (
            "History should show either past matchup entries or 'No history yet'"
        )

    def test_history_entries_show_pokemon_sprites(self, seeded_page, base_url):
        """FR-35: History entries display Pokemon sprite images."""
        seeded_page.goto(f"{base_url}/#/history")
        seeded_page.wait_for_selector("text=History", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        content = seeded_page.content()
        if "No history yet" not in content:
            images = seeded_page.query_selector_all("img")
            assert len(images) >= 3, "History entries should show Pokemon sprite images"

    def test_history_entries_show_dates(self, seeded_page, base_url):
        """FR-33: History entries display the matchup date in readable format."""
        seeded_page.goto(f"{base_url}/#/history")
        seeded_page.wait_for_selector("text=History", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        content = seeded_page.content()
        if "No history yet" not in content:
            has_readable_date = (
                "Today" in content
                or "Yesterday" in content
                or re.search(r"[A-Z][a-z]{2} \d{1,2}, \d{4}", content)
            )
            assert has_readable_date, (
                "History entries should display dates in readable format"
            )

    def test_history_entries_show_vote_counts(self, seeded_page, base_url):
        """FR-35: History entries display vote count information."""
        seeded_page.goto(f"{base_url}/#/history")
        seeded_page.wait_for_selector("text=History", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        content = seeded_page.content()
        if "No history yet" not in content:
            assert re.search(r"\d+ votes?", content), (
                "History entries should show vote counts"
            )


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.history
@pytest.mark.fr33
@pytest.mark.fr34
@pytest.mark.fr35
class TestHistory:
    """FR-33 to FR-35: Historical matchup retrieval."""

    def test_history_returns_list(self, api_url):
        """FR-34: The system allows retrieval of previous matchups."""
        httpx.get(f"{api_url}/api/matchup/today")

        resp = httpx.get(f"{api_url}/api/history")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_history_entries_have_required_fields(self, api_url):
        """FR-33/FR-35: History entries contain matchup data and winner info."""
        httpx.get(f"{api_url}/api/matchup/today")

        resp = httpx.get(f"{api_url}/api/history")
        data = resp.json()

        if len(data) > 0:
            entry = data[0]
            assert "id" in entry
            assert "match_date" in entry
            assert "pokemon" in entry
            assert len(entry["pokemon"]) == 3
            assert "total_votes" in entry
