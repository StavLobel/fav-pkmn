import re

import httpx
import pytest


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.voting
@pytest.mark.fr12
@pytest.mark.fr13
class TestVotingFlowE2E:
    """User flow 8.2: End-to-end vote submission via browser."""

    @pytest.mark.sanity
    def test_click_pokemon_triggers_vote(self, clean_page, api_url):
        """FR-12/FR-13: Clicking a Pokemon card submits a vote and shows results."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        first_name = resp.json()["pokemon"][0]["name"]
        capitalized = first_name[0].upper() + first_name[1:]

        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        card = clean_page.query_selector(f"text={capitalized}")
        assert card is not None, f"Pokemon '{capitalized}' should be visible"
        card.click()

        clean_page.wait_for_selector("text=Today's Results", timeout=15000)

    def test_voting_prompt_disappears_after_vote(self, clean_page, api_url):
        """FR-12: The voting interface is replaced by results after a successful vote."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        first_name = resp.json()["pokemon"][0]["name"]
        capitalized = first_name[0].upper() + first_name[1:]

        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)
        clean_page.click(f"text={capitalized}")

        clean_page.wait_for_selector("text=Today's Results", timeout=15000)
        prompt = clean_page.query_selector("text=Who's your favorite?")
        assert prompt is None, "Voting prompt should disappear after voting"

    def test_vote_count_appears_after_vote(self, clean_page, api_url):
        """FR-13: After voting, vote counts are visible in the results."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        first_name = resp.json()["pokemon"][0]["name"]
        capitalized = first_name[0].upper() + first_name[1:]

        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)
        clean_page.click(f"text={capitalized}")

        clean_page.wait_for_selector("text=Today's Results", timeout=15000)
        content = clean_page.content()
        assert re.search(r"total vote", content), "Total vote count should be visible"

    def test_your_pick_badge_appears(self, clean_page, api_url):
        """FR-12: The Pokemon the user voted for is marked with 'Your pick'."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        first_name = resp.json()["pokemon"][0]["name"]
        capitalized = first_name[0].upper() + first_name[1:]

        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)
        clean_page.click(f"text={capitalized}")

        clean_page.wait_for_selector("text=Today's Results", timeout=15000)
        badge = clean_page.query_selector("text=Your pick")
        assert badge is not None, "'Your pick' badge should appear on the voted Pokemon"


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.voting
@pytest.mark.fr15
@pytest.mark.fr18
class TestDuplicateVoteE2E:
    """User flow 8.4: Browser prevents re-voting on same day."""

    def test_no_voting_ui_on_second_visit(self, clean_page, api_url):
        """FR-15/FR-18: After voting, revisiting the page shows results not voting UI."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        first_name = resp.json()["pokemon"][0]["name"]
        capitalized = first_name[0].upper() + first_name[1:]

        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)
        clean_page.click(f"text={capitalized}")
        clean_page.wait_for_selector("text=Today's Results", timeout=15000)

        clean_page.reload()
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_timeout(3000)

        results = clean_page.query_selector("text=Today's Results")
        assert results is not None, "Results should persist after page reload"

        prompt = clean_page.query_selector("text=Who's your favorite?")
        assert prompt is None, "Voting prompt should not reappear after reload"


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.voting
@pytest.mark.fr12
@pytest.mark.fr13
@pytest.mark.fr14
@pytest.mark.fr15
class TestVotingFlow:
    """User flow 8.2: Successful vote submission."""

    @pytest.mark.sanity
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


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.voting
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


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.voting
@pytest.mark.fr27
class TestTieHandling:
    """FR-27: Handle ties between Pokemon."""

    def test_tie_produces_multiple_winners(self, api_url):
        """FR-27: When two Pokemon have equal votes, both are marked as winners."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()
        pokemon = data["pokemon"]

        token1_resp = httpx.get(f"{api_url}/api/matchup/today")
        token1 = token1_resp.cookies.get("voter_token")
        httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pokemon[0]["pokemon_id"]},
            cookies={"voter_token": token1},
        )

        token2_resp = httpx.get(f"{api_url}/api/matchup/today")
        token2 = token2_resp.cookies.get("voter_token")
        vote2 = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"], "pokemon_id": pokemon[1]["pokemon_id"]},
            cookies={"voter_token": token2},
        )
        results = vote2.json()

        winners = [p for p in results["pokemon"] if p["is_winner"]]
        assert len(winners) >= 2, "A tie should produce multiple winners"


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.voting
@pytest.mark.security
class TestVoteInputValidation:
    """NFR-10: Reject malformed vote submissions."""

    def test_vote_missing_pokemon_id(self, api_url):
        """NFR-10: POST with missing pokemon_id returns 422."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()
        token = matchup_resp.cookies.get("voter_token")

        resp = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": data["id"]},
            cookies={"voter_token": token},
        )
        assert resp.status_code == 422

    def test_vote_missing_matchup_id(self, api_url):
        """NFR-10: POST with missing matchup_id returns 422."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()
        token = matchup_resp.cookies.get("voter_token")

        resp = httpx.post(
            f"{api_url}/api/vote",
            json={"pokemon_id": data["pokemon"][0]["pokemon_id"]},
            cookies={"voter_token": token},
        )
        assert resp.status_code == 422

    def test_vote_invalid_matchup_id(self, api_url):
        """NFR-10: POST with non-existent matchup_id returns 404."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        token = matchup_resp.cookies.get("voter_token")

        resp = httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": 999999, "pokemon_id": 1},
            cookies={"voter_token": token},
        )
        assert resp.status_code == 404

    def test_vote_without_voter_token(self, api_url):
        """NFR-10: POST without voter_token cookie returns 401."""
        matchup_resp = httpx.get(f"{api_url}/api/matchup/today")
        data = matchup_resp.json()

        resp = httpx.post(
            f"{api_url}/api/vote",
            json={
                "matchup_id": data["id"],
                "pokemon_id": data["pokemon"][0]["pokemon_id"],
            },
        )
        assert resp.status_code == 401
