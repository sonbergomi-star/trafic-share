# Traffic Platform API Documentation

Complete API documentation for the Traffic Platform backend.

**Base URL:** `http://113.30.191.89/api`  
**Version:** 1.0.0

---

## Table of Contents

1. [Authentication](#authentication)
2. [Dashboard](#dashboard)
3. [Balance](#balance)
4. [Withdraw](#withdraw)
5. [Sessions](#sessions)
6. [Statistics](#statistics)
7. [Support](#support)
8. [News & Announcements](#news--announcements)
9. [Profile](#profile)
10. [Admin Endpoints](#admin-endpoints)

---

## Authentication

### Telegram Auth

**Endpoint:** `POST /auth/telegram`

Authenticate user via Telegram Widget data.

**Request Body:**
```json
{
  "id": 123456789,
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe",
  "auth_date": 1234567890,
  "hash": "telegram_hash_here"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "telegram_id": 123456789,
    "username": "johndoe",
    "first_name": "John",
    "balance_usd": 0.0
  }
}
```

### Renew Token

**Endpoint:** `POST /auth/renew`  
**Auth:** Required

Renew access token.

**Response:**
```json
{
  "access_token": "new_token_here",
  "token_type": "bearer",
  "expires_in": 604800
}
```

---

## Dashboard

### Get Dashboard Data

**Endpoint:** `GET /dashboard`  
**Auth:** Required

Get user dashboard with balance, stats, and price info.

**Response:**
```json
{
  "status": "success",
  "data": {
    "user": {
      "telegram_id": 123456789,
      "username": "johndoe",
      "first_name": "John",
      "balance_usd": 5.43
    },
    "today_earnings": 0.75,
    "week_earnings": 3.21,
    "total_sessions": 15,
    "active_sessions": 1,
    "current_price": {
      "price_per_gb": 1.50,
      "price_per_mb": 0.0015
    }
  }
}
```

---

## Balance

### Get Balance

**Endpoint:** `GET /balance`  
**Auth:** Required

Get current balance and traffic info.

**Response:**
```json
{
  "status": "success",
  "data": {
    "balance_usd": 5.43,
    "sent_mb": 3620.5,
    "used_mb": 3580.2,
    "pending_withdrawals": 0.0
  }
}
```

### Get Transaction History

**Endpoint:** `GET /balance/transactions`  
**Auth:** Required

**Query Parameters:**
- `page` (int, default: 1)
- `per_page` (int, default: 20)

**Response:**
```json
{
  "status": "success",
  "data": {
    "transactions": [
      {
        "id": 1,
        "type": "income",
        "amount_usd": 0.75,
        "description": "Session earnings",
        "status": "completed",
        "created_at": "2024-01-01T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 50,
      "total_pages": 3
    }
  }
}
```

---

## Withdraw

### Create Withdraw Request

**Endpoint:** `POST /withdraw/create`  
**Auth:** Required

Create USDT BEP20 withdrawal request.

**Request Body:**
```json
{
  "amount_usd": 2.50,
  "wallet_address": "0x1234567890123456789012345678901234567890"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "withdraw_id": 123,
    "amount_usd": 2.50,
    "amount_usdt": 2.50,
    "wallet_address": "0x1234...7890",
    "status": "pending",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### Get Withdraw History

**Endpoint:** `GET /withdraw/history`  
**Auth:** Required

**Response:**
```json
{
  "status": "success",
  "data": {
    "withdrawals": [
      {
        "id": 123,
        "amount_usd": 2.50,
        "amount_usdt": 2.50,
        "wallet_address": "0x1234...7890",
        "status": "completed",
        "tx_hash": "0xabcdef...",
        "created_at": "2024-01-01T12:00:00Z",
        "processed_at": "2024-01-01T12:05:00Z"
      }
    ]
  }
}
```

---

## Sessions

### Start Session

**Endpoint:** `POST /sessions/start`  
**Auth:** Required

Start new traffic sharing session.

**Request Body:**
```json
{
  "ip_address": "1.2.3.4",
  "location": "US",
  "network_type": "wifi"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid-here",
    "start_time": "2024-01-01T12:00:00Z",
    "price_per_mb": 0.0015
  }
}
```

### Stop Session

**Endpoint:** `POST /sessions/{session_id}/stop`  
**Auth:** Required

Stop active session.

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid-here",
    "duration": "01:23:45",
    "sent_mb": 150.5,
    "earned_usd": 0.225
  }
}
```

### Report Traffic

**Endpoint:** `POST /sessions/report`  
**Auth:** Required

Report traffic for active session.

**Request Body:**
```json
{
  "session_id": "uuid-here",
  "cumulative_mb": 150.5,
  "delta_mb": 10.2
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Traffic reported successfully"
}
```

### WebSocket Connection

**Endpoint:** `WS /sessions/ws/{session_id}`  
**Auth:** Required (via query param `token`)

Real-time session updates.

**Messages received:**
```json
{
  "type": "traffic_stats",
  "session_id": "uuid",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "sent_mb": 150.5,
    "speed_mb_s": 0.45,
    "earned_usd": 0.225
  }
}
```

---

## Statistics

### Get Statistics

**Endpoint:** `GET /stats`  
**Auth:** Required

**Query Parameters:**
- `period` (string): "today", "week", "month", "year"

**Response:**
```json
{
  "status": "success",
  "data": {
    "period": "week",
    "summary": {
      "total_sessions": 15,
      "completed_sessions": 14,
      "success_rate": 93.33,
      "total_sent_mb": 3620.5,
      "total_earned_usd": 5.43,
      "avg_duration": "01:15:30"
    },
    "daily_breakdown": [
      {
        "date": "2024-01-01",
        "sessions": 3,
        "sent_mb": 520.0,
        "earned": 0.78
      }
    ]
  }
}
```

---

## Support

### Create Support Request

**Endpoint:** `POST /support/create`  
**Auth:** Required

**Request Body:**
```json
{
  "subject": "Payment Issue",
  "message": "I haven't received my withdrawal",
  "attachment_url": "https://..."
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "ticket_id": 123,
    "subject": "Payment Issue",
    "status": "new",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### Get Support History

**Endpoint:** `GET /support/history`  
**Auth:** Required

---

## News & Announcements

### Get News

**Endpoint:** `GET /news`

**Response:**
```json
{
  "status": "success",
  "data": {
    "telegram_links": {
      "channel": "https://t.me/yourchannel",
      "group": "https://t.me/yourgroup"
    },
    "announcements": [
      {
        "id": 1,
        "title": "Price Update",
        "description": "New pricing: $1.50/GB",
        "image_url": "https://...",
        "created_at": "2024-01-01T12:00:00Z"
      }
    ],
    "promo_codes": [
      {
        "code": "WELCOME10",
        "bonus_percent": 10.0,
        "description": "10% bonus on first withdrawal"
      }
    ]
  }
}
```

---

## Profile

### Get Profile

**Endpoint:** `GET /profile`  
**Auth:** Required

**Response:**
```json
{
  "status": "success",
  "data": {
    "telegram_id": 123456789,
    "username": "johndoe",
    "first_name": "John",
    "balance_usd": 5.43,
    "total_sessions": 15,
    "total_earned": 10.25,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## Admin Endpoints

All admin endpoints require admin authentication.

### Get Dashboard Stats

**Endpoint:** `GET /admin/reports/dashboard`  
**Auth:** Admin

### Get All Users

**Endpoint:** `GET /admin/users`  
**Auth:** Admin

### Ban User

**Endpoint:** `POST /admin/users/{telegram_id}/ban`  
**Auth:** Admin

### Approve Withdrawal

**Endpoint:** `POST /admin/withdrawals/{withdraw_id}/approve`  
**Auth:** Admin

### Create Announcement

**Endpoint:** `POST /admin/announcements/create`  
**Auth:** Admin

---

## Error Responses

All error responses follow this format:

```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {}
}
```

**Common Error Codes:**
- `AUTH_001` - Invalid credentials
- `AUTH_002` - Token expired
- `VAL_001` - Invalid input
- `BUS_001` - Insufficient balance
- `NET_001` - VPN detected
- `SYS_001` - Internal error

---

## Rate Limiting

- 60 requests per minute per IP
- 1000 requests per hour per IP

Rate limit headers:
- `X-RateLimit-Limit-Minute`
- `X-RateLimit-Remaining-Minute`
- `X-RateLimit-Limit-Hour`
- `X-RateLimit-Remaining-Hour`

---

**Last Updated:** 2024-01-01  
**API Version:** 1.0.0
