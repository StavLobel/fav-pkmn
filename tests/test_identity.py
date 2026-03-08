import pytest
import httpx


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.identity
@pytest.mark.fr19
@pytest.mark.fr20
class TestBrowserTokenE2E:
    """FR-19/FR-20: Anonymous voter token is set in the browser."""

    def test_voter_token_cookie_set_on_page_load(self, clean_page, base_url):
        """FR-19/FR-20: Loading the page sets a voter_token cookie in the browser."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        cookies = clean_page.context.cookies()
        token_cookies = [c for c in cookies if c["name"] == "voter_token"]
        assert len(token_cookies) >= 1, (
            "voter_token cookie should be set after page load"
        )

    def test_voter_token_persists_across_reload(self, clean_page, base_url):
        """FR-20: The voter_token cookie persists across page reloads."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        cookies_before = clean_page.context.cookies()
        token_before = next(
            (c["value"] for c in cookies_before if c["name"] == "voter_token"), None
        )
        assert token_before is not None

        clean_page.reload()
        clean_page.wait_for_selector("text=PokePick", timeout=15000)

        cookies_after = clean_page.context.cookies()
        token_after = next(
            (c["value"] for c in cookies_after if c["name"] == "voter_token"), None
        )
        assert token_after == token_before, (
            "voter_token should remain the same after reload"
        )

    def test_voter_token_is_uuid_format(self, clean_page, base_url):
        """FR-19: The voter token is a UUID."""
        import re

        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        cookies = clean_page.context.cookies()
        token = next(
            (c["value"] for c in cookies if c["name"] == "voter_token"), None
        )
        assert token is not None
        assert re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            token,
        ), f"Token '{token}' should be a valid UUID"


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.identity
@pytest.mark.fr21
class TestBrowserTokenUsedInVoteE2E:
    """FR-21: The browser token is used when submitting a vote."""

    def test_vote_uses_browser_cookie(self, clean_page, api_url):
        """FR-21: Voting through the UI uses the browser's voter_token cookie."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        cookies_before = clean_page.context.cookies()
        token = next(
            (c["value"] for c in cookies_before if c["name"] == "voter_token"), None
        )
        assert token is not None

        resp = httpx.get(f"{api_url}/api/matchup/today")
        first_name = resp.json()["pokemon"][0]["name"]
        capitalized = first_name[0].upper() + first_name[1:]

        clean_page.click(f"text={capitalized}")
        clean_page.wait_for_selector("text=Today's Results", timeout=15000)

        cookies_after = clean_page.context.cookies()
        token_after = next(
            (c["value"] for c in cookies_after if c["name"] == "voter_token"), None
        )
        assert token_after is not None, (
            "voter_token should still exist after voting"
        )


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.identity
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


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.identity
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


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.identity
@pytest.mark.security
class TestCookieSecurityAttributes:
    """NFR-7/NFR-8: Secure cookie attributes."""

    def test_voter_token_cookie_is_httponly(self, api_url):
        """NFR-8: voter_token cookie has HttpOnly flag."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        set_cookie = resp.headers.get("set-cookie", "")
        assert "httponly" in set_cookie.lower(), "Cookie should have HttpOnly flag"

    def test_voter_token_cookie_samesite_lax(self, api_url):
        """NFR-8: voter_token cookie has SameSite=Lax."""
        resp = httpx.get(f"{api_url}/api/matchup/today")
        set_cookie = resp.headers.get("set-cookie", "")
        assert "samesite=lax" in set_cookie.lower(), "Cookie should have SameSite=Lax"
