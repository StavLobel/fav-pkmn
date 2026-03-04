import pytest


def _make_top10(gen_id, start_id):
    """Generate a fake top 10 for a generation."""
    return [
        {"id": start_id + i, "name": f"pokemon-{start_id + i}", "rating": 1600 - i * 15}
        for i in range(10)
    ]


GEN_RANGES = [
    (1, 1), (2, 152), (3, 252), (4, 387),
    (5, 494), (6, 650), (7, 722), (8, 810), (9, 906),
]

ALL_COMPLETED_STATE = {
    "gens": {
        str(gen_id): {
            "status": "completed",
            "top10": _make_top10(gen_id, start_id),
        }
        for gen_id, start_id in GEN_RANGES
    },
    "global": {"status": "not_started", "top10": None},
}


@pytest.fixture
def all_gens_completed_page(page, base_url):
    """Page with all 9 generations completed (mocked Top 10s)."""
    page.goto(base_url)
    page.evaluate(
        "(state) => window.localStorage.setItem('favpoke_v1', JSON.stringify(state))",
        ALL_COMPLETED_STATE,
    )
    page.reload()
    return page


@pytest.mark.fr17
class TestChampionshipCollection:
    def test_championship_button_visible_when_all_complete(self, all_gens_completed_page):
        """FR-17: 'Start Championship' button appears when all 9 gens are done."""
        page = all_gens_completed_page
        btn = page.get_by_role("button", name="Championship").or_(
            page.get_by_role("link", name="Championship")
        ).or_(
            page.locator("text=Championship")
        )
        btn.first.wait_for(state="visible", timeout=10000)
        assert btn.first.is_visible()

    def test_championship_button_hidden_when_incomplete(self, seeded_page):
        """FR-17: Button is not visible when some gens are not completed."""
        btn = seeded_page.locator("text=Championship")
        assert btn.count() == 0 or not btn.first.is_visible()


@pytest.mark.fr18
class TestGlobalPool:
    def test_championship_starts_pairwise(self, all_gens_completed_page):
        """FR-18: Clicking championship starts pairwise comparisons."""
        page = all_gens_completed_page
        btn = page.get_by_role("button", name="Championship").or_(
            page.get_by_role("link", name="Championship")
        ).or_(
            page.locator("text=Championship")
        )
        btn.first.click()

        page.wait_for_url("**/championship**", timeout=5000)
        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        assert pokemon.count() == 2


@pytest.mark.fr19
class TestGlobalPairwise:
    def test_shows_two_pokemon_from_different_gens(self, all_gens_completed_page):
        """FR-19: Pairwise screen shows Pokemon that may be from different gens."""
        page = all_gens_completed_page
        btn = page.get_by_role("button", name="Championship").or_(
            page.get_by_role("link", name="Championship")
        ).or_(
            page.locator("text=Championship")
        )
        btn.first.click()

        page.wait_for_url("**/championship**", timeout=5000)
        pokemon = page.locator('[data-testid="pokemon-card"]')
        pokemon.first.wait_for(state="visible", timeout=10000)
        assert pokemon.count() == 2

        names = [
            pokemon.nth(i).locator('[data-testid="pokemon-name"]').inner_text()
            for i in range(2)
        ]
        assert names[0] != names[1]


@pytest.mark.fr20
class TestGlobalTopTen:
    def test_produces_global_top_10(self, page, base_url):
        """FR-20: Championship result shows 10 ranked Pokemon."""
        page.goto(base_url)
        completed_state = dict(ALL_COMPLETED_STATE)
        completed_state["global"] = {
            "status": "completed",
            "top10": [
                {"id": i + 1, "name": f"champion-{i + 1}", "rating": 1700 - i * 20}
                for i in range(10)
            ],
        }
        page.evaluate(
            "(state) => window.localStorage.setItem('favpoke_v1', JSON.stringify(state))",
            completed_state,
        )
        page.goto(f"{base_url}/championship/result")

        items = page.locator('[data-testid="top-list-item"]')
        items.first.wait_for(state="visible", timeout=10000)
        assert items.count() == 10


@pytest.mark.fr21
class TestFinalRanking:
    def test_displays_final_ranking_screen(self, page, base_url):
        """FR-21: Final result screen shows names, sprites, and ranks."""
        page.goto(base_url)
        completed_state = dict(ALL_COMPLETED_STATE)
        completed_state["global"] = {
            "status": "completed",
            "top10": [
                {"id": i + 1, "name": f"champion-{i + 1}", "rating": 1700 - i * 20}
                for i in range(10)
            ],
        }
        page.evaluate(
            "(state) => window.localStorage.setItem('favpoke_v1', JSON.stringify(state))",
            completed_state,
        )
        page.goto(f"{base_url}/championship/result")

        items = page.locator('[data-testid="top-list-item"]')
        items.first.wait_for(state="visible", timeout=10000)

        first_item = items.first
        assert first_item.locator("img").count() >= 1
        assert first_item.inner_text().strip() != ""

    def test_ranking_summary_present(self, page, base_url):
        """FR-21: A ranking summary section is visible."""
        page.goto(base_url)
        completed_state = dict(ALL_COMPLETED_STATE)
        completed_state["global"] = {
            "status": "completed",
            "top10": [
                {"id": i + 1, "name": f"champion-{i + 1}", "rating": 1700 - i * 20}
                for i in range(10)
            ],
        }
        page.evaluate(
            "(state) => window.localStorage.setItem('favpoke_v1', JSON.stringify(state))",
            completed_state,
        )
        page.goto(f"{base_url}/championship/result")

        top_list = page.locator('[data-testid="top-list"]')
        top_list.wait_for(state="visible", timeout=10000)
        assert top_list.is_visible()
