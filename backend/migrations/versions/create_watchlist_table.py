"""Create watchlist table

Revision ID: create_watchlist_001
Revises: add_watchlist_001
Create Date: 2025-01-20 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'create_watchlist_001'
down_revision = 'add_watchlist_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'watchlists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('target_price', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('alert_on_any_drop', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('alert_on_target', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='watchlists_user_id_fkey'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='watchlists_product_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='watchlists_pkey')
    )
    
    op.create_index('idx_watchlists_user_product', 'watchlists', ['user_id', 'product_id'])
    op.create_index('idx_watchlists_user_id', 'watchlists', ['user_id'])
    op.create_index('idx_watchlists_product_id', 'watchlists', ['product_id'])


def downgrade() -> None:
    op.drop_index('idx_watchlists_product_id', table_name='watchlists')
    op.drop_index('idx_watchlists_user_id', table_name='watchlists')
    op.drop_index('idx_watchlists_user_product', table_name='watchlists')
    op.drop_table('watchlists')
