import datetime
import uuid

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class PokemonCache(Base):
    __tablename__ = "pokemon_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    pokemon_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sprite_url: Mapped[str] = mapped_column(String(500), nullable=False)
    types: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DailyMatchup(Base):
    __tablename__ = "daily_matchups"
    __table_args__ = (
        CheckConstraint(
            "pokemon_1_id != pokemon_2_id AND pokemon_2_id != pokemon_3_id AND pokemon_1_id != pokemon_3_id",
            name="ck_unique_pokemon",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    match_date: Mapped[datetime.date] = mapped_column(Date, unique=True, nullable=False, index=True)
    pokemon_1_id: Mapped[int] = mapped_column(Integer, ForeignKey("pokemon_cache.pokemon_id"), nullable=False)
    pokemon_2_id: Mapped[int] = mapped_column(Integer, ForeignKey("pokemon_cache.pokemon_id"), nullable=False)
    pokemon_3_id: Mapped[int] = mapped_column(Integer, ForeignKey("pokemon_cache.pokemon_id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    pokemon_1: Mapped["PokemonCache"] = relationship(foreign_keys=[pokemon_1_id])
    pokemon_2: Mapped["PokemonCache"] = relationship(foreign_keys=[pokemon_2_id])
    pokemon_3: Mapped["PokemonCache"] = relationship(foreign_keys=[pokemon_3_id])
    votes: Mapped[list["Vote"]] = relationship(back_populates="matchup")


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("matchup_id", "voter_token", name="uq_one_vote_per_token"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    matchup_id: Mapped[int] = mapped_column(Integer, ForeignKey("daily_matchups.id"), nullable=False)
    pokemon_id: Mapped[int] = mapped_column(Integer, nullable=False)
    voter_token: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    matchup: Mapped["DailyMatchup"] = relationship(back_populates="votes")
