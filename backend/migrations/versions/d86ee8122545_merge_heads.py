"""Merge heads

Revision ID: d86ee8122545
Revises: 8495efcc0d86, add_user_auth
Create Date: 2025-11-07 12:46:21.827977

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd86ee8122545'
down_revision = ('8495efcc0d86', 'add_user_auth')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass