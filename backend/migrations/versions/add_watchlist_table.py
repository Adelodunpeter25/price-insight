"""Add watchlist table

Revision ID: add_watchlist_001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_watchlist_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('watchlists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('target_price', sa.DECIMAL(precision=10, scale=2), nullable=True),
    sa.Column('alert_on_any_drop', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('alert_on_target', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('notes', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_watchlists_user_id'), 'watchlists', ['user_id'], unique=False)
    op.create_index(op.f('ix_watchlists_product_id'), 'watchlists', ['product_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_watchlists_product_id'), table_name='watchlists')
    op.drop_index(op.f('ix_watchlists_user_id'), table_name='watchlists')
    op.drop_table('watchlists')
