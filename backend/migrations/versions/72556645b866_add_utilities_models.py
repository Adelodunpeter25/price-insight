"""Add utilities models

Revision ID: 72556645b866
Revises: a887bbdae614
Create Date: 2025-11-07 15:03:25.207821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72556645b866'
down_revision = 'a887bbdae614'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create utility_services table
    op.create_table('utility_services',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('service_type', sa.String(length=50), nullable=False),
    sa.Column('provider', sa.String(length=100), nullable=False),
    sa.Column('billing_type', sa.String(length=20), nullable=False),
    sa.Column('billing_cycle', sa.String(length=20), nullable=True),
    sa.Column('base_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('plan_details', sa.Text(), nullable=True),
    sa.Column('url', sa.Text(), nullable=False),
    sa.Column('site', sa.String(length=100), nullable=False),
    sa.Column('is_tracked', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_utility_services_provider'), 'utility_services', ['provider'], unique=False)
    op.create_index(op.f('ix_utility_services_service_type'), 'utility_services', ['service_type'], unique=False)

    # Create utility_price_history table
    op.create_table('utility_price_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('price', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('tariff_details', sa.String(length=200), nullable=True),
    sa.Column('source', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['utility_services.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_utility_price_history_service_id'), 'utility_price_history', ['service_id'], unique=False)

    # Create utility_deals table
    op.create_table('utility_deals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('deal_type', sa.String(length=50), nullable=False),
    sa.Column('discount_percent', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('original_price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('deal_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('deal_start_date', sa.DateTime(), nullable=True),
    sa.Column('deal_end_date', sa.DateTime(), nullable=True),
    sa.Column('deal_source', sa.String(length=100), nullable=True),
    sa.Column('deal_description', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['utility_services.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_utility_deals_service_id'), 'utility_deals', ['service_id'], unique=False)

    # Create utility_alert_rules table
    op.create_table('utility_alert_rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.Column('service_type', sa.String(length=50), nullable=True),
    sa.Column('provider', sa.String(length=100), nullable=True),
    sa.Column('max_price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('rule_type', sa.String(length=50), nullable=False),
    sa.Column('threshold_value', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('percentage_threshold', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('notification_method', sa.String(length=50), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['utility_services.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_utility_alert_rules_provider'), 'utility_alert_rules', ['provider'], unique=False)
    op.create_index(op.f('ix_utility_alert_rules_service_id'), 'utility_alert_rules', ['service_id'], unique=False)
    op.create_index(op.f('ix_utility_alert_rules_service_type'), 'utility_alert_rules', ['service_type'], unique=False)

    # Create utility_alert_history table
    op.create_table('utility_alert_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rule_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.Column('alert_type', sa.String(length=50), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('triggered_at', sa.DateTime(), nullable=False),
    sa.Column('notification_sent', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['rule_id'], ['utility_alert_rules.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['utility_services.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_utility_alert_history_rule_id'), 'utility_alert_history', ['rule_id'], unique=False)
    op.create_index(op.f('ix_utility_alert_history_service_id'), 'utility_alert_history', ['service_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_utility_alert_history_service_id'), table_name='utility_alert_history')
    op.drop_index(op.f('ix_utility_alert_history_rule_id'), table_name='utility_alert_history')
    op.drop_table('utility_alert_history')
    op.drop_index(op.f('ix_utility_alert_rules_service_type'), table_name='utility_alert_rules')
    op.drop_index(op.f('ix_utility_alert_rules_service_id'), table_name='utility_alert_rules')
    op.drop_index(op.f('ix_utility_alert_rules_provider'), table_name='utility_alert_rules')
    op.drop_table('utility_alert_rules')
    op.drop_index(op.f('ix_utility_deals_service_id'), table_name='utility_deals')
    op.drop_table('utility_deals')
    op.drop_index(op.f('ix_utility_price_history_service_id'), table_name='utility_price_history')
    op.drop_table('utility_price_history')
    op.drop_index(op.f('ix_utility_services_service_type'), table_name='utility_services')
    op.drop_index(op.f('ix_utility_services_provider'), table_name='utility_services')
    op.drop_table('utility_services')