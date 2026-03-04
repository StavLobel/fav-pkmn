import pytest
from playwright.sync_api import Page, Browser


@pytest.fixture(scope="session")
def base_url():
    return "http://app:5173"


@pytest.fixture
def page(browser: Browser, base_url: str):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def clean_page(page: Page, base_url: str):
    """Page with cleared LocalStorage."""
    page.goto(base_url)
    page.evaluate("window.localStorage.clear()")
    page.reload()
    return page


@pytest.fixture
def seeded_page(page: Page, base_url: str):
    """Page with pre-seeded LocalStorage (Gen 1 completed)."""
    page.goto(base_url)
    page.evaluate("""
        window.localStorage.setItem('favpoke_v1', JSON.stringify({
            gens: {
                "1": {
                    status: "completed",
                    top10: [
                        { id: 25, name: "pikachu", rating: 1620 },
                        { id: 6, name: "charizard", rating: 1590 },
                        { id: 150, name: "mewtwo", rating: 1570 },
                        { id: 131, name: "lapras", rating: 1550 },
                        { id: 143, name: "snorlax", rating: 1530 },
                        { id: 9, name: "blastoise", rating: 1510 },
                        { id: 3, name: "venusaur", rating: 1495 },
                        { id: 130, name: "gyarados", rating: 1480 },
                        { id: 149, name: "dragonite", rating: 1470 },
                        { id: 94, name: "gengar", rating: 1460 }
                    ]
                }
            },
            global: { status: "not_started", top10: null }
        }))
    """)
    page.reload()
    return page
