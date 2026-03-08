# Contributing to Daily Starter

Thank you for your interest in contributing. This document covers the development workflow, conventions, and requirements for submitting changes.

---

## Development Environment

All development happens inside Docker containers. You do not need to install Flutter, Python, or any project dependencies on your host machine.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2+)
- [Git](https://git-scm.com/)

### Setup

```bash
git clone https://github.com/StavLobel/fav-pkmn.git
cd fav-pkmn
docker compose up
```

The frontend is available at http://localhost:5173 and the API at http://localhost:8000.

---

## Branch Naming

Create branches from `develop` using the following prefixes:

| Prefix      | Use case                          |
|-------------|-----------------------------------|
| `feature/*` | New features or enhancements      |
| `bugfix/*`  | Bug fixes                         |
| `hotfix/*`  | Urgent fixes for production       |

Examples: `feature/history-page`, `bugfix/duplicate-vote-race-condition`, `hotfix/cookie-secure-flag`.

---

## Commit Messages

Write clear, concise commit messages in the imperative mood.

**Format:**

```
<type>: <short summary>

<optional body explaining why, not what>
```

**Types:**

| Type       | Description                        |
|------------|------------------------------------|
| `feat`     | New feature                        |
| `fix`      | Bug fix                            |
| `refactor` | Code restructuring (no behavior change) |
| `test`     | Adding or updating tests           |
| `docs`     | Documentation changes              |
| `ci`       | CI/CD workflow changes             |
| `chore`    | Build, config, or tooling changes  |

**Examples:**

```
feat: add history page with past matchup results
fix: prevent duplicate vote on rapid double-click
test: add E2E tests for daily reset flow
```

---

## Pull Request Process

1. Create a branch from `develop` following the naming conventions above.
2. Make your changes, ensuring all tests pass.
3. Push your branch and open a pull request targeting `develop`.
4. Fill out the PR template completely.
5. Ensure CI passes (linting, build, widget tests, E2E tests).
6. Request a code review.
7. Address review feedback, then the PR will be merged.

Do not push directly to `main` or `develop`.

---

## Testing Requirements

This project follows a strict **test-driven development** workflow:

1. **Write a failing test first** that captures the expected behavior.
2. **Write the minimum code** to make the test pass.
3. **Refactor** while keeping all tests green.

### Running Tests

```bash
# Frontend widget tests
docker compose --profile test run --rm test-unit

# Full E2E and API test suite
docker compose --profile test run --rm test-e2e

# Tests for a specific SRS requirement
docker compose --profile test run --rm test-e2e pytest -m fr12 -v
```

All tests must pass before a PR can be merged. If you fix a bug, write a failing test that reproduces it before applying the fix.

See [docs/STP.md](docs/STP.md) for the complete test procedure, markers, and fixture reference.

---

## Code Style

### Python

Python code is linted and formatted with [ruff](https://docs.astral.sh/ruff/). Configuration is in `ruff.toml`.

```bash
ruff check backend/
ruff format --check backend/
```

CI will reject PRs that fail ruff checks.

### Dart

Flutter code must pass static analysis:

```bash
docker compose run --rm app flutter analyze
```

Follow the rules defined in `frontend/analysis_options.yaml`.

---

## Questions

If you have questions or need clarification, open a [GitHub Issue](https://github.com/StavLobel/fav-pkmn/issues) before starting work.
