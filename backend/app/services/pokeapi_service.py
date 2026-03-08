import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import PokemonCache


async def get_pokemon(db: AsyncSession, pokemon_id: int) -> PokemonCache:
    """Return cached Pokemon or fetch from PokeAPI and cache it."""
    result = await db.execute(
        select(PokemonCache).where(PokemonCache.pokemon_id == pokemon_id)
    )
    cached = result.scalar_one_or_none()
    if cached:
        return cached

    return await _fetch_and_cache(db, pokemon_id)


async def _fetch_and_cache(db: AsyncSession, pokemon_id: int) -> PokemonCache:
    url = f"{settings.pokeapi_base_url}/pokemon/{pokemon_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10.0)
        resp.raise_for_status()

    data = resp.json()
    pokemon = PokemonCache(
        pokemon_id=data["id"],
        name=data["name"],
        sprite_url=data["sprites"]["front_default"] or "",
        types=[t["type"]["name"] for t in data["types"]],
    )
    db.add(pokemon)
    await db.commit()
    await db.refresh(pokemon)
    return pokemon


async def get_multiple_pokemon(
    db: AsyncSession, pokemon_ids: list[int]
) -> list[PokemonCache]:
    """Fetch multiple Pokemon, using cache where available."""
    result = []
    for pid in pokemon_ids:
        result.append(await get_pokemon(db, pid))
    return result
