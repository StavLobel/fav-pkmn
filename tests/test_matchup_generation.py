import pytest
import httpx


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.matchup
@pytest.mark.fr1
@pytest.mark.fr2
@pytest.mark.fr5
class TestMatchupGeneration:
    """FR-1 to FR-5: Daily matchup generation."""

    @pytest.mark.sanity
    def test_matchup_contains_three_unique_pokemon(self, api_url):
        """FR-1/FR-5: Matchup has exactly 3 unique Pokemon."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        assert resp.status_code == 200
        data = resp.json()

        assert len(data["pokemon"]) == 3
        ids = [p["pokemon_id"] for p in data["pokemon"]]
        assert len(set(ids)) == 3, "All three Pokemon must be unique"

    def test_same_matchup_for_all_users(self, api_url):
        """FR-2: Same matchup is returned for different users."""
        resp1 = httpx.get(f"{api_url}/api/matchup/today")
        resp2 = httpx.get(f"{api_url}/api/matchup/today")

        assert resp1.json()["id"] == resp2.json()["id"]

    def test_matchup_has_pokemon_metadata(self, api_url):
        """FR-6/FR-9: Each Pokemon has name, sprite, and types."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        data = resp.json()

        for p in data["pokemon"]:
            assert p["name"], "Pokemon should have a name"
            assert p["sprite_url"], "Pokemon should have a sprite URL"
            assert isinstance(p["types"], list), "Types should be a list"
            assert len(p["types"]) >= 1, "Pokemon should have at least one type"
