import pytest
import httpx


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.daily_reset
@pytest.mark.fr29
@pytest.mark.fr30
class TestDailyReset:
    """FR-29/FR-30: Daily challenge reset and new matchup generation."""

    def test_new_day_produces_new_matchup(self, api_url):
        """FR-29/FR-30: Different dates produce different matchups."""
        resp_day1 = httpx.get(
            f"{api_url}/api/matchup/today",
            params={"_test_date": "2099-01-01"},
        )
        assert resp_day1.status_code == 200

        resp_day2 = httpx.get(
            f"{api_url}/api/matchup/today",
            params={"_test_date": "2099-01-02"},
        )
        assert resp_day2.status_code == 200

        assert resp_day1.json()["id"] != resp_day2.json()["id"], (
            "Different dates must produce different matchups"
        )

    def test_same_date_returns_same_matchup(self, api_url):
        """FR-29: The same date always returns the same matchup."""
        resp1 = httpx.get(
            f"{api_url}/api/matchup/today",
            params={"_test_date": "2099-02-01"},
        )
        resp2 = httpx.get(
            f"{api_url}/api/matchup/today",
            params={"_test_date": "2099-02-01"},
        )

        assert resp1.json()["id"] == resp2.json()["id"]


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.daily_reset
@pytest.mark.fr32
class TestParticipationAfterReset:
    """FR-32: Users can participate in a new challenge after daily reset."""

    def test_can_vote_on_new_day_after_previous_vote(self, api_url):
        """FR-32: A token that voted on day 1 can vote again on day 2."""
        resp_day1 = httpx.get(
            f"{api_url}/api/matchup/today",
            params={"_test_date": "2099-03-01"},
        )
        data_day1 = resp_day1.json()
        token = resp_day1.cookies.get("voter_token")

        vote1 = httpx.post(
            f"{api_url}/api/vote",
            json={
                "matchup_id": data_day1["id"],
                "pokemon_id": data_day1["pokemon"][0]["pokemon_id"],
            },
            cookies={"voter_token": token},
        )
        assert vote1.status_code == 200

        resp_day2 = httpx.get(
            f"{api_url}/api/matchup/today",
            params={"_test_date": "2099-03-02"},
            cookies={"voter_token": token},
        )
        data_day2 = resp_day2.json()

        assert data_day2["has_voted"] is False, (
            "User should not be marked as voted on the new day"
        )

        vote2 = httpx.post(
            f"{api_url}/api/vote",
            json={
                "matchup_id": data_day2["id"],
                "pokemon_id": data_day2["pokemon"][0]["pokemon_id"],
            },
            cookies={"voter_token": token},
        )
        assert vote2.status_code == 200

    def test_previous_day_vote_does_not_block_new_day(self, api_url):
        """FR-29: Yesterday's vote has no effect on today's matchup state."""
        resp_day1 = httpx.get(
            f"{api_url}/api/matchup/today",
            params={"_test_date": "2099-04-10"},
        )
        data_day1 = resp_day1.json()
        token = resp_day1.cookies.get("voter_token")

        httpx.post(
            f"{api_url}/api/vote",
            json={
                "matchup_id": data_day1["id"],
                "pokemon_id": data_day1["pokemon"][0]["pokemon_id"],
            },
            cookies={"voter_token": token},
        )

        resp_day2 = httpx.get(
            f"{api_url}/api/matchup/today",
            params={"_test_date": "2099-04-11"},
            cookies={"voter_token": token},
        )
        data_day2 = resp_day2.json()

        assert data_day2["has_voted"] is False
        assert data_day2["results"] is None
