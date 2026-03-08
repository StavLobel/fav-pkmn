import os

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL", "http://localhost:5173")


@pytest.fixture(scope="session")
def api_url():
    return os.getenv("API_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture()
def clean_page(browser, base_url):
    context = browser.new_context()
    context.clear_cookies()
    page = context.new_page()
    page.goto(base_url)
    yield page
    context.close()


@pytest.fixture()
def seeded_page(browser, base_url, api_url):
    """Page with an existing voter_token cookie that has already voted today."""
    import httpx

    context = browser.new_context()
    context.clear_cookies()
    page = context.new_page()

    resp = httpx.get(f"{api_url}/api/matchup/today")
    data = resp.json()
    matchup_id = data["id"]
    pokemon_id = data["pokemon"][0]["pokemon_id"]
    voter_token = resp.cookies.get("voter_token")

    if voter_token:
        context.add_cookies([{
            "name": "voter_token",
            "value": voter_token,
            "url": base_url,
        }])
        httpx.post(
            f"{api_url}/api/vote",
            json={"matchup_id": matchup_id, "pokemon_id": pokemon_id},
            cookies={"voter_token": voter_token},
        )

    page.goto(base_url)
    yield page
    context.close()
