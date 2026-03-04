
# Software Requirements Specification (SRS)
## Favorite Pokémon Ranking Application

Version: 1.0  
Date: 2026-03-04

---

# 1. Introduction

## 1.1 Purpose
The purpose of this document is to define the functional and non-functional requirements for the Favorite Pokémon Ranking Application.

The application allows users to determine their favorite Pokémon through an interactive ranking process performed generation by generation. The system stores the user's preferences locally and later runs a global championship to determine the user's overall favorite Pokémon.

## 1.2 Scope
The application is a lightweight web application that allows users to rank Pokémon through quick selections.

The system operates in two main stages:

1. Generation Ranking - Users rank Pokémon within a specific generation and produce a Top 10 list.
2. Global Championship - The system compares the Top 10 Pokémon from each generation to determine the user's overall Top Pokémon.

User progress is stored locally using LocalStorage.

## 1.3 Definitions

| Term | Description |
|-----|-------------|
| Generation | A Pokémon game generation (Gen 1, Gen 2, etc.) |
| Candidate Pool | Subset of Pokémon selected for detailed ranking |
| Elo Rating | Rating system used to rank Pokémon based on pairwise comparisons |
| Championship | Final ranking stage combining Pokémon from all generations |
| LocalStorage | Browser storage used to persist user progress |

---

# 2. Overall Description

## 2.1 Product Perspective
The application is a standalone web application.

It retrieves Pokémon data from PokeAPI.

All user data is stored locally in the browser.

## 2.2 Product Functions

- Rank Pokémon within each generation
- Generate Top 10 per generation
- Store progress locally
- Resume incomplete sessions
- Run global championship ranking
- Display final Top Pokémon

## 2.3 User Characteristics

The intended users are Pokémon fans who want to discover their favorite Pokémon through an interactive ranking process.

No technical knowledge is required.

## 2.4 Constraints

- No backend server required
- Progress stored locally
- Minimal number of user interactions
- Fast loading Pokémon sprites

---

# 3. System Features

## 3.1 Generation Selection

### Functional Requirements

FR-1 The system shall display available Pokémon generations.

FR-2 The system shall allow the user to start ranking a generation.

FR-3 The system shall display completion status for each generation.

FR-4 The system shall allow users to resume incomplete sessions.

---

## 3.2 Generation Ranking Phase A - Discovery

Users select their favorite Pokémon from a set of four.

### Functional Requirements

FR-5 The system shall display four Pokémon from the generation.

FR-6 The user shall select the preferred Pokémon.

FR-7 The system shall record the selection.

FR-8 The system shall repeat this process for a predefined number of selections.

FR-9 The system shall assign scores based on selections.

FR-10 The system shall create a candidate pool.

---

## 3.3 Generation Ranking Phase B - Pairwise Ranking

### Functional Requirements

FR-11 The system shall present two Pokémon from the candidate pool.

FR-12 The user shall select the preferred Pokémon.

FR-13 The system shall update Elo ratings.

FR-14 The system shall repeat comparisons until stability is reached.

FR-15 The system shall generate a Top 10 list.

FR-16 The system shall mark the generation as completed.

---

## 3.4 Championship Stage

### Functional Requirements

FR-17 The system shall collect Top 10 Pokémon from each generation.

FR-18 The system shall create a global candidate pool.

FR-19 The system shall run pairwise comparisons using Elo ranking.

FR-20 The system shall generate a global Top 10.

FR-21 The system shall display the final ranking.

---

## 3.5 Progress Persistence

### Functional Requirements

FR-22 The system shall store progress using LocalStorage.

FR-23 The system shall automatically save progress after each selection.

FR-24 The system shall restore progress when the user returns.

FR-25 The user shall be able to reset stored progress.

---

# 4. Data Storage

## Storage Method

Browser LocalStorage.

## Stored Data

- Completed generations
- Top 10 per generation
- Current ranking state
- Pokémon ratings and scores
- Number of selections

Example structure:

```
favpoke_v1
  gens
  inProgress
  global
```

---

# 5. User Interface Requirements

## Main Screens

### Home Screen

Displays:

- Generation list
- Completion status
- Start Championship button

### Ranking Screen

Displays:

- Pokémon sprites
- Pokémon names
- Selection interface

### Generation Result Screen

Displays:

- Top 10 Pokémon
- Refine ranking option

### Global Result Screen

Displays:

- Final Top 10 Pokémon
- Ranking summary

---

# 6. Non-Functional Requirements

## Performance

- Images load under 1 second
- Selections update instantly
- Application startup under 2 seconds

## Usability

- Minimal interaction required
- Generation ranking completed in under 5 minutes

## Reliability

- Progress must not be lost during normal usage
- System must recover after page reload

## Compatibility

- Support Chrome, Safari, Firefox, Edge
- Support desktop and mobile devices

---

# 7. Future Enhancements

- Global statistics
- Shareable ranking cards
- Friend comparison mode
- Shiny Pokémon mechanic
- Additional ranking modes
