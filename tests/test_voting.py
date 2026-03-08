import pytest
import httpx


@pytest.mark.fr12
@pytest.mark.fr13
@pytest.mark.fr14
@pytest.mark.fr15
class TestVotingFlow:
    """User flow 8.2: Successful vote submission."""

    def test_vote_submission_via_api(self, api_url):
        """FR-12/FR-13: A vote can be submitted through the API."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        assert matchup_resp.status_code == 200
        data = matchup_resp.json()

        token = matchup_resp.cookies.get("voter_token")
        assert token is not None, "Should receive a voter_token cookie"

        pokemon_id = data["pokemon"][0]["pokemon_id"]
        vote_resp = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pokemon_id},
            cookies={"voter_token": token},
        )
        assert vote_resp.status_code == 200

        results = vote_resp.json()
        assert results["total_votes"] >= 1
        assert results["matchup_id"] == data["id"]

    def test_vote_validates_pokemon_belongs_to_matchup(self, api_url):
        """FR-14: Rejects vote for a Pokemon not in the matchup."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()
        token = matchup_resp.cookies.get("voter_token")

        vote_resp = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": 999999},
            cookies={"voter_token": token},
        )
        assert vote_resp.status_code == 400


@pytest.mark.fr16
@pytest.mark.fr17
@pytest.mark.fr18
class TestDuplicateVote:
    """User flow 8.4: Attempted duplicate vote."""

    def test_rejects_duplicate_vote(self, api_url):
        """FR-15/FR-18: Duplicate vote from same token is rejected."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()
        token = matchup_resp.cookies.get("voter_token")
        pokemon_id = data["pokemon"][0]["pokemon_id"]

        first = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pokemon_id},
            cookies={"voter_token": token},
        )
        assert first.status_code == 200

        second = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pokemon_id},
            cookies={"voter_token": token},
        )
        assert second.status_code == 409
