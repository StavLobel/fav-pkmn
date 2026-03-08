import uuid

from fastapi import APIRouter, Cookie, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ResultsOut, VoteIn
from app.services import vote_service

router = APIRouter()


@router.post("/vote", response_model=ResultsOut)
async def submit_vote(
    vote: VoteIn,
    db: AsyncSession = Depends(get_db),
    voter_token: str | None = Cookie(default=None),
):
    if not voter_token:
        raise HTTPException(status_code=401, detail="No voter token found")

    try:
        token = uuid.UUID(voter_token)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid voter token")

    results = await vote_service.submit_vote(
        db, vote.matchup_id, vote.pokemon_id, token
    )
    return results
