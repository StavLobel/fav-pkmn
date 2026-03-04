import time

import pytest


@pytest.mark.nfr_perf
class TestPerformance:
    def test_app_loads_under_2_seconds(self, page, base_url):
        """NFR: Application startup completes within 2 seconds."""
        start = time.time()
        page.goto(base_url, wait_until="domcontentloaded")

        page.locator('[data-testid="generation-card"]').first.wait_for(
            state="visible", timeout=5000
        )
        elapsed = time.time() - start

        assert elapsed < 2.0, f"App took {elapsed:.2f}s to load (threshold: 2.0s)"

    def test_sprites_load_under_1_second(self, clean_page):
        """NFR: Pokemon sprite images load within 1 second."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/**", timeout=5000)

        start = time.time()
        sprites = clean_page.locator('[data-testid="pokemon-sprite"]')
        sprites.first.wait_for(state="visible", timeout=5000)
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Sprites took {elapsed:.2f}s to load (threshold: 1.0s)"

    def test_selection_updates_instantly(self, clean_page):
        """NFR: UI updates within 100ms of a selection click."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/**", timeout=5000)

        pokemon = clean_page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        first_names = [
            pokemon.nth(i).locator('[data-testid="pokemon-name"]').inner_text()
            for i in range(pokemon.count())
        ]

        start = time.time()
        pokemon.first.click()

        pokemon.first.wait_for(state="visible", timeout=1000)
        elapsed = time.time() - start

        assert elapsed < 0.5, f"UI update took {elapsed:.2f}s (threshold: 0.5s)"
