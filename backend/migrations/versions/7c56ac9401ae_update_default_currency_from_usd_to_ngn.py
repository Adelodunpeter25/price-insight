"""Update default currency from USD to NGN

Revision ID: 7c56ac9401ae
Revises: d86ee8122545
Create Date: 2025-11-07 12:46:31.863290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c56ac9401ae'
down_revision = 'd86ee8122545'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update default values for currency columns
    op.alter_column('price_history', 'currency', server_default='NGN')
    op.alter_column('flights', 'currency', server_default='NGN')
    op.alter_column('hotels', 'currency', server_default='NGN')
    
    # Update existing USD records to NGN (they should already be converted by scrapers)
    # This is safe because our scrapers now convert all prices to NGN
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE price_history SET currency = 'NGN' WHERE currency = 'USD'"))
    connection.execute(sa.text("UPDATE flights SET currency = 'NGN' WHERE currency = 'USD'"))
    connection.execute(sa.text("UPDATE hotels SET currency = 'NGN' WHERE currency = 'USD'"))


def downgrade() -> None:
    # Revert default values
    op.alter_column('price_history', 'currency', server_default='USD')
    op.alter_column('flights', 'currency', server_default='USD')
    op.alter_column('hotels', 'currency', server_default='USD')
    
    # Revert currency values
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE price_history SET currency = 'USD' WHERE currency = 'NGN'"))
    connection.execute(sa.text("UPDATE flights SET currency = 'USD' WHERE currency = 'NGN'"))
    connection.execute(sa.text("UPDATE hotels SET currency = 'USD' WHERE currency = 'NGN'"))