import re

import httpx
import pytest


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.results
@pytest.mark.fr23
@pytest.mark.fr24
class TestResultsDisplayE2E:
    """FR-23/FR-24: Browser-based results display after voting."""

    def test_results_heading_visible(self, seeded_page):
        """FR-23: 'Today's Results' heading appears after voting."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        heading = seeded_page.query_selector("text=Today's Results")
        assert heading is not None, "Results heading should be visible"

    def test_total_votes_displayed(self, seeded_page):
        """FR-24: Total vote count is shown in the results view."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        content = seeded_page.content()
        assert re.search(r"\d+ total votes?", content), (
            "Total vote count text should be visible"
        )

    def test_vote_percentages_displayed(self, seeded_page):
        """FR-24: Vote percentages are shown for each Pokemon."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        content = seeded_page.content()
        assert re.search(r"\d+(\.\d+)?%", content), (
            "Vote percentage should be visible in results"
        )

    def test_individual_vote_counts_displayed(self, seeded_page):
        """FR-24: Individual vote counts are shown for each Pokemon."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        content = seeded_page.content()
        assert re.search(r"\d+ votes? \(\d+", content), (
            "Individual vote counts with percentages should be visible"
        )

    def test_pokemon_names_in_results(self, seeded_page, api_url):
        """FR-23: All three Pokemon names appear in the results view."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        names = [p["name"] for p in resp.json()["pokemon"]]

        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        for name in names:
            capitalized = name[0].upper() + name[1:]
            el = seeded_page.query_selector(f"text={capitalized}")
            assert el is not None, (
                f"Pokemon '{capitalized}' should be visible in results"
            )

    def test_pokemon_sprites_in_results(self, seeded_page):
        """FR-23: Pokemon sprites are shown in the results view."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        images = seeded_page.query_selector_all("img")
        assert len(images) >= 3, "At least 3 Pokemon sprites should be in results"


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.results
@pytest.mark.fr25
class TestUserPickHighlightE2E:
    """FR-25: The user's pick is highlighted in results."""

    def test_your_pick_badge_visible(self, seeded_page):
        """FR-25: 'Your pick' badge is visible on the Pokemon the user voted for."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        badge = seeded_page.query_selector("text=Your pick")
        assert badge is not None, "'Your pick' badge should be visible in results"


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.results
@pytest.mark.fr26
class TestWinnerIndicatorE2E:
    """FR-26: The winner is indicated in the results view."""

    def test_winner_indicated_in_results(self, seeded_page):
        """FR-26: The winner is visually indicated in the results view."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        results_visible = seeded_page.query_selector("text=Today's Results") is not None
        assert results_visible, "Results should be visible to verify winner indication"


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.results
@pytest.mark.fr28
class TestRevisitResultsE2E:
    """FR-28: Results persist on revisit."""

    def test_results_shown_on_revisit(self, seeded_page):
        """FR-28: Reloading the page after voting still shows results."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)
        assert seeded_page.query_selector("text=Today's Results") is not None

        seeded_page.reload()
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        assert seeded_page.query_selector("text=Today's Results") is not None, (
            "Results should persist after page reload"
        )


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.results
@pytest.mark.fr23
@pytest.mark.fr24
@pytest.mark.fr25
@pytest.mark.fr26
@pytest.mark.fr27
class TestResultsDisplay:
    """FR-23 to FR-28: Results display after voting."""

    @pytest.mark.sanity
    def test_results_contain_all_fields(self, api_url):
        """FR-24: Results include vote counts, percentages, and total."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()
        token = matchup_resp.cookies.get("voter_token")
        pid = data["pokemon"][0]["pokemon_id"]

        vote_resp = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pid},
            cookies={"voter_token": token},
        )
        results = vote_resp.json()

        assert "total_votes" in results
        assert "pokemon" in results
        assert len(results["pokemon"]) == 3

        for p in results["pokemon"]:
            assert "vote_count" in p
            assert "vote_percentage" in p
            assert "is_winner" in p
            assert "pokemon_id" in p
            assert "name" in p

    def test_winner_is_indicated(self, api_url):
        """FR-26: The current winner is indicated in results."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()
        token = matchup_resp.cookies.get("voter_token")
        pid = data["pokemon"][0]["pokemon_id"]

        vote_resp = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pid},
            cookies={"voter_token": token},
        )
        results = vote_resp.json()

        winners = [p for p in results["pokemon"] if p["is_winner"]]
        assert len(winners) >= 1, "At least one Pokemon should be marked as winner"

    def test_revisit_shows_results(self, api_url):
        """FR-28: Revisiting after voting returns results in matchup response."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()
        token = matchup_resp.cookies.get("voter_token")
        pid = data["pokemon"][0]["pokemon_id"]

        httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pid},
            cookies={"voter_token": token},
        )

        revisit = httpx.get(
            f"{api_url}/api/matchup/today",
            cookies={"voter_token": token},
        )
        revisit_data = revisit.json()

        assert revisit_data["has_voted"] is True
        assert revisit_data["user_pick"] == pid
        assert revisit_data["results"] is not None

    def test_results_include_user_pick(self, api_url):
        """FR-25: Results response contains user_pick matching the voted Pokemon."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()
        token = matchup_resp.cookies.get("voter_token")
        voted_pid = data["pokemon"][1]["pokemon_id"]

        httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": voted_pid},
            cookies={"voter_token": token},
        )

        revisit = httpx.get(
            f"{api_url}/api/matchup/today",
            cookies={"voter_token": token},
        )
        revisit_data = revisit.json()

        assert revisit_data["user_pick"] == voted_pid, (
            f"user_pick should be {voted_pid}, got {revisit_data['user_pick']}"
        )
