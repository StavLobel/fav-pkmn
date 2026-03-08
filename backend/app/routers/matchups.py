import uuid

from fastapi import APIRouter, Cookie, Depends, Query, Response
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import DailyMatchup, PokemonCache, Vote
from app.schemas import HistoryEntry, MatchupOut, PokemonOut
from app.services import matchup_service, vote_service

router = APIRouter()


@router.get("/matchup/today", response_model=MatchupOut)
async def get_today_matchup(
    response: Response,
    db: AsyncSession = Depends(get_db),
    voter_token: str | None = Cookie(default=None),
):
    token = uuid.UUID(voter_token) if voter_token else uuid.uuid4()

    if not voter_token:
        response.set_cookie(
            key="voter_token",
            value=str(token),
            httponly=True,
            samesite="lax",
            max_age=365 * 24 * 60 * 60,
        )

    matchup = await matchup_service.get_or_create_today(db)
    pokemon_list = await matchup_service.get_matchup_with_pokemon(db, matchup)

    pokemon_out = [
        PokemonOut(
            pokemon_id=p.pokemon_id,
            name=p.name,
            sprite_url=p.sprite_url,
            types=p.types,
        )
        for p in pokemon_list
    ]

    user_pick = await matchup_service.check_has_voted(db, matchup.id, token)
    has_voted = user_pick is not None

    results = None
    if has_voted:
        results = await vote_service.get_results(db, matchup, pokemon_list)

    return MatchupOut(
        id=matchup.id,
        match_date=matchup.match_date,
        pokemon=pokemon_out,
        has_voted=has_voted,
        user_pick=user_pick,
        results=results,
    )


@router.get("/history", response_model=list[HistoryEntry])
async def get_history(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=30, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = await db.execute(
        select(DailyMatchup)
        .order_by(desc(DailyMatchup.match_date))
        .limit(limit)
        .offset(offset)
    )
    matchups = result.scalars().all()

    entries = []
    for m in matchups:
        pokemon_list = await matchup_service.get_matchup_with_pokemon(db, m)
        pokemon_out = [
            PokemonOut(
                pokemon_id=p.pokemon_id,
                name=p.name,
                sprite_url=p.sprite_url,
                types=p.types,
            )
            for p in pokemon_list
        ]

        vote_counts = await db.execute(
            select(Vote.pokemon_id, func.count(Vote.id))
            .where(Vote.matchup_id == m.id)
            .group_by(Vote.pokemon_id)
        )
        counts = dict(vote_counts.all())
        total = sum(counts.values())

        winner = None
        if counts:
            winner_id = max(counts, key=counts.get)
            max_count = counts[winner_id]
            tied = sum(1 for c in counts.values() if c == max_count) > 1
            if not tied:
                wp = next(p for p in pokemon_list if p.pokemon_id == winner_id)
                winner = PokemonOut(
                    pokemon_id=wp.pokemon_id,
                    name=wp.name,
                    sprite_url=wp.sprite_url,
                    types=wp.types,
                )

        entries.append(
            HistoryEntry(
                id=m.id,
                match_date=m.match_date,
                pokemon=pokemon_out,
                winner=winner,
                total_votes=total,
            )
        )

    return entries
