"""Initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-11-02 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True, index=True),
        sa.Column("username", sa.String(length=255)),
        sa.Column("first_name", sa.String(length=255)),
        sa.Column("photo_url", sa.Text()),
        sa.Column("auth_date", sa.DateTime()),
        sa.Column("jwt_token", sa.Text()),
        sa.Column("balance_usd", sa.Numeric(18, 6), server_default="0"),
        sa.Column("sent_mb", sa.Float(), server_default="0"),
        sa.Column("used_mb", sa.Float(), server_default="0"),
        sa.Column("device_token", sa.String(length=255)),
        sa.Column("notifications_enabled", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("last_seen", sa.DateTime()),
        sa.Column("role", sa.String(length=16), server_default="user"),
        sa.Column("two_factor_enabled", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("last_login_ip", sa.String(length=64)),
        sa.Column("last_login_device", sa.String(length=128)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "announcements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(length=255)),
        sa.Column("link", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "daily_price",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False, unique=True),
        sa.Column("price_per_gb", sa.Numeric(8, 4), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "promo_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("bonus_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("expires_at", sa.DateTime()),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True),
        sa.Column("language", sa.String(length=10), server_default="uz"),
        sa.Column("push_notifications", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("session_updates", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("system_updates", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("two_factor_enabled", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("single_device_mode", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("battery_saver", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("theme", sa.String(length=16), server_default="light"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "login_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True),
        sa.Column("city", sa.String(length=64)),
        sa.Column("device", sa.String(length=128)),
        sa.Column("ip_address", sa.String(length=64)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "traffic_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(length=64), nullable=False, unique=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_role", sa.String(length=16), server_default="user"),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime()),
        sa.Column("duration_seconds", sa.Integer()),
        sa.Column("sent_mb", sa.Float(), server_default="0"),
        sa.Column("used_mb", sa.Float(), server_default="0"),
        sa.Column("earned_usd", sa.Numeric(18, 6), server_default="0"),
        sa.Column("status", sa.String(length=16), server_default="active"),
        sa.Column("filter_status", sa.String(length=16), server_default="pending"),
        sa.Column("filter_reasons", sa.JSON()),
        sa.Column("ip_country", sa.String(length=2)),
        sa.Column("ip_asn", sa.String(length=64)),
        sa.Column("is_proxy", sa.Boolean()),
        sa.Column("vpn_score", sa.Float()),
        sa.Column("network_type_client", sa.String(length=16)),
        sa.Column("network_type_asn", sa.String(length=32)),
        sa.Column("validated_at", sa.DateTime()),
        sa.Column("device_id", sa.String(length=128)),
        sa.Column("client_ip", sa.String(length=64)),
        sa.Column("app_version", sa.String(length=32)),
        sa.Column("os", sa.String(length=32)),
        sa.Column("battery_level", sa.Integer()),
        sa.Column("pending_admin_ticket_id", sa.String(length=64)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "session_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("traffic_sessions.id", ondelete="CASCADE")),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("sequence_number", sa.Integer(), server_default="0"),
        sa.Column("delta_mb", sa.Float(), nullable=False),
        sa.Column("cumulative_mb", sa.Float(), nullable=False),
        sa.Column("speed_mbps", sa.Float(), nullable=False),
        sa.Column("battery_level", sa.Integer()),
        sa.Column("network_type", sa.String(length=32)),
        sa.Column("data", sa.JSON(), server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "traffic_filter_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("traffic_sessions.id", ondelete="SET NULL")),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("device_id", sa.String(length=128)),
        sa.Column("client_ip", sa.String(length=64)),
        sa.Column("asn", sa.String(length=64)),
        sa.Column("country", sa.String(length=2)),
        sa.Column("isp", sa.String(length=128)),
        sa.Column("is_proxy", sa.Boolean()),
        sa.Column("vpn_score", sa.Float()),
        sa.Column("network_type_client", sa.String(length=16)),
        sa.Column("network_type_asn", sa.String(length=32)),
        sa.Column("check_sequence", sa.JSON(), server_default=sa.text("'{}'")),
        sa.Column("final_decision", sa.String(length=32), nullable=False),
        sa.Column("reasons", sa.JSON(), server_default=sa.text("'{}'")),
        sa.Column("admin_override_by", sa.String(length=64)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "device_registry",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("device_token", sa.String(length=512), nullable=False),
        sa.Column("platform", sa.String(length=16), nullable=False),
        sa.Column("notifications_enabled", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "notification_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", sa.String(length=128)),
        sa.Column("notif_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.String(length=1024), nullable=False),
        sa.Column("payload", sa.JSON(), server_default=sa.text("'{}'")),
        sa.Column("delivered", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("opened", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("amount_usd", sa.Numeric(18, 6), nullable=False),
        sa.Column("amount_usdt", sa.Numeric(18, 6)),
        sa.Column("currency", sa.String(length=8), server_default="USD"),
        sa.Column("status", sa.String(length=16), server_default="completed"),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "withdraw_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount_usd", sa.Numeric(18, 6), nullable=False),
        sa.Column("amount_usdt", sa.Numeric(18, 6)),
        sa.Column("wallet_address", sa.String(length=128), nullable=False),
        sa.Column("network", sa.String(length=32), server_default="BEP20"),
        sa.Column("status", sa.String(length=16), server_default="pending"),
        sa.Column("payout_id", sa.String(length=128)),
        sa.Column("tx_hash", sa.String(length=128)),
        sa.Column("provider_response", sa.JSON()),
        sa.Column("idempotency_key", sa.String(length=128), unique=True),
        sa.Column("reserved_balance", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("fee_usd", sa.Numeric(18, 6)),
        sa.Column("note", sa.Text()),
        sa.Column("processed_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "balance_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("previous_balance", sa.Numeric(18, 6), nullable=False),
        sa.Column("new_balance", sa.Numeric(18, 6), nullable=False),
        sa.Column("delta", sa.Numeric(18, 6), nullable=False),
        sa.Column("reason", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "support_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("attachment_url", sa.String(length=255)),
        sa.Column("status", sa.String(length=16), server_default="new"),
        sa.Column("admin_reply", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("support_requests")
    op.drop_table("balance_history")
    op.drop_table("withdraw_requests")
    op.drop_table("transactions")
    op.drop_table("notification_log")
    op.drop_table("device_registry")
    op.drop_table("traffic_filter_audit")
    op.drop_table("session_reports")
    op.drop_table("traffic_sessions")
    op.drop_table("login_history")
    op.drop_table("user_settings")
    op.drop_table("promo_codes")
    op.drop_table("daily_price")
    op.drop_table("announcements")
    op.drop_table("users")
