# Agent Tools Reference
## Favorite Pokemon Ranking Application

This document catalogs the MCP servers, agent skills, and Cursor rules relevant to this project, along with guidance on when and how to use each.

---

# 1. MCP Servers

## 1.1 Relevant to This Project

### context7 (Documentation Lookup)

**Purpose**: Retrieves up-to-date documentation and code examples for any library via the Context7 API.

**Tools**:
- `resolve-library-id` -- Resolves a library name to a Context7-compatible ID
- `query-docs` -- Fetches documentation and code examples for a given library ID + query

**When to use**:
- Looking up React 19 API details (hooks, component patterns, new features)
- Checking Vite configuration options (server, build, plugins)
- Referencing Tailwind CSS v4 utility classes or config changes
- Verifying React Router v7 routing API (loaders, actions, route config)
- Reviewing Vitest assertion API, mocking, and configuration
- Looking up Playwright selectors, assertions, and fixtures for pytest-playwright
- Checking pytest markers, fixtures, and parametrize syntax

**Relevant library lookups for this project**:
- `react` -- Component API, hooks, rendering
- `vite` -- Dev server config, build options, plugins
- `tailwindcss` -- Utility classes, theme customization, v4 changes
- `react-router` -- Route definitions, useParams, useNavigate, loaders
- `vitest` -- Test runner config, assertions, mocking
- `playwright` -- Browser automation selectors, page interactions
- `pytest` -- Fixtures, markers, parametrize, conftest patterns

### fetch (URL Fetching)

**Purpose**: Fetches any URL from the internet and returns contents as markdown.

**Tools**:
- `fetch` -- Fetches a URL with optional max_length and start_index for pagination

**When to use**:
- Fetching PokeAPI documentation at `https://pokeapi.co/docs/v2`
- Testing PokeAPI endpoints directly (e.g., `https://pokeapi.co/api/v2/pokemon/25`)
- Verifying sprite URL patterns and availability
- Reading external library changelogs or migration guides

### sequential-thinking (Problem Solving)

**Purpose**: Structured, multi-step reasoning tool for breaking down complex problems.

**Tools**:
- `sequentialthinking` -- Step-by-step thinking with branching, revision, and hypothesis verification

**When to use**:
- Designing the Elo rating algorithm and tuning K-factor
- Working out stability detection thresholds and matchmaking logic
- Planning the candidate pool sizing formula (min 20, max 30, proportional)
- Debugging complex state management issues in ranking flow
- Reasoning about edge cases in LocalStorage persistence and recovery

### filesystem (File Operations)

**Purpose**: Read, write, search, and manage files and directories.

**Tools**:
- `read_file`, `read_multiple_files`, `read_text_file` -- Read file contents
- `write_file`, `edit_file` -- Write and edit files
- `create_directory`, `list_directory`, `directory_tree` -- Directory operations
- `search_files` -- Search for patterns in files
- `move_file`, `get_file_info`, `list_directory_with_sizes` -- File management

**When to use**:
- Bulk file operations during scaffolding
- Searching across test files for pattern consistency
- Inspecting directory structure for completeness

## 1.2 Not Relevant to This Project

### kubernetes

Not applicable. This project uses Docker Compose only, no Kubernetes orchestration.

### MaaS Confluence

Not applicable. No Confluence wiki integration needed for this project.

### markitdown

No tools registered. Not usable in current configuration.

---

# 2. Agent Skills

## 2.1 Available Built-in Skills

### create-rule

**Path**: `~/.cursor/skills-cursor/create-rule/SKILL.md`

**Purpose**: Creates `.mdc` rule files in `.cursor/rules/` for persistent AI guidance.

**When to use**: To establish project conventions that the AI agent should always follow. Recommended rules for this project:

- **react-patterns.mdc** (`globs: **/*.jsx`) -- Functional components only, custom hooks for reusable logic, named exports
- **tdd-workflow.mdc** (`alwaysApply: true`) -- Always write tests before implementation, red-green-refactor cycle
- **tailwind-conventions.mdc** (`globs: **/*.jsx`) -- Mobile-first responsive classes, project color palette, no inline styles
- **testing-conventions.mdc** (`globs: **/*.test.*`) -- Vitest for unit/component tests, naming conventions, mock patterns
- **pytest-conventions.mdc** (`globs: tests/**/*.py`) -- Marker usage, fixture patterns, class-based test organization

### create-skill

**Path**: `~/.cursor/skills-cursor/create-skill/SKILL.md`

**Purpose**: Guides creation of new Agent Skills (SKILL.md files) for Cursor.

**When to use**: To create project-specific skills if recurring workflows emerge during development, such as a PokeAPI integration skill or a ranking algorithm debugging skill.

## 2.2 Installable Curated Skills (via skill-installer)

The following curated skills from the [openai/skills](https://github.com/openai/skills) repository are relevant:

### playwright (Recommended -- Install)

**Purpose**: Specialized guidance for writing Playwright tests.

**Relevance**: Directly supports the E2E pytest + Playwright testing layer defined in the STP. Provides patterns for selectors, assertions, page interactions, and test structure.

**Install**:
```bash
# Via skill-installer
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo openai/skills --path skills/.curated/playwright
```

### screenshot (Optional)

**Purpose**: Take and analyze screenshots.

**Relevance**: Useful for visual regression testing of the Pokemon ranking UI during development. Could capture and compare UI states across viewports.

### security-best-practices (Optional)

**Purpose**: Security review and best practices.

**Relevance**: Lightweight review of LocalStorage usage, PokeAPI calls, and general frontend security (XSS prevention, CSP headers in nginx config).

### Not Relevant

The following curated skills are not needed for this project:
- `chatgpt-apps`, `cloudflare-deploy`, `figma`, `figma-implement-design`, `jupyter-notebook`, `linear`, `netlify-deploy`, `notion-*`, `openai-docs`, `pdf`, `render-deploy`, `sentry`, `sora`, `speech`, `spreadsheet`, `transcribe`, `vercel-deploy`, `yeet`, `gh-address-comments`, `gh-fix-ci`, `doc`, `imagegen`, `develop-web-game`

---

# 3. Recommended Cursor Rules

The following `.cursor/rules/` files should be created to maintain consistency throughout development.

### tdd-workflow.mdc

```
alwaysApply: true
```

Enforce TDD red-green-refactor. Always write a failing test before writing implementation code. Reference the STP for test IDs and markers.

### react-conventions.mdc

```
globs: src/**/*.jsx
```

Functional components with hooks. Named exports. Props destructured in signature. Custom hooks in `src/hooks/`. No class components.

### pytest-e2e.mdc

```
globs: tests/**/*.py
```

Use `@pytest.mark.<fr_id>` markers on every test. Class-based test grouping. Use fixtures from conftest.py. Docstrings reference SRS requirement IDs.

### docker-workflow.mdc

```
alwaysApply: true
```

All commands run inside Docker containers. Use `docker compose` for dev and test workflows. Never install dependencies on the host directly.

---

# 4. Usage During Development

## Typical Workflow Integration

```
Developer Task                    Tool to Use
------------------------------    ------------------------------------------
Look up React hook API            context7: resolve-library-id + query-docs
Check Tailwind class names        context7: query-docs with tailwindcss
Test a PokeAPI endpoint           fetch: hit the endpoint directly
Design Elo algorithm              sequential-thinking: multi-step reasoning
Write Playwright E2E tests        context7 (playwright docs) + playwright skill
Set up project conventions        create-rule skill
Verify Docker config syntax       context7: query-docs with docker/vite
Debug complex ranking state       sequential-thinking: step-by-step analysis
```
