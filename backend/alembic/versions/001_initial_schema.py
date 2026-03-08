"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-08

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pokemon_cache",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pokemon_id", sa.Integer(), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("sprite_url", sa.String(500), nullable=False),
        sa.Column("types", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "daily_matchups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_date", sa.Date(), nullable=False, unique=True, index=True),
        sa.Column(
            "pokemon_1_id",
            sa.Integer(),
            sa.ForeignKey("pokemon_cache.pokemon_id"),
            nullable=False,
        ),
        sa.Column(
            "pokemon_2_id",
            sa.Integer(),
            sa.ForeignKey("pokemon_cache.pokemon_id"),
            nullable=False,
        ),
        sa.Column(
            "pokemon_3_id",
            sa.Integer(),
            sa.ForeignKey("pokemon_cache.pokemon_id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "pokemon_1_id != pokemon_2_id AND pokemon_2_id != pokemon_3_id AND pokemon_1_id != pokemon_3_id",
            name="ck_unique_pokemon",
        ),
    )

    op.create_table(
        "votes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "matchup_id",
            sa.Integer(),
            sa.ForeignKey("daily_matchups.id"),
            nullable=False,
        ),
        sa.Column("pokemon_id", sa.Integer(), nullable=False),
        sa.Column("voter_token", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("matchup_id", "voter_token", name="uq_one_vote_per_token"),
    )


def downgrade() -> None:
    op.drop_table("votes")
    op.drop_table("daily_matchups")
    op.drop_table("pokemon_cache")
