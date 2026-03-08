import datetime
import random
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models import DailyMatchup, PokemonCache, Vote
from app.services.pokeapi_service import get_multiple_pokemon


def _today() -> datetime.date:
    return datetime.datetime.now(datetime.timezone.utc).date()


async def get_or_create_today(
    db: AsyncSession,
    override_date: datetime.date | None = None,
) -> DailyMatchup:
    """Return today's matchup, creating it lazily if it doesn't exist."""
    today = override_date or _today()
    matchup = await _get_by_date(db, today)
    if matchup:
        return matchup

    return await _create_matchup(db, today)


async def _get_by_date(db: AsyncSession, date: datetime.date) -> DailyMatchup | None:
    result = await db.execute(
        select(DailyMatchup).where(DailyMatchup.match_date == date)
    )
    return result.scalar_one_or_none()


async def _create_matchup(
    db: AsyncSession, date: datetime.date
) -> DailyMatchup:
    pokemon_ids = random.sample(range(1, settings.max_pokemon_id + 1), 3)
    await get_multiple_pokemon(db, pokemon_ids)

    matchup = DailyMatchup(
        match_date=date,
        pokemon_1_id=pokemon_ids[0],
        pokemon_2_id=pokemon_ids[1],
        pokemon_3_id=pokemon_ids[2],
    )
    db.add(matchup)
    try:
        await db.commit()
        await db.refresh(matchup)
    except IntegrityError:
        await db.rollback()
        matchup = await _get_by_date(db, date)
        if matchup is None:
            raise
    return matchup


async def get_matchup_with_pokemon(
    db: AsyncSession, matchup: DailyMatchup
) -> list[PokemonCache]:
    """Load the three Pokemon for a matchup."""
    ids = [matchup.pokemon_1_id, matchup.pokemon_2_id, matchup.pokemon_3_id]
    result = await db.execute(
        select(PokemonCache).where(PokemonCache.pokemon_id.in_(ids))
    )
    pokemon_map = {p.pokemon_id: p for p in result.scalars().all()}
    return [pokemon_map[pid] for pid in ids]


async def check_has_voted(
    db: AsyncSession, matchup_id: int, voter_token: uuid.UUID
) -> int | None:
    """Return the pokemon_id the user voted for, or None."""
    result = await db.execute(
        select(Vote.pokemon_id).where(
            Vote.matchup_id == matchup_id,
            Vote.voter_token == voter_token,
        )
    )
    return result.scalar_one_or_none()
