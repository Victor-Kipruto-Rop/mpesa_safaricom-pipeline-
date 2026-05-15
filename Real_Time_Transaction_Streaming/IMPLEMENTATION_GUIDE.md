"""
Comprehensive Implementation Guide for M-Pesa Analytics Platform
Complete step-by-step guide with all components
"""

# COMPLETE IMPLEMENTATION GUIDE
# ============================

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          M-PESA ANALYTICS PLATFORM                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Safaricom   │  │  C2B Direct  │  │  STK Push    │  │  Legacy    │ │
│  │  Webhook     │  │  API         │  │  Callbacks   │  │  Systems   │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬─────┘ │
│         │                 │                  │                 │       │
│         └─────────────────┼──────────────────┼─────────────────┘       │
│                           │                  │                         │
│                    ┌──────▼──────────────────▼──────────┐              │
│                    │   Flask Webhook Receiver           │              │
│                    │   • Transaction parsing            │              │
│                    │   • Real-time validation           │              │
│                    │   • Rate limiting                  │              │
│                    └──────┬───────────────────────────┬──┘              │
│                           │                           │                 │
│        ┌──────────────────┘                           │                 │
│        │                                              │                 │
│  ┌─────▼──────────────┐                      ┌──────▼────────────┐    │
│  │  Apache Kafka      │                      │  PostgreSQL DB    │    │
│  │  • 3 partitions    │                      │  • Raw data       │    │
│  │  • 24h retention   │                      │  • Staging tables │    │
│  │  • High throughput │                      │  • Mart tables    │    │
│  └─────┬──────────────┘                      └──────▼────────────┘    │
│        │                                            │                  │
│        │  ┌────────────────────────────────────────┘                  │
│        │  │                                                            │
│  ┌─────▼──▼────────────────────────────────────┐                      │
│  │   Data Processing Pipeline                  │                      │
│  │   • Kafka Consumer (ingestion/              │                      │
│  │   • DBT Models (dbt/)                       │                      │
│  │   • Advanced Analytics (analytics/)         │                      │
│  │   • Fraud Detection ML (ml/)                │                      │
│  └─────┬──────────────────────────────────────┘                       │
│        │                                                              │
│  ┌─────▼──────────────┐        ┌──────────────────────┐              │
│  │  Redis Cache       │        │  GCS Backups         │              │
│  │  • Hot data        │        │  • Daily backups     │              │
│  │  • Session data    │        │  • 30-day retention  │              │
│  └────────────────────┘        └──────────────────────┘              │
│        │                                                              │
│        │  ┌────────────────────────────────────────────┐             │
│        │  │                                            │             │
│  ┌─────▼──▼──────────────────────────────────────────┐│             │
│  │   Grafana Dashboards                             ││             │
│  │   • Real-Time Overview (3000:3000)               ││             │
│  │   • Advanced Analytics                           ││             │
│  │   • Fraud Detection & Security                   ││             │
│  │   • Operational Metrics                          ││             │
│  └────────────────────────────────────────────────────┘│             │
│                                                        │             │
│        ┌─────────────────────────────────────────────┘             │
│        │                                                            │
│  ┌─────▼──────────────────┐                ┌─────────────────────┐│
│  │  GCP Cloud Components  │                │  Security Layer    ││
│  │  • Cloud SQL           │                │  • HMAC signing    ││
│  │  • Cloud Run           │                │  • Field encryption││
│  │  • Cloud Storage       │                │  • Rate limiting   ││
│  │  • Cloud Pub/Sub       │                │  • IP filtering    ││
│  │  • Cloud Monitoring    │                │  • Audit logging   ││
│  └────────────────────────┘                └─────────────────────┘│
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## QUICK START (15 minutes)

### 1. Verify Infrastructure
```bash
cd /home/kipruto/Desktop/DATA_ENGINEERING/01_MPESA_Safaricom/01_Real_Time_Transaction_Streaming

# Check environment
python verify_setup.py

# Test Daraja API
python test_daraja.py
```

### 2. Start Grafana (already running)
- Access at: http://localhost:3000
- Username: admin
- Password: admin123

### 3. Configure PostgreSQL Data Source
- Click Settings → Data Sources
- Add PostgreSQL
- Host: localhost:5433
- Database: mpesa_analytics
- User: data_engineer
- Password: change_me

### 4. Import Dashboards
```bash
# Generate dashboard JSON files
python dashboards/grafana_dashboards.py

# Dashboards created in dashboards/ directory
# Import manually via Grafana UI or API
```

## STEP-BY-STEP IMPLEMENTATION

### Phase 1: Data Ingestion (Week 1)

#### 1.1 Start Kafka Consumer
```bash
# Terminal 1: Start consumer
python ingestion/kafka_consumer.py

# Monitors mpesa-transactions topic
# Processes and inserts data into PostgreSQL
# Logs to logs/kafka_consumer.log
```

#### 1.2 Test with Sample Data
```bash
# Terminal 2: Send test data to Kafka
python scripts/send_sample_transactions.py
```

#### 1.3 Verify Data Ingestion
```bash
# Check PostgreSQL
psql -h localhost -p 5433 -U data_engineer -d mpesa_analytics

# Verify raw table
SELECT COUNT(*) FROM mpesa_transactions_raw;
```

### Phase 2: Data Transformation (Week 1-2)

#### 2.1 Create DBT Models
```bash
cd dbt/

# Create staging models
dbt run --profiles-dir profiles/ --select stg_*

# Create data marts
dbt run --profiles-dir profiles/ --select mart_*

# Run tests
dbt test --profiles-dir profiles/
```

#### 2.2 Verify Transformations
```bash
# Check staging tables
SELECT COUNT(*) FROM stg_mpesa_transactions;

# Check marts
SELECT * FROM mart_daily_transactions;
```

### Phase 3: Advanced Analytics (Week 2)

#### 3.1 Run Analytics Engine
```bash
python analytics/advanced_analytics.py > reports/analytics_report.json

# Generates:
# - Customer segmentation
# - Behavior analysis  
# - Anomaly detection
# - Forecasting
# - Regional analysis
```

#### 3.2 Schedule Analytics Job
```bash
# Add to Airflow DAG (or cron)
*/30 * * * * python analytics/advanced_analytics.py
```

### Phase 4: Fraud Detection ML (Week 2-3)

#### 4.1 Train Fraud Models
```bash
python ml/fraud_detection.py

# Creates and saves:
# - Isolation Forest model
# - Random Forest classifier
# - Gradient Boosting model
# Models saved in models/ directory
```

#### 4.2 Real-Time Fraud Scoring
```bash
# In production:
from ml.fraud_detection import FraudDetectionEngine

engine = FraudDetectionEngine()

# Score incoming transaction
transaction = {
    'transaction_id': 'TXN001',
    'phone_number': '+254712345678',
    'amount': 5000,
    'transaction_time': '2024-05-15 14:30:00',
    'business_shortcode': '8759693',
    'region': 'Nairobi'
}

fraud_score = engine.predict_fraud(transaction)
```

### Phase 5: Dashboards & Visualization (Week 3)

#### 5.1 Create Dashboard Data Source
```bash
# PostgreSQL already configured on localhost:5433
# Create connection in Grafana
```

#### 5.2 Import Dashboards
```bash
# Method 1: Manual (via UI)
# 1. Go to Grafana → Dashboards → Import
# 2. Upload dashboards/realtime_dashboard.json
# 3. Repeat for other dashboards

# Method 2: API
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/realtime_dashboard.json
```

#### 5.3 Verify Dashboards
- Real-Time Overview: http://localhost:3000/d/realtime
- Advanced Analytics: http://localhost:3000/d/analytics
- Fraud Detection: http://localhost:3000/d/fraud
- Operational: http://localhost:3000/d/operational

### Phase 6: Security & GCP Setup (Week 4)

#### 6.1 Review Security Policies
```bash
python security/gcp_integration.py

# Displays:
# - Rate limiting rules
# - Authentication policies
# - Encryption standards
# - Audit logging setup
# - Network policies
```

#### 6.2 Setup GCP Project
```bash
# Set GCP project
gcloud config set project mpesapipeline

# Create Cloud SQL instance
gcloud sql instances create mpesa-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-custom-4-16384 \
  --region=africa-south1

# Create database
gcloud sql databases create mpesa_analytics \
  --instance=mpesa-postgres

# Create user
gcloud sql users create data_engineer \
  --instance=mpesa-postgres \
  --password=SecurePassword123
```

#### 6.3 Migrate to Cloud SQL
```bash
# Export from local
pg_dump -h localhost -p 5433 -U data_engineer mpesa_analytics > backup.sql

# Import to Cloud SQL
gcloud sql import sql mpesa-postgres backup.sql \
  --database=mpesa_analytics

# Test connection
gcloud sql connect mpesa-postgres --user=data_engineer
```

### Phase 7: Production Deployment (Week 4-5)

#### 7.1 Create Docker Image
```bash
docker build -t gcr.io/mpesapipeline/mpesa-app:latest .
docker push gcr.io/mpesapipeline/mpesa-app:latest
```

#### 7.2 Deploy to Cloud Run
```bash
gcloud run deploy mpesa-app \
  --image=gcr.io/mpesapipeline/mpesa-app:latest \
  --platform managed \
  --region africa-south1 \
  --set-env-vars "DB_HOST=cloudsql:mpesapipeline:africa-south1:mpesa-postgres"
```

#### 7.3 Configure Load Balancer
```bash
# Create load balancer
gcloud compute backend-services create mpesa-backend \
  --protocol=HTTP \
  --global
```

### Phase 8: Monitoring & Alerting (Ongoing)

#### 8.1 Setup Cloud Monitoring
```bash
# Create dashboard
gcloud monitoring dashboards create --config-from-file=monitoring.yaml
```

#### 8.2 Create Alerts
- Database CPU > 80% → Alert
- Query latency p95 > 500ms → Alert
- Kafka consumer lag > 1000 → Alert
- Fraud detection spike > 10% → Alert

## ENVIRONMENT CONFIGURATION

### Required Environment Variables
```bash
# Database
DB_HOST=localhost
DB_PORT=5433
DB_NAME=mpesa_analytics
DB_USER=data_engineer
DB_PASSWORD=change_me

# Kafka
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=mpesa-transactions
KAFKA_GROUP_ID=mpesa-consumer-group

# Daraja API
DARAJA_CONSUMER_KEY=your_key_here
DARAJA_CONSUMER_SECRET=your_secret_here
DARAJA_BUSINESS_SHORTCODE=8759693
DARAJA_PASSKEY=your_passkey
DARAJA_ENVIRONMENT=sandbox

# GCP
GCP_PROJECT_ID=mpesapipeline
GCP_REGION=africa-south1
GCP_SQL_INSTANCE=mpesa-postgres

# Application
APP_ENV=production
APP_SECRET_KEY=your_secret_key
LOG_LEVEL=INFO
DOMAIN=chamayangu.online
```

## MONITORING & HEALTH CHECKS

### Health Endpoints
```
GET /health - Basic health check
GET /health/db - Database connection
GET /health/kafka - Kafka connectivity
GET /health/daraja - Daraja API connection
```

### Metrics
```
# PostgreSQL
SELECT count(*) FROM mpesa_transactions_raw;
SELECT count(DISTINCT phone_number) FROM mpesa_transactions_raw;
SELECT SUM(amount) FROM mpesa_transactions_raw WHERE DATE(transaction_time) = CURRENT_DATE;

# Kafka
kafka-topics --bootstrap-server localhost:9092 --topic mpesa-transactions --describe

# Performance
EXPLAIN ANALYZE SELECT * FROM mpesa_transactions_raw WHERE phone_number = '+254712345678';
```

## TROUBLESHOOTING

### Common Issues

1. **Kafka Consumer Lag**
   - Issue: Consumer falling behind
   - Solution: Increase num_consumer_threads or add more partitions

2. **Database Query Slow**
   - Issue: Slow transaction queries
   - Solution: Add indexes on (phone_number, transaction_time)

3. **Grafana No Data**
   - Issue: Dashboard shows no data
   - Solution: Verify PostgreSQL data source, check SQL in dashboard

4. **Fraud Detection Low Accuracy**
   - Issue: Model not detecting fraud
   - Solution: Retrain with more historical data, adjust thresholds

## PERFORMANCE TARGETS

```
✓ Latency: < 500ms (p95)
✓ Throughput: 1000+ transactions/minute
✓ Availability: 99.95% uptime
✓ Data freshness: < 5 minutes
✓ Fraud detection: > 95% accuracy
✓ Database response: < 100ms (p95)
✓ API availability: 99.9% uptime
```

## SECURITY CHECKLIST

```
✓ Enable SSL/TLS encryption
✓ Configure API rate limiting
✓ Enable HMAC request signing
✓ Mask sensitive data in logs
✓ Setup audit logging
✓ Configure IP whitelisting
✓ Enable database encryption
✓ Rotate secrets monthly
✓ Monitor fraud detection alerts
✓ Review access logs daily
```

## BACKUP & DISASTER RECOVERY

```bash
# Daily backup (automated)
0 2 * * * gcloud sql backups create mpesa-backup \
    --instance=mpesa-postgres

# Monthly archival
0 3 1 * * gsutil cp gs://mpesapipeline-backups/* \
    gs://mpesapipeline-archive/

# Test restore (weekly)
# gcloud sql backups restore timestamp --backup-instance=mpesa-postgres
```

## CONTACTS & SUPPORT

- Email: kiprutovictor39@gmail.com
- Phone: +254 723 484 552
- Domain: chamayangu.online
- GCP Project: mpesapipeline

---

**Last Updated:** May 15, 2026
**Status:** Production Ready
**Version:** 1.0
