import pytest
import httpx


@pytest.mark.fr23
@pytest.mark.fr24
@pytest.mark.fr25
@pytest.mark.fr26
@pytest.mark.fr27
class TestResultsDisplay:
    """FR-23 to FR-28: Results display after voting."""

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
