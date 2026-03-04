# Favorite Pokemon Ranking Application

## Tech Stack

- **React 19** with **Vite** (JavaScript, no TypeScript)
- **Tailwind CSS v4** for styling
- **React Router v7** for page navigation
- **PokeAPI** (`https://pokeapi.co/api/v2/`) for Pokemon data and sprites
- **LocalStorage** for persistence (no backend)
- **Docker** for containerized development and production

## Docker Setup

### Project Root Files

```
Dockerfile            # Multi-stage build (dev + prod targets)
docker-compose.yml    # Dev environment with hot-reload
.dockerignore         # Exclude node_modules, dist, .git, etc.
```

### Dockerfile (multi-stage)

- **Dev target** (`docker build --target dev`): Node 22 Alpine, installs deps, runs `vite dev` with `--host 0.0.0.0` so the dev server is reachable from outside the container.
- **Prod target** (`docker build --target prod`): Two-stage build -- first stage builds the app with `vite build`, second stage serves the `dist/` folder via **nginx** (Alpine) on port 80.

### docker-compose.yml (development)

```yaml
services:
  app:
    build:
      context: .
      target: dev
    ports:
      - "5173:5173"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
```

Key points:

- Bind-mount the project root so source changes trigger Vite HMR instantly
- Anonymous volume for `node_modules` prevents host OS overriding container deps
- Port 5173 exposed for browser access at `http://localhost:5173`

### .dockerignore

```
node_modules
dist
.git
.gitignore
*.md
```

### Vite Config Adjustment

Vite must listen on `0.0.0.0` inside Docker. In `vite.config.js`:

```js
server: {
  host: '0.0.0.0',
  port: 5173,
  watch: { usePolling: true }
}
```

`usePolling` ensures file-watch works reliably with Docker bind mounts on macOS.

### Workflow

- **Dev**: `docker compose up` -- starts the app with hot-reload on `http://localhost:5173`
- **Prod**: `docker build -t fav-pkmn . && docker run -p 8080:80 fav-pkmn` -- serves optimized build via nginx on `http://localhost:8080`

## Project Structure

```
src/
  components/         # Reusable UI components
    PokemonCard.jsx   # Displays sprite + name, clickable
    GenerationCard.jsx# Shows gen info + completion status
    TopList.jsx       # Renders a ranked Top 10 list
    ProgressBar.jsx   # Visual progress indicator
  pages/              # Route-level screens
    HomePage.jsx      # Generation list + championship button
    RankingPage.jsx   # Handles both Phase A and Phase B
    ResultPage.jsx    # Generation Top 10 result
    ChampionshipPage.jsx  # Global championship ranking
    GlobalResultPage.jsx  # Final Top 10 display
  hooks/
    useLocalStorage.js  # Read/write/reset LocalStorage state
    usePokemon.js       # Fetch + cache Pokemon data from PokeAPI
  utils/
    elo.js            # Elo rating calculation
    generations.js    # Generation ID ranges + metadata
    ranking.js        # Discovery scoring + candidate pool logic
    storage.js        # LocalStorage schema + helpers
  App.jsx             # Router setup
  main.jsx            # Entry point
```

## Generation Data

A static config mapping each generation to its Pokemon ID range:

| Gen | Name   | IDs      |
| --- | ------ | -------- |
| 1   | Kanto  | 1-151    |
| 2   | Johto  | 152-251  |
| 3   | Hoenn  | 252-386  |
| 4   | Sinnoh | 387-493  |
| 5   | Unova  | 494-649  |
| 6   | Kalos  | 650-721  |
| 7   | Alola  | 722-809  |
| 8   | Galar  | 810-905  |
| 9   | Paldea | 906-1025 |

Defined in `src/utils/generations.js` as an array of objects with `{ id, name, startId, endId }`.

## Core Algorithm

### Phase A - Discovery (`src/utils/ranking.js`)

- Shuffle all Pokemon in the generation
- Group them into sets of 4
- Present each group; the user picks 1 favorite
- Track a score for each Pokemon (selected = +1)
- After all groups are shown, take the top ~30 Pokemon by score as the **candidate pool**
- For smaller generations, adjust candidate pool size proportionally (e.g., top 20% of gen size, minimum 20, capped at 30)

### Phase B - Pairwise Elo Ranking (`src/utils/elo.js`)

- All candidates start with Elo rating 1500
- Present two Pokemon; user picks the winner
- Update ratings using standard Elo formula: `newRating = oldRating + K * (result - expected)` with K=32
- **Matchmaking**: Prioritize pairing Pokemon with similar ratings and fewest comparisons
- **Stability detection**: Track rating changes over the last N rounds; stop when average change drops below a threshold (e.g., < 2 points per match over last 10 matches), or after a maximum number of comparisons (e.g., `candidatePoolSize * 5`)
- Sort by final Elo rating; extract **Top 10**

### Championship (`src/pages/ChampionshipPage.jsx`)

- Collect Top 10 from every completed generation (up to 90 Pokemon)
- Run Phase B (pairwise Elo) on the combined pool
- Produce the global **Top 10**

## LocalStorage Schema (`src/utils/storage.js`)

Key: `favpoke_v1`

```json
{
  "gens": {
    "1": {
      "status": "completed",
      "top10": [{ "id": 25, "name": "pikachu", "rating": 1620 }],
      "candidatePool": []
    },
    "2": {
      "status": "in_progress",
      "phase": "discovery",
      "currentIndex": 12,
      "scores": { "152": 1, "155": 0 },
      "groups": [[152,153,154,155]],
      "candidatePool": null,
      "ratings": null
    }
  },
  "global": {
    "status": "not_started",
    "top10": null
  }
}
```

## Screens and Routing

- `/` -- **HomePage**: Grid of generation cards showing name, sprite preview, and status badge (not started / in progress / completed). "Start Championship" button appears when all gens are completed.
- `/rank/:genId` -- **RankingPage**: Renders Phase A (pick 1 of 4) or Phase B (pick 1 of 2) based on current state. Shows progress bar. Auto-saves after every selection.
- `/result/:genId` -- **ResultPage**: Displays the Top 10 for a generation with sprites, names, and ranks. "Back to Home" and "Refine Ranking" buttons.
- `/championship` -- **ChampionshipPage**: Pairwise Elo comparisons across all generations' Top 10s.
- `/championship/result` -- **GlobalResultPage**: Final Top 10 with sprites, names, ranks, and a summary.

## PokeAPI Integration (`src/hooks/usePokemon.js`)

- Fetch Pokemon by ID: `https://pokeapi.co/api/v2/pokemon/{id}`
- Extract `name` and `sprites.front_default` (or `sprites.other['official-artwork'].front_default` for higher quality)
- Cache fetched data in a React context or in-memory map to avoid redundant requests
- Batch-prefetch upcoming Pokemon (e.g., next group of 4) for snappy UX
- Use sprite URL shortcut where possible: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png` to avoid full API calls just for images

## UI/UX Design Notes

- Pokemon-inspired color palette (reds, blues, yellows) with Tailwind custom theme
- Cards use hover/press animations for satisfying interactions
- Mobile-first responsive layout (cards stack vertically on small screens, grid on desktop)
- Transition animations between selections for smooth flow
- Generation cards show a small sprite collage or representative starter Pokemon
- Progress bar during ranking phases shows how many comparisons remain (approximate for Phase B)
- Reset button on the home page with a confirmation dialog

## Future Enhancements

The following features from the SRS (Section 7) are deferred to future iterations:

- **Shiny Pokemon mechanic**: During ranking, a Pokemon has a small random chance (e.g., 1/20) of appearing with its shiny sprite instead of the default. Purely cosmetic -- does not affect ranking logic. Implementation would use PokeAPI's `sprites.front_shiny` URL.
- **Global statistics**: Aggregate ranking data across users.
- **Shareable ranking cards**: Generate an image/card of the user's Top 10 to share on social media.
- **Friend comparison mode**: Compare rankings between friends.
- **Additional ranking modes**: Alternative ranking algorithms or formats.

## Key Implementation Details

- **No backend**: Everything runs client-side. PokeAPI is the only external dependency.
- **Auto-save**: Every user selection triggers a LocalStorage write via `useLocalStorage` hook.
- **Resilience**: On page load, check LocalStorage and restore state. If data is corrupted, offer a reset.
- **Performance**: Use sprite URL shortcut to avoid full API calls. Lazy-load images. Keep bundle small.
