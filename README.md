# Daily Starter

**A daily Pokemon voting challenge for the web.** Pick your favorite from three random Pokemon each day -- one vote, one chance, every day.

[![CI](https://github.com/StavLobel/fav-pkmn/actions/workflows/ci.yml/badge.svg)](https://github.com/StavLobel/fav-pkmn/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Flutter](https://img.shields.io/badge/Flutter-Web-02569B?logo=flutter)](https://flutter.dev)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docs.docker.com/compose/)

---

## Features

- **Daily challenge** -- Three random Pokemon are selected each day, shared across all users.
- **One vote per day** -- Anonymous browser-based identity enforces a single vote per device.
- **Instant results** -- See aggregated vote counts, percentages, and the current winner immediately after voting.
- **History** -- Browse past matchups and their outcomes.
- **No accounts required** -- Participation is entirely anonymous via secure cookies.
- **Fully containerized** -- One command to run the entire stack locally.

---

## Demo

<!-- Replace with an actual screenshot or GIF once available -->
> Screenshot or demo GIF placeholder. Run `docker compose up` to see it live at http://localhost:5173.

---

## Tech Stack

| Layer        | Technology                  |
|--------------|-----------------------------|
| Frontend     | Flutter (Dart) -- Web       |
| Backend      | FastAPI (Python 3.12)       |
| Database     | PostgreSQL 16               |
| Reverse Proxy| Nginx                       |
| Containers   | Docker / Docker Compose     |
| E2E Testing  | Playwright (pytest)         |
| CI/CD        | GitHub Actions              |

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2+)

No other dependencies need to be installed on the host machine. The Flutter SDK, Python, and all packages are managed inside containers.

### Quick Start

```bash
# Clone the repository
git clone https://github.com/StavLobel/fav-pkmn.git
cd fav-pkmn

# Start all services (database, API, frontend)
docker compose up
```

| Service   | URL                     |
|-----------|-------------------------|
| Frontend  | http://localhost:5173    |
| API       | http://localhost:8000    |
| Database  | localhost:5432           |

Stop everything with `Ctrl+C`, or run `docker compose down` to remove containers. Add `-v` to also remove the database volume.

---

## Development

All development happens inside Docker containers. Do not install project dependencies directly on the host.

### Running Services

```bash
# Start with hot-reload (frontend and backend)
docker compose up
```

The `api` service bind-mounts `backend/` for live reload via uvicorn. The `app` service bind-mounts `frontend/lib/` and `frontend/test/` for Flutter hot-reload.

### Database Migrations

```bash
# Generate a new migration after model changes
docker compose exec api alembic revision --autogenerate -m "description"

# Apply pending migrations
docker compose exec api alembic upgrade head
```

### Linting

```bash
# Python (ruff)
ruff check backend/
ruff format --check backend/

# Dart (flutter analyze inside the container)
docker compose run --rm app flutter analyze
```

---

## Project Structure

```
fav-pkmn/
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── routers/        # API route handlers
│   │   ├── services/       # Business logic
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── database.py     # DB engine and session
│   │   ├── config.py       # Application configuration
│   │   └── main.py         # FastAPI entry point
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Flutter web application
│   ├── lib/
│   │   ├── models/         # Data models
│   │   ├── providers/      # State management
│   │   ├── screens/        # Page-level widgets
│   │   ├── services/       # API client
│   │   ├── widgets/        # Reusable UI components
│   │   └── main.dart       # App entry point
│   ├── test/               # Widget tests
│   ├── web/                # Web-specific assets
│   └── Dockerfile
├── tests/                  # E2E and API tests (pytest + Playwright)
│   ├── conftest.py         # Shared fixtures
│   ├── test_matchup_generation.py
│   ├── test_daily_challenge.py
│   ├── test_voting.py
│   ├── test_identity.py
│   ├── test_results.py
│   ├── test_daily_reset.py
│   ├── test_history.py
│   ├── test_performance.py
│   └── Dockerfile
├── nginx/                  # Reverse proxy configuration
├── docs/                   # Project documentation
│   └── STP.md              # Software Test Procedure
├── .github/                # CI/CD workflows and templates
├── docker-compose.yml      # Development services
├── docker-compose.prod.yml # Production services
├── SRS.md                  # Software Requirements Specification
└── ruff.toml               # Python linter configuration
```

---

## Testing

The project follows a strict **test-driven development** workflow: every feature begins with a failing test.

### Test Layers

| Layer            | Framework           | Command |
|------------------|---------------------|---------|
| Frontend widgets | Flutter test (Dart)  | `docker compose --profile test run --rm test-unit` |
| API tests        | pytest + httpx       | `docker compose --profile test run --rm test-e2e pytest -m api -v` |
| E2E browser      | pytest + Playwright  | `docker compose --profile test run --rm test-e2e pytest -m e2e -v` |

### Running Tests

```bash
# All frontend widget tests
docker compose --profile test run --rm test-unit

# Full E2E and API test suite
docker compose --profile test run --rm test-e2e

# Single SRS requirement (e.g., FR-12: vote submission)
docker compose --profile test run --rm test-e2e pytest -m fr12 -v

# Quick sanity check
docker compose --profile test run --rm test-e2e pytest -m sanity -v

# Security tests only
docker compose --profile test run --rm test-e2e pytest -m security -v
```

Tests are tagged with `@pytest.mark.<fr_id>` markers corresponding to functional requirements in the [SRS](SRS.md). Suite markers (`sanity`, `regression`, `smoke`) and feature markers (`matchup`, `voting`, `identity`, etc.) are also available. See [docs/STP.md](docs/STP.md) for the full test procedure and marker reference.

---

## Deployment

The project uses a two-stage deployment pipeline via GitHub Actions:

1. **Development** -- Pushes to `develop` trigger the CI workflow. On success, the app is automatically deployed to a dev VPS using `docker-compose.dev-remote.yml`, followed by smoke tests.
2. **Production** -- Pushing a version tag (`v*`) triggers the release workflow: the full test suite runs, a GitHub Release is created with an auto-generated changelog, and the app is deployed to production using `docker-compose.prod.yml`, followed by health checks.

```bash
# Production build (local preview)
docker compose -f docker-compose.prod.yml up -d
# Access at http://localhost:80
```

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on setting up the development environment, branch conventions, testing requirements, and the pull request process.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [PokeAPI](https://pokeapi.co/) -- Pokemon data and sprite images.
- Inspired by daily challenge games like [Wordle](https://www.nytimes.com/games/wordle) and [Pokedoku](https://pokedoku.com/).
