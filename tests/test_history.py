import pytest
import httpx


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
