import datetime

from pydantic import BaseModel


class PokemonOut(BaseModel):
    pokemon_id: int
    name: str
    sprite_url: str
    types: list[str]


class MatchupOut(BaseModel):
    id: int
    match_date: datetime.date
    pokemon: list[PokemonOut]
    has_voted: bool = False
    user_pick: int | None = None
    results: "ResultsOut | None" = None


class VoteIn(BaseModel):
    matchup_id: int
    pokemon_id: int


class PokemonResult(BaseModel):
    pokemon_id: int
    name: str
    sprite_url: str
    types: list[str]
    vote_count: int
    vote_percentage: float
    is_winner: bool


class ResultsOut(BaseModel):
    matchup_id: int
    total_votes: int
    pokemon: list[PokemonResult]


class HistoryEntry(BaseModel):
    id: int
    match_date: datetime.date
    pokemon: list[PokemonOut]
    winner: PokemonOut | None = None
    total_votes: int
