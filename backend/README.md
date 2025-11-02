## Traffic Platform Backend

This service implements the Telegram-authenticated traffic sharing backend described in the product specifications. It exposes REST and WebSocket endpoints for the Android client and admin tooling, and orchestrates background workers for pricing, notifications, payouts, and telemetry reconciliation.

### Features

- Telegram Login and JWT session management
- Dashboard aggregation with pricing, balance, traffic, and notifications
- Traffic start/stop flow with policy filters, admin bypass, and audit logging
- Pricing announcements with admin workflows and push notifications
- Session telemetry ingestion, analytics aggregation, and statistics APIs
- Balance and payout management with transactional accounting and provider integrations
- Notifications pipeline for FCM, Telegram, and email
- Support ticketing, news & promo, settings, and profile management endpoints
- Admin panel APIs covering users, APIs, traffic pools, payouts, and system settings

For setup and deployment instructions see the repository-level documentation.
