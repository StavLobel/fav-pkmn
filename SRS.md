# PokePick - Software Requirements Specification (SRS)

## 1. System Overview

PokePick is a web application that presents users with a daily Pokémon voting challenge.

Each day, the system selects three Pokémon at random and presents them to all users as a shared daily matchup. Users vote for their favorite Pokémon among the three options. After voting, the user immediately sees the aggregated results for that day's matchup.

The application behaves similarly to daily challenge games such as Wordle or Pokedoku, where each user can participate once per day.

The system does not require user accounts. Instead, anonymous browser identification is used to enforce one vote per browser per day.

Sprites and Pokémon metadata are sourced from the PokeAPI.

---

# 2. Functional Requirements

## 2.1 Daily Matchup Generation

FR-1  
The system shall generate one daily matchup containing exactly three unique Pokémon.

FR-2  
The system shall ensure the same daily matchup is presented to all users on the same calendar day.

FR-3  
The system shall store each daily matchup in the database with its associated date.

FR-4  
The system shall prevent more than one matchup from being created for the same date.

FR-5  
The system shall ensure the three Pokémon in a matchup are unique.

FR-6  
The system shall retrieve Pokémon metadata (name, sprite, types) from PokeAPI when a Pokémon is first used.

FR-7  
The system shall cache Pokémon metadata locally to reduce external API calls.

---

## 2.2 Daily Challenge Display

FR-8  
The system shall display the current day’s matchup when a user visits the application.

FR-9  
The system shall display for each Pokémon:
- name
- sprite image
- optional type icons

FR-10  
The system shall present the three Pokémon as selectable options.

FR-11  
The system shall indicate whether the user has already completed today's challenge.

---

## 2.3 Voting

FR-12  
The system shall allow the user to select exactly one Pokémon from the three options.

FR-13  
The system shall submit the vote to the backend server.

FR-14  
The system shall verify that the selected Pokémon belongs to the current daily matchup.

FR-15  
The system shall allow only one vote per browser identity per daily matchup.

FR-16  
The system shall store each vote in the database.

FR-17  
The system shall associate each vote with:
- daily matchup
- selected Pokémon
- anonymous browser token
- timestamp

FR-18  
The system shall reject a vote if the browser identity has already voted for that matchup.

---

## 2.4 Anonymous Identity

FR-19  
The system shall generate a random anonymous voter token for each browser.

FR-20  
The system shall store the token in a browser cookie.

FR-21  
The system shall include the token when submitting a vote.

FR-22  
The system shall enforce uniqueness of votes using the combination of:
- daily_matchup_id
- voter_token.

---

## 2.5 Results Display

FR-23  
The system shall display the voting results immediately after the user submits a vote.

FR-24  
The system shall display:
- vote counts for each Pokémon
- vote percentages
- total vote count.

FR-25  
The system shall highlight the Pokémon selected by the user.

FR-26  
The system shall indicate the current winner.

FR-27  
The system shall handle ties between Pokémon.

FR-28  
If the user revisits the app after already voting, the system shall show the results instead of the voting interface.

---

## 2.6 Daily Reset

FR-29  
The system shall reset the challenge once per calendar day.

FR-30  
The system shall unlock a new matchup automatically after the daily reset.

FR-31  
The system shall determine the reset time using the configured application timezone.

FR-32  
The system shall allow users to participate in the new challenge after reset.

---

## 2.7 History

FR-33  
The system shall store historical matchups.

FR-34  
The system shall allow retrieval of previous matchups and results.

FR-35  
The system shall display the winning Pokémon for past days.

---

# 3. Non-Functional Requirements

## 3.1 Performance

NFR-1  
The application shall load the daily matchup within 2 seconds under normal conditions.

NFR-2  
The voting endpoint shall respond within 500 milliseconds under normal load.

---

## 3.2 Scalability

NFR-3  
The system shall support at least 10,000 daily votes without performance degradation.

NFR-4  
The database schema shall support horizontal scaling if required.

---

## 3.3 Reliability

NFR-5  
The system shall ensure data consistency when storing votes.

NFR-6  
The system shall enforce database constraints to prevent duplicate votes.

---

## 3.4 Security

NFR-7  
The system shall use secure cookies for storing anonymous tokens.

NFR-8  
Cookies shall use the following properties:
- HttpOnly
- Secure
- SameSite=Lax.

NFR-9  
The system shall validate all incoming requests.

NFR-10  
The system shall reject malformed vote submissions.

---

## 3.5 Availability

NFR-11  
The system shall be available 24 hours per day.

NFR-12  
The system shall recover gracefully if the PokeAPI is temporarily unavailable by using cached Pokémon data.

---

## 3.6 Maintainability

NFR-13  
The system shall follow modular architecture principles.

NFR-14  
The backend codebase shall follow SOLID principles.

NFR-15  
The system shall separate API, business logic, and persistence layers.

---

# 4. Technical Requirements

## 4.1 Backend

Recommended backend framework:

FastAPI (Python)

Responsibilities:
- daily matchup generation
- vote submission
- results aggregation
- Pokémon metadata caching
- anonymous token validation

---

## 4.2 Frontend

Recommended frontend options:

React / Next.js  
or  
Flutter Web

Responsibilities:
- displaying the daily trio
- submitting votes
- displaying results
- handling completion state

---

## 4.3 Database

Recommended database:

PostgreSQL

Tables required:

pokemon_cache  
daily_matchups  
votes

---

## 4.4 External APIs

PokeAPI will be used for Pokémon metadata.

Required fields:
- Pokémon ID
- name
- sprite
- types

---

## 4.5 Scheduled Tasks

A scheduled job shall run once per day to generate the next matchup.

Possible implementations:
- server cron job
- background worker
- scheduled cloud function

---

# 5. Constraints

C-1  
The system shall not require user accounts.

C-2  
The system shall rely on anonymous browser cookies for vote identification.

C-3  
The system shall minimize external API calls by caching Pokémon data.

C-4  
The system shall ensure that daily matchups are consistent across all users.

---

# 6. Assumptions

A-1  
Users access the application through modern web browsers.

A-2  
Cookies are enabled in the user’s browser.

A-3  
Pokémon data retrieved from PokeAPI remains stable.

---

# 7. Future Enhancements (Out of Scope for MVP)

- Global leaderboard of most popular Pokémon
- Generation filters
- Special event days
- Shiny Pokémon events
- Social sharing
- Regional leaderboards

---

# 8. User Flows

## 8.1 First Visit - Before Voting

1. The user opens the PokePick application.
2. The system checks for the presence of an anonymous voter token cookie.
3. If the cookie does not exist, the system generates a new anonymous voter token and stores it in a secure cookie.
4. The system retrieves the daily matchup for the current date.
5. The system checks whether the current anonymous voter token has already submitted a vote for the current daily matchup.
6. If the user has not voted yet, the system displays the three Pokémon for the day.
7. The user views the Pokémon cards and selects one Pokémon as their favorite.

Expected outcome:
The user sees the current daily trio and is able to vote.

---

## 8.2 Successful Vote Submission

1. The user selects one Pokémon from the three displayed options.
2. The frontend sends the selected Pokémon and current matchup ID to the backend.
3. The backend validates that:
   - the matchup exists
   - the selected Pokémon belongs to the matchup
   - the anonymous voter token exists
   - the token has not already voted for the matchup
4. The backend stores the vote in the database.
5. The backend aggregates the updated results for the matchup.
6. The system returns the results to the frontend.
7. The frontend displays the results screen.

Expected outcome:
The vote is recorded successfully and results are displayed.

---

## 8.3 Revisiting the App After Voting on the Same Day

1. The user opens the application again later on the same day.
2. The system reads the anonymous voter token from the cookie.
3. The system retrieves the current daily matchup.
4. The system checks whether the token has already voted for that matchup.
5. The system finds an existing vote.
6. The voting interface is skipped.
7. The results screen is displayed.

Expected outcome:
The user cannot vote again on the same day and sees the results.

---

## 8.4 Attempted Duplicate Vote

1. The user attempts to submit another vote.
2. The backend checks the votes table for an existing vote with the same:
   - daily_matchup_id
   - voter_token
3. A duplicate vote is detected.
4. The backend rejects the request.

Expected outcome:
The duplicate vote is not stored.

---

## 8.5 New Day Unlock

1. A new calendar day begins according to the configured timezone.
2. The scheduled job generates a new daily matchup.
3. The user opens the application.
4. The system retrieves the new matchup.
5. The system checks if the user has voted today.
6. No vote is found.
7. The system displays the new trio.

Expected outcome:
The user can participate in the new daily challenge.

---

## 8.6 Viewing Historical Results

1. The user navigates to the history section.
2. The system retrieves past daily matchups.
3. The system retrieves vote results for each matchup.
4. The system displays previous dates, Pokémon trios, and winners.

Expected outcome:
The user can browse historical daily matchups.