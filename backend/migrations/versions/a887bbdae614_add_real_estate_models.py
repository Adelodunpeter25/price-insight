"""Add real estate models

Revision ID: a887bbdae614
Revises: 7c56ac9401ae
Create Date: 2025-11-07 14:39:01.915797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a887bbdae614'
down_revision = '7c56ac9401ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create properties table
    op.create_table('properties',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('property_type', sa.String(length=50), nullable=False),
    sa.Column('location', sa.String(length=200), nullable=False),
    sa.Column('bedrooms', sa.Integer(), nullable=True),
    sa.Column('bathrooms', sa.Integer(), nullable=True),
    sa.Column('size_sqm', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('price', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('price_per_sqm', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('listing_type', sa.String(length=20), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('agent', sa.String(length=200), nullable=True),
    sa.Column('url', sa.Text(), nullable=False),
    sa.Column('site', sa.String(length=100), nullable=False),
    sa.Column('features', sa.Text(), nullable=True),
    sa.Column('is_tracked', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_properties_location'), 'properties', ['location'], unique=False)
    op.create_index(op.f('ix_properties_price'), 'properties', ['price'], unique=False)
    op.create_index(op.f('ix_properties_property_type'), 'properties', ['property_type'], unique=False)

    # Create property_price_history table
    op.create_table('property_price_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.Column('price', sa.DECIMAL(precision=15, scale=2), nullable=False),
    sa.Column('price_per_sqm', sa.DECIMAL(precision=10, scale=2), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('listing_status', sa.String(length=50), nullable=True),
    sa.Column('source', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_property_price_history_property_id'), 'property_price_history', ['property_id'], unique=False)

    # Create property_deals table
    op.create_table('property_deals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.Column('deal_type', sa.String(length=50), nullable=False),
    sa.Column('discount_percent', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('original_price', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('deal_price', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('deal_start_date', sa.DateTime(), nullable=True),
    sa.Column('deal_end_date', sa.DateTime(), nullable=True),
    sa.Column('deal_source', sa.String(length=100), nullable=True),
    sa.Column('deal_description', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_property_deals_property_id'), 'property_deals', ['property_id'], unique=False)

    # Create property_alert_rules table
    op.create_table('property_alert_rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(length=200), nullable=True),
    sa.Column('property_type', sa.String(length=50), nullable=True),
    sa.Column('max_price', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('min_bedrooms', sa.Integer(), nullable=True),
    sa.Column('rule_type', sa.String(length=50), nullable=False),
    sa.Column('threshold_value', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('percentage_threshold', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('notification_method', sa.String(length=50), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_property_alert_rules_location'), 'property_alert_rules', ['location'], unique=False)
    op.create_index(op.f('ix_property_alert_rules_property_id'), 'property_alert_rules', ['property_id'], unique=False)

    # Create property_alert_history table
    op.create_table('property_alert_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rule_id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=True),
    sa.Column('alert_type', sa.String(length=50), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('triggered_at', sa.DateTime(), nullable=False),
    sa.Column('notification_sent', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
    sa.ForeignKeyConstraint(['rule_id'], ['property_alert_rules.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_property_alert_history_property_id'), 'property_alert_history', ['property_id'], unique=False)
    op.create_index(op.f('ix_property_alert_history_rule_id'), 'property_alert_history', ['rule_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_property_alert_history_rule_id'), table_name='property_alert_history')
    op.drop_index(op.f('ix_property_alert_history_property_id'), table_name='property_alert_history')
    op.drop_table('property_alert_history')
    op.drop_index(op.f('ix_property_alert_rules_property_id'), table_name='property_alert_rules')
    op.drop_index(op.f('ix_property_alert_rules_location'), table_name='property_alert_rules')
    op.drop_table('property_alert_rules')
    op.drop_index(op.f('ix_property_deals_property_id'), table_name='property_deals')
    op.drop_table('property_deals')
    op.drop_index(op.f('ix_property_price_history_property_id'), table_name='property_price_history')
    op.drop_table('property_price_history')
    op.drop_index(op.f('ix_properties_property_type'), table_name='properties')
    op.drop_index(op.f('ix_properties_price'), table_name='properties')
    op.drop_index(op.f('ix_properties_location'), table_name='properties')
    op.drop_table('properties')