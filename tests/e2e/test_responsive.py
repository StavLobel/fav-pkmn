import pytest


VIEWPORTS = [
    {"width": 375, "height": 812, "name": "mobile"},
    {"width": 768, "height": 1024, "name": "tablet"},
    {"width": 1440, "height": 900, "name": "desktop"},
]


@pytest.mark.nfr_compat
class TestResponsive:
    @pytest.mark.parametrize("viewport", VIEWPORTS, ids=lambda v: v["name"])
    def test_home_page_renders_correctly(self, browser, base_url, viewport):
        """NFR: Home page is usable at mobile, tablet, and desktop widths."""
        context = browser.new_context(
            viewport={"width": viewport["width"], "height": viewport["height"]}
        )
        page = context.new_page()

        page.goto(base_url)

        cards = page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)

        assert cards.count() == 9

        for i in range(cards.count()):
            assert cards.nth(i).is_visible(), (
                f"Card {i + 1} not visible at {viewport['name']} "
                f"({viewport['width']}x{viewport['height']})"
            )

        context.close()

    @pytest.mark.parametrize("viewport", VIEWPORTS, ids=lambda v: v["name"])
    def test_ranking_screen_renders_correctly(self, browser, base_url, viewport):
        """NFR: Ranking screen cards are visible and clickable at all viewports."""
        context = browser.new_context(
            viewport={"width": viewport["width"], "height": viewport["height"]}
        )
        page = context.new_page()

        page.goto(base_url)

        gen_cards = page.locator('[data-testid="generation-card"]')
        gen_cards.first.wait_for(state="visible", timeout=10000)
        gen_cards.first.click()

        page.wait_for_url("**/rank/**", timeout=5000)

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        for i in range(pokemon.count()):
            assert pokemon.nth(i).is_visible(), (
                f"Pokemon card {i + 1} not visible at {viewport['name']} "
                f"({viewport['width']}x{viewport['height']})"
            )

        pokemon.first.click()

        pokemon.first.wait_for(state="visible", timeout=5000)
        assert pokemon.count() >= 2

        context.close()
