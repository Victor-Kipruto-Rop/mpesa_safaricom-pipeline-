"""
README - M-Pesa Platform Production Deployment Guide
======================================================

This is a production-ready M-Pesa analytics platform integrated with Safaricom Daraja API.
Complete with webhooks, fraud detection, analytics, and Cloud Run deployment.

Quick Links:
- API Reference: See API_REFERENCE.md
- Deployment Steps: See DEPLOYMENT_STEPS.md
- Production Checklist: See PRODUCTION_CHECKLIST.md
- Architecture Diagram: See docs/ARCHITECTURE.md
"""

# ============================================================================
# 🚀 QUICK START (5 minutes)
# ============================================================================

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- Safaricom Daraja credentials (Business Shortcode, Consumer Key/Secret)

## 1. Clone and Setup

```bash
git clone <repo-url> mpesa-platform
cd mpesa-platform/01_MPESA_Safaricom/01_Real_Time_Transaction_Streaming
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with Safaricom credentials and other settings
```

Required in .env:
```
DARAJA_CONSUMER_KEY=your_key
DARAJA_CONSUMER_SECRET=your_secret
DARAJA_BUSINESS_SHORTCODE=8759693
DARAJA_PASSKEY=your_passkey
DARAJA_ENVIRONMENT=sandbox  # or production
DATABASE_URL=postgresql://user:pass@localhost:5432/mpesa
```

## 3. Start Services

```bash
# Start PostgreSQL, Redis, Kafka
docker compose up -d

# Create database tables
python -c "from app.database.connection import Base, engine; Base.metadata.create_all(engine)"

# Run application
uvicorn app.main:app --reload
```

API is now at: `http://localhost:8000`
API Docs at: `http://localhost:8000/docs`

## 4. Test Webhooks

```bash
# In another terminal, start ngrok for local testing
ngrok http 8000

# Register callbacks with Safaricom
python -c "
import asyncio
from app.services.safaricom import daraja_service

async def register():
    await daraja_service.register_c2b_callback(
        confirmation_url='https://YOUR_NGROK_URL/api/v1/webhooks/c2b/confirmation',
        validation_url='https://YOUR_NGROK_URL/api/v1/webhooks/c2b/validation'
    )

asyncio.run(register())
"

# Send test payment
curl -X POST http://localhost:8000/api/v1/transactions/initiate-stk \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "254712345678",
    "amount": 100,
    "account_reference": "ChamaNdoto"
  }'
```

---

## 📁 Project Structure

```
01_Real_Time_Transaction_Streaming/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── models.py               # SQLAlchemy ORM models
│   ├── database/
│   │   └── connection.py        # Database connection setup
│   ├── api/
│   │   └── v1/
│   │       ├── webhooks.py     # Webhook endpoints
│   │       ├── transactions.py # Transaction endpoints
│   │       ├── analytics.py    # Analytics endpoints
│   │       └── admin.py        # Admin endpoints
│   ├── services/
│   │   ├── safaricom.py        # Daraja API integration
│   │   ├── transaction.py      # Transaction business logic
│   │   ├── reconciliation.py   # Reconciliation service
│   │   └── fraud.py            # Fraud detection service
│   └── middleware/
│       ├── auth.py             # HMAC verification
│       ├── rate_limit.py       # Rate limiting
│       └── logging.py          # Structured logging
├── ml/
│   └── fraud_detection.py       # ML-based fraud detection
├── analytics/
│   └── advanced_analytics.py    # Advanced analytics engine
├── ingestion/
│   └── kafka_consumer.py        # Kafka transaction ingestion
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
│   ├── ARCHITECTURE.md          # System architecture
│   ├── DATABASE_SCHEMA.md       # Database design
│   └── CONTRIBUTING.md          # Development guidelines
├── docker-compose.yml           # Local development services
├── Dockerfile                   # Production Docker image
├── Makefile                     # Common automation tasks
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── API_REFERENCE.md            # Complete API documentation
├── DEPLOYMENT_STEPS.md         # Production deployment guide
├── PRODUCTION_CHECKLIST.md     # Implementation checklist
└── README.md                    # This file
```

---

## 🔧 Common Tasks

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_transaction.py -v
```

### Database Management

```bash
# Connect to database
make db-connect

# View database status
make db-status

# Create backup
make db-backup

# Run migrations
alembic upgrade head
```

### Data Processing

```bash
# Start transaction ingestion from Kafka
make ingest

# Run fraud detection
make fraud-detection

# Generate analytics reports
make analytics

# Generate dashboards
make dashboards
```

### Monitoring

```bash
# Health check
make health-check

# View logs
make logs

# Monitor metrics
make metrics
```

### Production Operations

```bash
# Deploy to Cloud Run
make gcp-deploy

# Setup GCP infrastructure
make gcp-setup

# Run security checks
make security-check
```

See [Makefile](Makefile) for all 50+ available commands.

---

## 🔐 Security

### HMAC Signature Verification

All webhook requests from Safaricom must be signed with HMAC-SHA256:

```python
import hmac
import hashlib
import json

def verify_signature(request_body: str, signature: str, secret: str) -> bool:
    computed = hmac.new(
        secret.encode(),
        request_body.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature)
```

### Environment Secrets

- Never commit `.env` file with real credentials
- Use Google Secret Manager in production
- Rotate credentials regularly
- Enable audit logging for all API access

### Database Security

- Enable SSL/TLS for connections
- Use strong passwords
- Restrict network access with VPC
- Enable automated backups
- Monitor for unauthorized access

### API Security

- All endpoints use HTTPS only
- Rate limiting: 100 requests/minute
- CORS enabled only for known domains
- CSRF protection on state-changing endpoints
- SQL injection prevention via parameterized queries

---

## 📊 Monitoring & Observability

### Prometheus Metrics

```
# Request metrics
http_requests_total{method="POST",endpoint="/webhooks/c2b"}
http_request_duration_seconds{method="POST",endpoint="/webhooks/c2b"}
http_requests_failed_total{method="POST",endpoint="/webhooks/c2b"}

# Application metrics
active_transactions_count
kafka_lag
database_connection_pool_active
fraud_alerts_total
```

### Cloud Logging

Access logs in Google Cloud Console or CLI:

```bash
gcloud logging read "resource.type=cloud_run_revision" \
  --format=json --limit=50
```

### Alerting

Configured alert rules for:
- High error rate (> 1%)
- High latency (p95 > 5s)
- Service unavailability
- Database connection pool exhaustion
- Kafka lag > 1000 messages
- Fraud detection spike

---

## 🧪 Testing

### Unit Tests

```python
# tests/unit/test_safaricom.py
import pytest
from app.services.safaricom import DarajaService

@pytest.mark.asyncio
async def test_get_access_token():
    service = DarajaService()
    token = await service.get_access_token()
    assert token is not None
    assert len(token) > 0
```

### Integration Tests

```python
# tests/integration/test_webhooks.py
def test_c2b_confirmation_webhook():
    response = client.post(
        "/api/v1/webhooks/c2b/confirmation",
        json={...},
        headers={
            "X-Safaricom-Signature": valid_signature
        }
    )
    assert response.status_code == 200
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/v1/health

# Using Locust
locust -f tests/load/locustfile.py --headless -u 100 -r 10
```

---

## 🐛 Troubleshooting

### Issue: Database Connection Failed

```bash
# Check Docker is running
docker ps

# Check database service
docker compose ps postgres

# Verify credentials in .env
grep DATABASE_URL .env

# Connect directly
psql postgresql://user:pass@localhost:5432/mpesa
```

### Issue: Webhooks Not Received

1. Verify ngrok URL is correct
2. Check Safaricom dashboard for callback URL registration
3. Ensure X-Safaricom-Signature header is present
4. Verify HMAC secret matches
5. Check application logs: `docker compose logs app`

### Issue: Fraud Detection Not Working

1. Ensure ML models are trained: `python ml/fraud_detection.py --train`
2. Check model files exist: `ls models/`
3. Verify data in database: `SELECT COUNT(*) FROM transactions;`
4. Check for required features in transaction data

### Issue: High Latency on Webhooks

1. Check database connection pool: `make health-check`
2. Monitor Kafka lag: `make logs | grep kafka_lag`
3. Scale Cloud Run: `gcloud run services update mpesa-app --max-instances=200`
4. Enable caching: Set REDIS_ENABLED=true in .env

---

## 📈 Performance Optimization

### Database

- Add indexes on frequently queried columns (30+ already defined)
- Use materialized views for complex queries
- Enable query result caching
- Partition large tables by date

### Application

- Enable response caching: `Cache-Control: max-age=60`
- Use connection pooling (default: 10 connections)
- Batch webhook processing: Process 100 transactions at once
- Async operations: Use asyncio for I/O

### Infrastructure

- Cloud Run: Min 2 instances, max 200 for auto-scaling
- Cloud SQL: db-custom-4-16384 (4 CPU, 16GB RAM)
- Redis: 4GB instance for caching
- Cloud Load Balancer: Distribute traffic across instances

---

## 🚀 Production Deployment

### Prerequisites

1. GCP Project: `mpesapipeline`
2. Cloud SQL Instance: `mpesa-postgres`
3. Docker image: `gcr.io/mpesapipeline/mpesa-app`
4. Domain: `chamayangu.online` with SSL certificate
5. Service Account: `mpesa-app-sa`

### Deployment Steps

See complete guide: [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)

Quick deploy:
```bash
export PROJECT_ID=mpesapipeline
export REGION=africa-south1

# Build and push image
docker build -t gcr.io/$PROJECT_ID/mpesa-app:latest .
docker push gcr.io/$PROJECT_ID/mpesa-app:latest

# Deploy to Cloud Run
gcloud run deploy mpesa-app \
  --image=gcr.io/$PROJECT_ID/mpesa-app:latest \
  --region=$REGION \
  --set-env-vars="ENVIRONMENT=production"
```

---

## 📚 API Documentation

### Interactive API Docs

Once running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Complete Reference

See [API_REFERENCE.md](API_REFERENCE.md) for:
- All endpoints with examples
- Request/response schemas
- Error codes and handling
- Rate limiting rules
- Authentication details

### Example: Initiate STK Push

```bash
curl -X POST http://localhost:8000/api/v1/transactions/initiate-stk \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "254712345678",
    "amount": 500,
    "account_reference": "ChamaNdoto",
    "description": "Payment for group"
  }'

# Response:
{
  "status": "pending",
  "checkout_request_id": "ws_CO_DMZ_12321...",
  "message": "STK popup sent to phone",
  "expires_in_seconds": 120
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes following [CONTRIBUTING.md](docs/CONTRIBUTING.md)
4. Add tests for new functionality
5. Run tests: `pytest`
6. Submit pull request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📞 Support

- **Documentation**: https://chamayangu.online/docs
- **Issues**: GitHub Issues on repository
- **Email**: support@chamayangu.online
- **Slack**: #mpesa-platform channel

---

## ✅ Checklist for First Deployment

- [ ] Clone repository and install dependencies
- [ ] Configure .env with Safaricom credentials
- [ ] Start Docker services: `docker compose up -d`
- [ ] Create database tables: `python -c "from app.database.connection import Base, engine; Base.metadata.create_all(engine)"`
- [ ] Test local API: `curl http://localhost:8000/api/v1/health`
- [ ] Run tests: `pytest`
- [ ] Register webhooks: `python scripts/register_callbacks.py`
- [ ] Test webhook: Send payment via Safaricom Sandbox
- [ ] Check GCP project created: `gcloud projects list`
- [ ] Setup Cloud SQL: `gcloud sql instances create mpesa-postgres`
- [ ] Deploy to Cloud Run: `gcloud run deploy mpesa-app`
- [ ] Setup domain and SSL: Follow HTTPS setup in DEPLOYMENT_STEPS.md
- [ ] Configure monitoring: `gcloud monitoring dashboards create`
- [ ] Switch to production Safaricom credentials
- [ ] Run load test: `ab -n 1000 -c 10`
- [ ] Monitor metrics: Visit Cloud Console dashboard

---

**Last Updated**: January 2024
**Status**: Production Ready ✅
**Maintainer**: Data Engineering Team
"""