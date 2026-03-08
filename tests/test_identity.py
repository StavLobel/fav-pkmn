import pytest
import httpx


@pytest.mark.fr19
@pytest.mark.fr20
@pytest.mark.fr21
class TestAnonymousIdentity:
    """FR-19 to FR-22: Anonymous browser identity via cookies."""

    def test_first_visit_sets_voter_token_cookie(self, api_url):
        """FR-19/FR-20: A random voter token is generated and set as a cookie."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        assert resp.status_code == 200
        token = resp.cookies.get("voter_token")
        assert token is not None, "voter_token cookie should be set on first visit"
        assert len(token) == 36, "Token should be a UUID"

    def test_existing_token_is_reused(self, api_url):
        """FR-21: The existing token is included in subsequent requests."""
        first = httpx.get(f"{api_url}/api/matchup/today")
        token = first.cookies.get("voter_token")

        second = httpx.get(
            f"{api_url}/api/matchup/today",
            cookies={"voter_token": token},
        )
        new_token = second.cookies.get("voter_token")
        assert new_token is None, "Should not set a new cookie when token already exists"


@pytest.mark.fr22
class TestVoteUniqueness:
    """FR-22: Vote uniqueness via matchup_id + voter_token."""

    def test_different_tokens_can_both_vote(self, api_url):
        """FR-22: Two different tokens can each vote for the same matchup."""
        resp1 = httpx.get(f"{api_url}/api/matchup/today")
        token1 = resp1.cookies.get("voter_token")
        data = resp1.json()
        pid = data["pokemon"][0]["pokemon_id"]

        httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pid},
            cookies={"voter_token": token1},
        )

        resp2 = httpx.get(f"{api_url}/api/matchup/today")
        token2 = resp2.cookies.get("voter_token")

        vote2 = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pid},
            cookies={"voter_token": token2},
        )
        assert vote2.status_code == 200
