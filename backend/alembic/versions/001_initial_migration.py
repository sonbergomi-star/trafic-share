"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('phone_number', sa.String(length=50), nullable=True),
        sa.Column('balance_usd', sa.Float(), nullable=False, server_default='0'),
        sa.Column('sent_mb', sa.Float(), nullable=False, server_default='0'),
        sa.Column('used_mb', sa.Float(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_banned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index('idx_users_telegram_id', 'users', ['telegram_id'])
    
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('sent_mb', sa.Float(), nullable=False, server_default='0'),
        sa.Column('local_counted_mb', sa.Float(), nullable=False, server_default='0'),
        sa.Column('server_counted_mb', sa.Float(), nullable=False, server_default='0'),
        sa.Column('earned_usd', sa.Float(), nullable=False, server_default='0'),
        sa.Column('last_report_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id'),
        sa.ForeignKeyConstraint(['telegram_id'], ['users.telegram_id'], ondelete='CASCADE')
    )
    op.create_index('idx_sessions_telegram_id', 'sessions', ['telegram_id'])
    op.create_index('idx_sessions_status', 'sessions', ['status'])
    op.create_index('idx_sessions_is_active', 'sessions', ['is_active'])
    
    # Create session_reports table
    op.create_table(
        'session_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('cumulative_mb', sa.Float(), nullable=False),
        sa.Column('delta_mb', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE')
    )
    op.create_index('idx_session_reports_session_id', 'session_reports', ['session_id'])
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('amount_usd', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['telegram_id'], ['users.telegram_id'], ondelete='CASCADE')
    )
    op.create_index('idx_transactions_telegram_id', 'transactions', ['telegram_id'])
    op.create_index('idx_transactions_type', 'transactions', ['type'])
    
    # Create withdraw_requests table
    op.create_table(
        'withdraw_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('amount_usd', sa.Float(), nullable=False),
        sa.Column('amount_usdt', sa.Float(), nullable=False),
        sa.Column('wallet_address', sa.String(length=255), nullable=False),
        sa.Column('network', sa.String(length=50), nullable=False, server_default='BEP20'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('payout_id', sa.String(length=255), nullable=True),
        sa.Column('tx_hash', sa.String(length=255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('admin_note', sa.Text(), nullable=True),
        sa.Column('reserved_balance', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['telegram_id'], ['users.telegram_id'], ondelete='CASCADE')
    )
    op.create_index('idx_withdraw_requests_telegram_id', 'withdraw_requests', ['telegram_id'])
    op.create_index('idx_withdraw_requests_status', 'withdraw_requests', ['status'])
    
    # Create announcements table
    op.create_table(
        'announcements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('link', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create promo_codes table
    op.create_table(
        'promo_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('bonus_percent', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create support_requests table
    op.create_table(
        'support_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('attachment_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='new'),
        sa.Column('admin_reply', sa.Text(), nullable=True),
        sa.Column('admin_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('replied_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['telegram_id'], ['users.telegram_id'], ondelete='CASCADE')
    )
    op.create_index('idx_support_requests_telegram_id', 'support_requests', ['telegram_id'])
    
    # Create app_settings table
    op.create_table(
        'app_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    
    # Create daily_prices table
    op.create_table(
        'daily_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('price_per_gb', sa.Float(), nullable=False),
        sa.Column('price_per_mb', sa.Float(), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('admin_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date')
    )
    
    # Create traffic_logs table
    op.create_table(
        'traffic_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('sent_mb', sa.Float(), nullable=False),
        sa.Column('sold_mb', sa.Float(), nullable=False),
        sa.Column('profit_usd', sa.Float(), nullable=False),
        sa.Column('price_per_mb', sa.Float(), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['telegram_id'], ['users.telegram_id'], ondelete='CASCADE')
    )
    op.create_index('idx_traffic_logs_telegram_id', 'traffic_logs', ['telegram_id'])
    op.create_index('idx_traffic_logs_date', 'traffic_logs', ['date'])
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['telegram_id'], ['users.telegram_id'], ondelete='CASCADE')
    )
    op.create_index('idx_notifications_telegram_id', 'notifications', ['telegram_id'])
    
    # Create fcm_tokens table
    op.create_table(
        'fcm_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('device_info', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['telegram_id'], ['users.telegram_id'], ondelete='CASCADE')
    )
    op.create_index('idx_fcm_tokens_telegram_id', 'fcm_tokens', ['telegram_id'])
    op.create_index('idx_fcm_tokens_token', 'fcm_tokens', ['token'])


def downgrade() -> None:
    op.drop_table('fcm_tokens')
    op.drop_table('notifications')
    op.drop_table('traffic_logs')
    op.drop_table('daily_prices')
    op.drop_table('app_settings')
    op.drop_table('support_requests')
    op.drop_table('promo_codes')
    op.drop_table('announcements')
    op.drop_table('withdraw_requests')
    op.drop_table('transactions')
    op.drop_table('session_reports')
    op.drop_table('sessions')
    op.drop_table('users')
