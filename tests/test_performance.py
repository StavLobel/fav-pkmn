import time

import pytest
import httpx


@pytest.mark.nfr_perf
class TestPerformance:
    """NFR-1/NFR-2: Response time benchmarks."""

    def test_matchup_loads_within_2_seconds(self, api_url):
        """NFR-1: GET /api/matchup/today responds in under 2 seconds."""
        start = time.monotonic()
        resp = httpx.get(f"{api_url}/api/matchup/today")
        elapsed = time.monotonic() - start

        assert resp.status_code == 200
        assert elapsed < 2.0, f"Matchup load took {elapsed:.2f}s, expected < 2.0s"

    def test_vote_responds_within_500ms(self, api_url):
        """NFR-2: POST /api/vote responds in under 500 milliseconds."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()
        token = matchup_resp.cookies.get("voter_token")
        pid = data["pokemon"][0]["pokemon_id"]

        start = time.monotonic()
        vote_resp = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pid},
            cookies={"voter_token": token},
        )
        elapsed = time.monotonic() - start

        assert vote_resp.status_code == 200
        assert elapsed < 0.5, f"Vote took {elapsed:.2f}s, expected < 0.5s"
