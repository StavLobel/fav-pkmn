import re

import pytest


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.matchup
@pytest.mark.fr8
@pytest.mark.fr9
@pytest.mark.fr10
class TestDailyChallengeDisplay:
    """User flow 8.1: First visit - before voting."""

    @pytest.mark.sanity
    def test_shows_three_pokemon(self, clean_page):
        """FR-8/FR-10: The daily challenge displays exactly 3 selectable Pokemon."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        images = clean_page.query_selector_all("img")
        assert len(images) >= 3, (
            f"Expected at least 3 Pokemon sprites, got {len(images)}"
        )

    def test_shows_voting_prompt(self, clean_page):
        """FR-8: System displays the daily matchup with a prompt to vote."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        assert clean_page.query_selector("text=Who's your favorite?") is not None

    def test_shows_vote_instruction(self, clean_page):
        """FR-10: Subtitle instructs the user to tap a Pokemon."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        instruction = clean_page.query_selector("text=Tap a Pokemon to cast your vote")
        assert instruction is not None, "Vote instruction subtitle should be visible"

    def test_pokemon_names_are_visible(self, clean_page, api_url):
        """FR-9: Each Pokemon's name is displayed on the card."""
        import httpx

        resp = httpx.get(f"{api_url}/api/matchup/today")
        names = [p["name"] for p in resp.json()["pokemon"]]

        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        for name in names:
            capitalized = name[0].upper() + name[1:]
            el = clean_page.query_selector(f"text={capitalized}")
            assert el is not None, f"Pokemon name '{capitalized}' should be visible"

    def test_pokemon_sprites_have_src(self, clean_page):
        """FR-9: Each Pokemon sprite image has a valid source URL."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        images = clean_page.query_selector_all("img")
        sprites = [
            img for img in images if "pokeapi" in (img.get_attribute("src") or "")
        ]
        assert len(sprites) >= 3, (
            f"Expected 3 PokeAPI sprite images, got {len(sprites)}"
        )

    def test_type_chips_are_displayed(self, clean_page, api_url):
        """FR-9: Pokemon type badges are visible on the cards."""
        import httpx

        resp = httpx.get(f"{api_url}/api/matchup/today")
        all_types = set()
        for p in resp.json()["pokemon"]:
            for t in p["types"]:
                all_types.add(t[0].upper() + t[1:])

        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        clean_page.wait_for_selector("img", timeout=15000)

        found = 0
        for type_name in all_types:
            if clean_page.query_selector(f"text={type_name}") is not None:
                found += 1

        assert found >= 1, "At least one type chip should be visible on the cards"

    def test_app_bar_title_is_pokepick(self, clean_page):
        """FR-8: The app bar displays 'PokePick' as the title."""
        title = clean_page.wait_for_selector("text=PokePick", timeout=15000)
        assert title is not None

    def test_history_button_is_visible(self, clean_page):
        """FR-8: The history navigation button is present in the app bar."""
        clean_page.wait_for_selector("text=PokePick", timeout=15000)
        history_btn = clean_page.query_selector("[aria-label='History']")
        if history_btn is None:
            history_btn = clean_page.query_selector("text=History")
        assert (
            history_btn is not None
            or clean_page.query_selector("button >> text=history") is not None
        ), "History button should be accessible in the app bar"


@pytest.mark.regression
@pytest.mark.e2e
@pytest.mark.matchup
@pytest.mark.fr11
class TestCompletionState:
    """User flow 8.3: Revisiting after voting."""

    def test_shows_results_after_voting(self, seeded_page):
        """FR-11/FR-28: After voting, results are shown instead of voting UI."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        results_visible = seeded_page.query_selector("text=Today's Results") is not None
        assert results_visible, "Results should be displayed after voting"

    def test_voting_prompt_hidden_after_voting(self, seeded_page):
        """FR-11: The voting prompt is not shown when the user has already voted."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        prompt = seeded_page.query_selector("text=Who's your favorite?")
        assert prompt is None, "Voting prompt should not appear after voting"

    def test_total_votes_visible_on_revisit(self, seeded_page):
        """FR-28: Revisiting shows results with total vote count."""
        seeded_page.wait_for_selector("text=PokePick", timeout=15000)
        seeded_page.wait_for_timeout(3000)

        content = seeded_page.content()
        assert re.search(r"total vote", content), (
            "Total vote count should be visible on revisit"
        )
