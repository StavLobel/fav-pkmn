import re

import pytest


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.matchup
class TestVsBadgeE2E:
    """VS badge should appear between Pokemon cards on the voting screen."""

    def test_vs_badge_visible_on_voting_screen(self, clean_page):
        """The VS badge appears between Pokemon cards."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        vs_badge = clean_page.query_selector("text=VS")
        assert vs_badge is not None, "VS badge should be visible between Pokemon cards"


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.results
class TestShareButtonE2E:
    """Share button should appear on the results screen."""

    def test_share_button_visible_after_voting(self, seeded_page):
        """A Share button appears on the results screen."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        share_btn = seeded_page.query_selector("text=Share")
        assert share_btn is not None, "Share button should be visible on results screen"


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.results
class TestCountdownTimerE2E:
    """Countdown timer should appear on the results screen."""

    def test_countdown_visible_after_voting(self, seeded_page):
        """A countdown timer showing time until next challenge appears."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        label = seeded_page.query_selector("text=Next challenge in")
        assert label is not None, "Countdown label should be visible on results screen"

        content = seeded_page.content()
        assert re.search(r"\d{2}:\d{2}:\d{2}", content), (
            "Countdown timer should show HH:MM:SS format"
        )


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.results
class TestAlreadyVotedBannerE2E:
    """'You voted earlier today!' banner shows on revisit."""

    def test_banner_shows_on_revisit(self, seeded_page):
        """The already-voted banner appears when revisiting after voting."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        banner = seeded_page.query_selector("text=You voted earlier today!")
        assert banner is not None, (
            "'You voted earlier today!' banner should appear on revisit"
        )


@pytest.mark.regression
@pytest.mark.e2e
class TestDisclaimerFooterE2E:
    """Disclaimer footer should appear on every screen."""

    def test_disclaimer_on_daily_challenge(self, clean_page):
        """The disclaimer footer is visible on the daily challenge screen."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        content = clean_page.content()
        assert "not affiliated with" in content, (
            "Disclaimer text should be visible on the daily challenge screen"
        )

    def test_disclaimer_on_history(self, clean_page, base_url):
        """The disclaimer footer is visible on the history screen."""
        clean_page.goto(f"{base_url}/#/history")
        clean_page.wait_for_selector("text=History", timeout=15000)
        clean_page.wait_for_timeout(3000)

        content = clean_page.content()
        assert "not affiliated with" in content, (
            "Disclaimer text should be visible on the history screen"
        )


@pytest.mark.regression
@pytest.mark.e2e
class TestPrivacyPolicyE2E:
    """Privacy Policy link and page."""

    def test_privacy_link_visible(self, clean_page):
        """A Privacy Policy link is visible in the footer."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        link = clean_page.query_selector("text=Privacy Policy")
        assert link is not None, "Privacy Policy link should be visible in footer"

    def test_privacy_page_navigable(self, clean_page, base_url):
        """The privacy policy page renders with expected content."""
        clean_page.goto(f"{base_url}/#/privacy")
        clean_page.wait_for_timeout(3000)

        content = clean_page.content()
        assert "Cookies" in content or "cookies" in content, (
            "Privacy policy should mention cookies"
        )
        assert "PokeAPI" in content or "pokeapi" in content, (
            "Privacy policy should mention PokeAPI"
        )


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.history
class TestHistoryDateFormattingE2E:
    """History dates should be formatted as human-readable text."""

    def test_today_label_in_history(self, seeded_page, base_url):
        """Today's entry should show 'Today' instead of ISO date."""
        seeded_page.goto(f"{base_url}/#/history")
        seeded_page.wait_for_selector("text=History", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        content = seeded_page.content()
        if "No history yet" not in content:
            assert "Today" in content or re.search(r"[A-Z][a-z]{2} \d", content), (
                "History dates should be formatted as readable text"
            )
