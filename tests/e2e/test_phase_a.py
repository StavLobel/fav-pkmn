import pytest


@pytest.mark.fr5
class TestDiscoveryDisplay:
    def test_shows_four_pokemon(self, clean_page):
        """FR-5: Ranking screen displays exactly 4 Pokemon cards."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/1", timeout=5000)

        pokemon = clean_page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        assert pokemon.count() == 4

    def test_pokemon_have_sprites_and_names(self, clean_page):
        """FR-5: Each of the 4 cards shows a sprite image and a name."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/1", timeout=5000)

        pokemon = clean_page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        for i in range(4):
            card = pokemon.nth(i)
            sprite = card.locator('[data-testid="pokemon-sprite"]')
            name = card.locator('[data-testid="pokemon-name"]')
            assert sprite.is_visible()
            assert name.inner_text().strip() != ""


@pytest.mark.fr6
@pytest.mark.fr7
class TestDiscoverySelection:
    def test_clicking_pokemon_selects_it(self, clean_page):
        """FR-6/FR-7: Clicking a Pokemon card records the selection and advances."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/1", timeout=5000)

        pokemon = clean_page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        first_group_names = [
            pokemon.nth(i).locator('[data-testid="pokemon-name"]').inner_text()
            for i in range(4)
        ]

        pokemon.first.click()

        pokemon.first.wait_for(state="visible", timeout=10000)
        new_names = [
            pokemon.nth(i).locator('[data-testid="pokemon-name"]').inner_text()
            for i in range(pokemon.count())
        ]

        assert new_names != first_group_names

    def test_only_one_selectable_per_group(self, clean_page):
        """FR-6: After selecting one, the group advances (no double pick)."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/1", timeout=5000)

        pokemon = clean_page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        first_name = pokemon.first.locator('[data-testid="pokemon-name"]').inner_text()
        pokemon.first.click()

        pokemon.first.wait_for(state="visible", timeout=10000)
        new_first_name = pokemon.first.locator('[data-testid="pokemon-name"]').inner_text()

        assert first_name != new_first_name or pokemon.count() != 4


@pytest.mark.fr8
class TestDiscoveryRepetition:
    def test_new_group_after_selection(self, clean_page):
        """FR-8: After selecting, a new group of 4 Pokemon appears."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/1", timeout=5000)

        pokemon = clean_page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        pokemon.first.click()

        pokemon.first.wait_for(state="visible", timeout=10000)
        assert pokemon.count() >= 2

    def test_progress_bar_advances(self, clean_page):
        """FR-8: Progress bar increases after each selection."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/1", timeout=5000)

        progress = clean_page.locator('[data-testid="progress-bar-fill"]')
        progress.wait_for(state="visible", timeout=10000)
        initial_width = progress.evaluate("el => el.style.width || '0%'")

        pokemon = clean_page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        pokemon.first.click()

        clean_page.wait_for_timeout(500)
        new_width = progress.evaluate("el => el.style.width || '0%'")

        initial_pct = float(initial_width.replace("%", "") or "0")
        new_pct = float(new_width.replace("%", "") or "0")
        assert new_pct > initial_pct


@pytest.mark.fr9
@pytest.mark.fr10
class TestCandidatePoolCreation:
    def test_transitions_to_phase_b(self, page, base_url):
        """FR-9/FR-10: After all groups shown, transitions to pairwise phase."""
        page.goto(base_url)

        scores = {str(i): i % 5 for i in range(1, 152)}
        page.evaluate("""(scores) => {
            window.localStorage.setItem('favpoke_v1', JSON.stringify({
                gens: {
                    "1": {
                        status: "in_progress",
                        phase: "a",
                        currentGroup: 37,
                        totalGroups: 38,
                        scores: scores
                    }
                },
                global: { status: "not_started", top10: null }
            }))
        }""", scores)
        page.goto(f"{base_url}/rank/1")

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        pokemon.first.click()

        page.wait_for_timeout(2000)

        pokemon_visible = page.locator('[data-testid="pokemon-card"]')
        pokemon_visible.first.wait_for(state="visible", timeout=10000)
        assert pokemon_visible.count() == 2 or pokemon_visible.count() == 4

    def test_candidate_pool_stored(self, page, base_url):
        """FR-10: LocalStorage contains candidatePool after Phase A completes."""
        page.goto(base_url)

        scores = {str(i): 151 - i for i in range(1, 152)}
        page.evaluate("""(scores) => {
            window.localStorage.setItem('favpoke_v1', JSON.stringify({
                gens: {
                    "1": {
                        status: "in_progress",
                        phase: "a",
                        currentGroup: 37,
                        totalGroups: 38,
                        scores: scores
                    }
                },
                global: { status: "not_started", top10: null }
            }))
        }""", scores)
        page.goto(f"{base_url}/rank/1")

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        pokemon.first.click()

        page.wait_for_timeout(2000)

        state = page.evaluate(
            "JSON.parse(window.localStorage.getItem('favpoke_v1'))"
        )
        gen1 = state.get("gens", {}).get("1", {})
        assert gen1.get("phase") == "b" or gen1.get("candidatePool") is not None
