# M-Pesa Platform API Reference

Complete documentation of all API endpoints for the ChamaNdoto M-Pesa analytics platform.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Health & Status](#health--status)
3. [Webhooks](#webhooks)
4. [Transactions](#transactions)
5. [Analytics](#analytics)
6. [Reconciliation](#reconciliation)
7. [Admin](#admin)
8. [Error Handling](#error-handling)

---

## Authentication

All endpoints (except health checks) require HMAC signature verification on the `X-Safaricom-Signature` header.

### Signature Verification

```
Signature = HMAC-SHA256(
    body_json,
    api_secret_key
)

Header: X-Safaricom-Signature: {signature}
```

**Example:**

```python
import hmac
import hashlib
import json

secret = "your-secret-key"
body = json.dumps({"amount": 100, "msisdn": "254712345678"})
signature = hmac.new(
    secret.encode(),
    body.encode(),
    hashlib.sha256
).hexdigest()
```

---

## Health & Status

### GET /api/v1/health

Check application health status.

**Response:**
```json
{
  "service": "M-Pesa Analytics Platform",
  "version": "1.0.0",
  "status": "operational",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "connected",
  "redis": "connected",
  "kafka": "connected"
}
```

**Status Codes:**
- `200` - All systems operational
- `503` - One or more services unavailable

---

## Webhooks

### POST /api/v1/webhooks/c2b/validation

Safaricom calls this endpoint to validate incoming C2B payments.

**Headers:**
```
Content-Type: application/json
X-Safaricom-Signature: {hmac_signature}
```

**Request Body:**
```json
{
  "TransactionType": "Pay Bills Online",
  "TransID": "LHG31AA5V61",
  "TransTime": "20240115103030",
  "TransAmount": "100",
  "BusinessShortCode": "8759693",
  "BillRefNumber": "ChamaNdoto",
  "InvoiceNumber": "",
  "FirstName": "John",
  "MiddleName": "",
  "LastName": "Doe",
  "MSISDN": "254712345678"
}
```

**Response (Must respond within 25 seconds):**
```json
{
  "ResultCode": 0,
  "ResultDesc": "Accepted"
}
```

**Response Codes:**
- `0` - Accept transaction
- `1` - Reject transaction

---

### POST /api/v1/webhooks/c2b/confirmation

Safaricom calls this endpoint to confirm completed C2B payments.

**Request Body:**
```json
{
  "TransactionType": "Pay Bills Online",
  "TransID": "LHG31AA5V61",
  "TransTime": "20240115103030",
  "TransAmount": "100",
  "BusinessShortCode": "8759693",
  "BillRefNumber": "ChamaNdoto",
  "InvoiceNumber": "",
  "FirstName": "John",
  "MiddleName": "",
  "LastName": "Doe",
  "MSISDN": "254712345678",
  "TransactionStatus": "Success"
}
```

**Response:**
```json
{
  "ResultCode": 0,
  "ResultDesc": "Received Successfully"
}
```

---

### POST /api/v1/webhooks/stk/callback

Safaricom calls this endpoint when customer completes STK push payment.

**Request Body:**
```json
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "29115-34620561-1",
      "CheckoutRequestID": "ws_CO_DMZ_12321_2740201215163000",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {
            "Name": "Amount",
            "Value": 100
          },
          {
            "Name": "MpesaReceiptNumber",
            "Value": "LHG31AA5V61"
          },
          {
            "Name": "TransactionDate",
            "Value": 20240115103030
          },
          {
            "Name": "PhoneNumber",
            "Value": 254712345678
          }
        ]
      }
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Payment processed"
}
```

---

### POST /api/v1/webhooks/b2c/callback

Safaricom calls this endpoint for B2C (payout) completion.

**Request Body:**
```json
{
  "Result": {
    "ResultType": 0,
    "ResultCode": 0,
    "ResultDesc": "The service request is processed successfully.",
    "OriginatorConversationID": "256-38651-1234567890",
    "ConversationID": "256-38651-1234567890",
    "TransactionID": "TLP738NFXY",
    "ResultParameters": {
      "ResultParameter": [
        {
          "Key": "TransactionAmount",
          "Value": 100
        },
        {
          "Key": "TransactionReceipt",
          "Value": "LHG31AA5V61"
        },
        {
          "Key": "B2CUtilityAccountAvailableFunds": "50000"
        }
      ]
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "B2C payment confirmed"
}
```

---

## Transactions

### GET /api/v1/transactions

Retrieve transaction history with filtering.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `phone_number` | string | Filter by customer phone |
| `status` | string | `success`, `pending`, `failed` |
| `start_date` | ISO8601 | Start date (default: 7 days ago) |
| `end_date` | ISO8601 | End date (default: now) |
| `limit` | integer | Results per page (default: 100, max: 1000) |
| `offset` | integer | Pagination offset (default: 0) |

**Example Request:**
```bash
GET /api/v1/transactions?phone_number=254712345678&status=success&limit=50
```

**Response:**
```json
{
  "data": [
    {
      "id": "txn_001",
      "phone_number": "254712345678",
      "amount": 100.00,
      "status": "success",
      "transaction_type": "c2b",
      "reference": "ChamaNdoto",
      "receipt_number": "LHG31AA5V61",
      "timestamp": "2024-01-15T10:30:00Z",
      "fraud_score": 0.02,
      "region": "Nairobi"
    }
  ],
  "total": 245,
  "limit": 50,
  "offset": 0
}
```

---

### GET /api/v1/transactions/{transaction_id}

Get detailed transaction information.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `transaction_id` | string | Transaction ID |

**Response:**
```json
{
  "id": "txn_001",
  "phone_number": "254712345678",
  "amount": 100.00,
  "status": "success",
  "transaction_type": "c2b",
  "reference": "ChamaNdoto",
  "receipt_number": "LHG31AA5V61",
  "timestamp": "2024-01-15T10:30:00Z",
  "fraud_score": 0.02,
  "fraud_flag": false,
  "region": "Nairobi",
  "processing_time_ms": 234,
  "webhook_received_at": "2024-01-15T10:30:01Z",
  "error_message": null
}
```

---

### POST /api/v1/transactions/initiate-stk

Initiate STK push payment (show popup on customer phone).

**Request Body:**
```json
{
  "phone_number": "254712345678",
  "amount": 500.00,
  "account_reference": "ChamaNdoto",
  "description": "Payment for group contribution"
}
```

**Response:**
```json
{
  "status": "pending",
  "checkout_request_id": "ws_CO_DMZ_12321_2740201215163000",
  "phone_number": "254712345678",
  "amount": 500.00,
  "message": "STK popup sent to phone",
  "expires_in_seconds": 120
}
```

**Status Codes:**
- `200` - STK pushed successfully
- `400` - Invalid request (missing fields, invalid phone)
- `429` - Rate limited
- `500` - Service error

---

### GET /api/v1/transactions/stk/{checkout_request_id}/status

Query STK push status.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `checkout_request_id` | string | Checkout request ID |

**Response:**
```json
{
  "checkout_request_id": "ws_CO_DMZ_12321_2740201215163000",
  "status": "success",
  "result_code": 0,
  "result_description": "The service request is processed successfully.",
  "transaction_data": {
    "amount": 500.00,
    "phone_number": "254712345678",
    "mpesa_receipt": "LHG31AA5V61",
    "transaction_date": "2024-01-15T10:30:00Z"
  }
}
```

---

### POST /api/v1/transactions/initiate-b2c

Initiate B2C payout to customer.

**Request Body:**
```json
{
  "phone_number": "254712345678",
  "amount": 1000.00,
  "reference": "Monthly_Payout",
  "remarks": "Group distribution"
}
```

**Response:**
```json
{
  "status": "pending",
  "conversation_id": "256-38651-1234567890",
  "transaction_id": "TLP738NFXY",
  "phone_number": "254712345678",
  "amount": 1000.00,
  "message": "Payout initiated"
}
```

---

## Analytics

### GET /api/v1/analytics/summary

Get high-level analytics summary.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `period` | string | `today`, `week`, `month`, `year` (default: `month`) |

**Response:**
```json
{
  "period": "month",
  "metrics": {
    "total_transactions": 1250,
    "total_amount": 125000.00,
    "unique_customers": 342,
    "average_transaction_size": 100.00,
    "success_rate": 0.98,
    "fraud_rate": 0.02,
    "peak_hour": "14:00-15:00"
  },
  "top_merchants": [
    {
      "name": "Merchant A",
      "transaction_count": 245,
      "total_amount": 24500.00
    }
  ],
  "regional_distribution": {
    "Nairobi": 0.45,
    "Mombasa": 0.25,
    "Kisumu": 0.15,
    "Other": 0.15
  }
}
```

---

### GET /api/v1/analytics/customer/{phone_number}

Get customer-specific analytics.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `phone_number` | string | Customer phone number |

**Response:**
```json
{
  "phone_number": "254712345678",
  "profile": {
    "first_transaction": "2023-01-01T00:00:00Z",
    "transaction_count": 45,
    "total_amount": 45000.00,
    "average_transaction": 1000.00,
    "segment": "High Value",
    "lifetime_value": 45000.00
  },
  "recent_transactions": [
    {
      "id": "txn_001",
      "amount": 1000.00,
      "timestamp": "2024-01-15T10:30:00Z",
      "status": "success"
    }
  ],
  "risk_profile": {
    "fraud_score": 0.05,
    "fraud_flag": false,
    "risk_level": "low",
    "anomaly_flags": []
  }
}
```

---

### GET /api/v1/analytics/fraud-alerts

Get active fraud alerts.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `severity` | string | `low`, `medium`, `high`, `critical` |
| `status` | string | `active`, `resolved` |
| `limit` | integer | Number of alerts (default: 100) |

**Response:**
```json
{
  "data": [
    {
      "id": "alert_001",
      "phone_number": "254712345678",
      "severity": "high",
      "status": "active",
      "reason": "Unusual transaction pattern detected",
      "fraud_score": 0.92,
      "created_at": "2024-01-15T10:30:00Z",
      "transaction_ids": ["txn_001", "txn_002"]
    }
  ],
  "total_active": 12,
  "total_critical": 2
}
```

---

### GET /api/v1/analytics/forecast

Get transaction forecast.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `days` | integer | Forecast days (default: 7, max: 30) |

**Response:**
```json
{
  "forecast_period_days": 7,
  "predictions": [
    {
      "date": "2024-01-16",
      "predicted_volume": 1350,
      "predicted_amount": 135000.00,
      "confidence_interval": {
        "lower": 1200,
        "upper": 1500
      }
    }
  ]
}
```

---

## Reconciliation

### POST /api/v1/reconciliation/daily

Trigger daily reconciliation process.

**Request Body:**
```json
{
  "date": "2024-01-15",
  "manual": false
}
```

**Response:**
```json
{
  "status": "processing",
  "reconciliation_id": "recon_001",
  "date": "2024-01-15",
  "started_at": "2024-01-16T00:30:00Z",
  "estimated_completion": "2024-01-16T00:45:00Z"
}
```

---

### GET /api/v1/reconciliation/{reconciliation_id}

Get reconciliation status.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `reconciliation_id` | string | Reconciliation ID |

**Response:**
```json
{
  "reconciliation_id": "recon_001",
  "date": "2024-01-15",
  "status": "completed",
  "started_at": "2024-01-16T00:30:00Z",
  "completed_at": "2024-01-16T00:42:15Z",
  "statistics": {
    "total_transactions": 1250,
    "total_amount": 125000.00,
    "matched": 1248,
    "mismatched": 2,
    "missing_in_system": 0,
    "missing_in_safaricom": 0
  },
  "mismatches": [
    {
      "transaction_id": "txn_001",
      "our_amount": 100.00,
      "safaricom_amount": 105.00,
      "difference": 5.00,
      "reason": "Amount mismatch"
    }
  ]
}
```

---

### GET /api/v1/reconciliation/reports

Get reconciliation reports.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | ISO8601 | Start date |
| `end_date` | ISO8601 | End date |
| `status` | string | `completed`, `failed`, `pending` |

**Response:**
```json
{
  "data": [
    {
      "reconciliation_id": "recon_001",
      "date": "2024-01-15",
      "status": "completed",
      "total_transactions": 1250,
      "match_rate": 0.9984,
      "issues_found": 2
    }
  ],
  "summary": {
    "average_match_rate": 0.9987,
    "total_issues": 8,
    "critical_issues": 0
  }
}
```

---

## Admin

### GET /api/v1/admin/logs

Get application logs.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | string | `debug`, `info`, `warning`, `error`, `critical` |
| `service` | string | Service name |
| `limit` | integer | Number of logs (default: 100) |
| `search` | string | Search term |

**Response:**
```json
{
  "data": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "error",
      "service": "webhook_handler",
      "message": "Failed to process transaction",
      "context": {
        "transaction_id": "txn_001",
        "error_code": "DB_ERROR"
      },
      "stack_trace": "..."
    }
  ],
  "total": 1542
}
```

---

### POST /api/v1/admin/alerts/test

Test alert system.

**Request Body:**
```json
{
  "alert_type": "high_error_rate",
  "severity": "critical"
}
```

**Response:**
```json
{
  "status": "sent",
  "alert_id": "alert_test_001",
  "recipients": [
    "admin@chamayangu.online"
  ],
  "message": "Test alert sent successfully"
}
```

---

### GET /api/v1/admin/health-check

Detailed health check (admin only).

**Response:**
```json
{
  "service": "M-Pesa Analytics Platform",
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "database": {
      "status": "connected",
      "latency_ms": 5,
      "connection_pool": {
        "active": 3,
        "idle": 7,
        "total": 10
      }
    },
    "redis": {
      "status": "connected",
      "latency_ms": 2
    },
    "kafka": {
      "status": "connected",
      "lag": {
        "transactions_topic": 0,
        "events_topic": 0
      }
    },
    "safaricom_api": {
      "status": "reachable",
      "latency_ms": 245
    },
    "gcp": {
      "status": "connected",
      "services": [
        "Secret Manager",
        "Cloud Storage",
        "Cloud Monitoring"
      ]
    }
  }
}
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request parameters",
    "details": {
      "field": "phone_number",
      "reason": "Must be 12 digits starting with 254"
    },
    "request_id": "req_abc123def456",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_REQUEST` | 400 | Missing or invalid parameters |
| `UNAUTHORIZED` | 401 | Missing authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `VALIDATION_ERROR` | 422 | Data validation failed |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Dependent service down |
| `SAFARICOM_ERROR` | 502 | Safaricom API error |

---

## Rate Limiting

All API endpoints are rate limited:

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Webhooks | 500/min | Per IP |
| Regular API | 100/min | Per API key |
| Admin API | 10/min | Per API key |

Headers returned:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705318200
```

---

## Pagination

Large result sets use cursor-based pagination:

```json
{
  "data": [...],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 1250,
    "has_next": true,
    "next_url": "/api/v1/transactions?offset=50"
  }
}
```

---

## Support

- **Documentation**: https://chamayangu.online/docs
- **API Issues**: https://github.com/yourorg/mpesa-platform/issues
- **Email**: support@chamayangu.online
- **Slack**: #api-support channel
