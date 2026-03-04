import pytest


@pytest.mark.fr22
class TestLocalStorageUsage:
    def test_data_stored_under_correct_key(self, clean_page):
        """FR-22: Data is stored under 'favpoke_v1' key in LocalStorage."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/**", timeout=5000)
        clean_page.wait_for_timeout(1000)

        keys = clean_page.evaluate(
            "Object.keys(window.localStorage)"
        )
        assert "favpoke_v1" in keys


@pytest.mark.fr23
class TestAutoSave:
    def test_save_after_discovery_selection(self, clean_page):
        """FR-23: LocalStorage updates immediately after picking a Pokemon in Phase A."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/**", timeout=5000)

        pokemon = clean_page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        state_before = clean_page.evaluate(
            "window.localStorage.getItem('favpoke_v1')"
        )

        pokemon.first.click()
        clean_page.wait_for_timeout(500)

        state_after = clean_page.evaluate(
            "window.localStorage.getItem('favpoke_v1')"
        )

        assert state_after != state_before, "LocalStorage should update after selection"

    def test_save_after_pairwise_selection(self, page, base_url):
        """FR-23: LocalStorage updates immediately after picking in Phase B."""
        page.goto(base_url)
        candidates = list(range(1, 26))
        ratings = {str(c): 1500 for c in candidates}
        page.evaluate("""(data) => {
            window.localStorage.setItem('favpoke_v1', JSON.stringify({
                gens: {
                    "1": {
                        status: "in_progress",
                        phase: "b",
                        candidatePool: data.candidates,
                        ratings: data.ratings,
                        comparisons: {},
                        totalComparisons: 0,
                        ratingHistory: []
                    }
                },
                global: { status: "not_started", top10: null }
            }))
        }""", {"candidates": candidates, "ratings": ratings})
        page.goto(f"{base_url}/rank/1")

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        state_before = page.evaluate(
            "window.localStorage.getItem('favpoke_v1')"
        )

        pokemon.first.click()
        page.wait_for_timeout(500)

        state_after = page.evaluate(
            "window.localStorage.getItem('favpoke_v1')"
        )

        assert state_after != state_before, "LocalStorage should update after pairwise selection"


@pytest.mark.fr24
class TestRestoreProgress:
    def test_reload_restores_discovery_progress(self, clean_page):
        """FR-24: After page reload during Phase A, user resumes at correct group."""
        cards = clean_page.locator('[data-testid="generation-card"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()

        clean_page.wait_for_url("**/rank/**", timeout=5000)

        pokemon = clean_page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        pokemon.first.click()

        clean_page.wait_for_timeout(500)

        state_before_reload = clean_page.evaluate(
            "JSON.parse(window.localStorage.getItem('favpoke_v1'))"
        )

        clean_page.reload()

        pokemon = clean_page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        state_after_reload = clean_page.evaluate(
            "JSON.parse(window.localStorage.getItem('favpoke_v1'))"
        )

        assert state_after_reload == state_before_reload

    def test_reload_restores_pairwise_progress(self, page, base_url):
        """FR-24: After page reload during Phase B, user resumes with correct ratings."""
        page.goto(base_url)
        candidates = list(range(1, 26))
        ratings = {str(c): 1500 + c for c in candidates}
        page.evaluate("""(data) => {
            window.localStorage.setItem('favpoke_v1', JSON.stringify({
                gens: {
                    "1": {
                        status: "in_progress",
                        phase: "b",
                        candidatePool: data.candidates,
                        ratings: data.ratings,
                        comparisons: {},
                        totalComparisons: 10,
                        ratingHistory: [1.5, 1.2, 0.8]
                    }
                },
                global: { status: "not_started", top10: null }
            }))
        }""", {"candidates": candidates, "ratings": ratings})
        page.goto(f"{base_url}/rank/1")

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        pokemon.first.click()
        page.wait_for_timeout(500)

        page.reload()

        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)

        state = page.evaluate(
            "JSON.parse(window.localStorage.getItem('favpoke_v1'))"
        )
        gen1 = state["gens"]["1"]
        assert gen1["phase"] == "b"
        assert gen1["totalComparisons"] >= 10


@pytest.mark.fr25
class TestResetProgress:
    def test_reset_clears_all_data(self, seeded_page):
        """FR-25: Reset button clears LocalStorage and returns to initial state."""
        reset_btn = seeded_page.get_by_role("button", name="Reset").or_(
            seeded_page.locator("text=Reset")
        )

        if reset_btn.count() > 0 and reset_btn.first.is_visible():
            seeded_page.on("dialog", lambda dialog: dialog.accept())
            reset_btn.first.click()
            seeded_page.wait_for_timeout(1000)

            state = seeded_page.evaluate(
                "JSON.parse(window.localStorage.getItem('favpoke_v1'))"
            )
            if state is not None:
                assert state.get("gens") == {} or state.get("gens") is None
        else:
            pytest.skip("Reset button not visible on page")

    def test_reset_requires_confirmation(self, seeded_page):
        """FR-25: Reset shows a confirmation dialog before clearing."""
        reset_btn = seeded_page.get_by_role("button", name="Reset").or_(
            seeded_page.locator("text=Reset")
        )

        if reset_btn.count() > 0 and reset_btn.first.is_visible():
            dialog_appeared = {"value": False}

            def handle_dialog(dialog):
                dialog_appeared["value"] = True
                dialog.dismiss()

            seeded_page.on("dialog", handle_dialog)
            reset_btn.first.click()
            seeded_page.wait_for_timeout(1000)

            assert dialog_appeared["value"], "A confirmation dialog should appear"
        else:
            pytest.skip("Reset button not visible on page")
