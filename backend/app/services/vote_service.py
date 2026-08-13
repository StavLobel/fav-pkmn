import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DailyMatchup, PokemonCache, Vote
from app.schemas import PokemonResult, ResultsOut


async def submit_vote(
    db: AsyncSession,
    matchup_id: int,
    pokemon_id: int,
    voter_token: uuid.UUID,
) -> ResultsOut:
    """Validate and record a vote, then return aggregated results."""
    matchup = await _get_matchup(db, matchup_id)
    _validate_pokemon_in_matchup(matchup, pokemon_id)

    vote = Vote(
        matchup_id=matchup_id,
        pokemon_id=pokemon_id,
        voter_token=voter_token,
    )
    db.add(vote)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail="Already voted for this matchup"
        ) from None

    pokemon_list = await _get_matchup_pokemon(db, matchup)
    return await get_results(db, matchup, pokemon_list)


async def _get_matchup(db: AsyncSession, matchup_id: int) -> DailyMatchup:
    result = await db.execute(select(DailyMatchup).where(DailyMatchup.id == matchup_id))
    matchup = result.scalar_one_or_none()
    if not matchup:
        raise HTTPException(status_code=404, detail="Matchup not found")
    return matchup


def _validate_pokemon_in_matchup(matchup: DailyMatchup, pokemon_id: int) -> None:
    valid_ids = {matchup.pokemon_1_id, matchup.pokemon_2_id, matchup.pokemon_3_id}
    if pokemon_id not in valid_ids:
        raise HTTPException(
            status_code=400,
            detail="Pokemon does not belong to this matchup",
        )


async def _get_matchup_pokemon(
    db: AsyncSession, matchup: DailyMatchup
) -> list[PokemonCache]:
    ids = [matchup.pokemon_1_id, matchup.pokemon_2_id, matchup.pokemon_3_id]
    result = await db.execute(
        select(PokemonCache).where(PokemonCache.pokemon_id.in_(ids))
    )
    pokemon_map = {p.pokemon_id: p for p in result.scalars().all()}
    return [pokemon_map[pid] for pid in ids]


async def get_results(
    db: AsyncSession,
    matchup: DailyMatchup,
    pokemon_list: list[PokemonCache],
) -> ResultsOut:
    """Aggregate vote counts for a matchup."""
    result = await db.execute(
        select(Vote.pokemon_id, func.count(Vote.id))
        .where(Vote.matchup_id == matchup.id)
        .group_by(Vote.pokemon_id)
    )
    counts = dict(result.all())
    total = sum(counts.values())

    max_count = max(counts.values()) if counts else 0

    pokemon_results = []
    for p in pokemon_list:
        count = counts.get(p.pokemon_id, 0)
        pokemon_results.append(
            PokemonResult(
                pokemon_id=p.pokemon_id,
                name=p.name,
                sprite_url=p.sprite_url,
                types=p.types,
                vote_count=count,
                vote_percentage=round(count / total * 100, 1) if total > 0 else 0.0,
                is_winner=count == max_count and max_count > 0,
            )
        )

    return ResultsOut(
        matchup_id=matchup.id,
        total_votes=total,
        pokemon=pokemon_results,
    )
