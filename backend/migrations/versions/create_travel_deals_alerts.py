"""Create travel deals and alerts tables

Revision ID: travel_deals_alerts
Revises: c92b6eaecdda
Create Date: 2025-11-07 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'travel_deals_alerts'
down_revision = 'c92b6eaecdda'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create travel_deals table
    op.create_table('travel_deals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flight_id', sa.Integer(), nullable=True),
        sa.Column('hotel_id', sa.Integer(), nullable=True),
        sa.Column('discount_percent', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('original_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('deal_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('deal_start_date', sa.DateTime(), nullable=True),
        sa.Column('deal_end_date', sa.DateTime(), nullable=True),
        sa.Column('deal_source', sa.String(length=100), nullable=False),
        sa.Column('deal_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['flight_id'], ['flights.id'], ),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create travel_alert_rules table
    op.create_table('travel_alert_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flight_id', sa.Integer(), nullable=True),
        sa.Column('hotel_id', sa.Integer(), nullable=True),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('threshold_value', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('percentage_threshold', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('notification_method', sa.String(length=50), nullable=False, default='console'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['flight_id'], ['flights.id'], ),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create travel_alert_history table
    op.create_table('travel_alert_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_rule_id', sa.Integer(), nullable=False),
        sa.Column('flight_id', sa.Integer(), nullable=True),
        sa.Column('hotel_id', sa.Integer(), nullable=True),
        sa.Column('trigger_value', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('message', sa.String(length=500), nullable=False),
        sa.Column('notification_sent', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['alert_rule_id'], ['travel_alert_rules.id'], ),
        sa.ForeignKeyConstraint(['flight_id'], ['flights.id'], ),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('travel_alert_history')
    op.drop_table('travel_alert_rules')
    op.drop_table('travel_deals')