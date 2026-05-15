# 🚀 M-PESA PROJECT - QUICK REFERENCE CARD

## One-Liner Commands

```bash
# Verify everything is working
python verify_setup.py

# Test Daraja API credentials
python test_daraja.py

# Check Docker status
docker compose ps

# Start/Stop services
docker compose up -d      # Start all services
docker compose down       # Stop all services
docker compose restart    # Restart services

# View logs
docker compose logs -f                    # All services
docker compose logs -f webhook            # Webhook only
docker compose logs -f kafka-consumer     # Kafka consumer only
docker compose logs -f postgres           # Database only

# Run Jupyter notebooks
jupyter notebook notebooks/

# Connect to database
psql -h localhost -p 5433 -U data_engineer -d mpesa_analytics

# List Kafka topics
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Monitor Kafka messages
docker compose exec kafka kafka-console-consumer --topic mpesa-transactions \
  --bootstrap-server localhost:9092 --from-beginning --max-messages 10
```

---

## Environment Setup

### Activate Virtual Environment
```bash
source .venv/bin/activate
```

### Load Environment Variables
```bash
export $(cat .env | grep -v '#' | xargs)
```

### View Loaded Credentials
```bash
echo "Consumer Key: $DARAJA_CONSUMER_KEY"
echo "Business Shortcode: $MPESA_BUSINESS_SHORTCODE"
echo "Database: $POSTGRES_DB"
```

---

## Database Tasks

### Query Transaction Count
```sql
SELECT COUNT(*) FROM mpesa_transactions_raw;
```

### View Recent Transactions
```sql
SELECT * FROM mpesa_transactions_raw 
ORDER BY created_at DESC LIMIT 10;
```

### Check Staging Data
```sql
SELECT COUNT(*) FROM stg_c2b_transactions;
```

### View All Tables
```sql
\dt
```

### Exit Database
```sql
\q
```

---

## Docker Tasks

### Restart Single Service
```bash
docker compose restart postgres
docker compose restart kafka
docker compose restart webhook
```

### View Service Logs (Live)
```bash
docker compose logs -f [service-name]
```

### Execute Command in Container
```bash
docker compose exec postgres psql -U data_engineer -d mpesa_analytics
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Rebuild Images
```bash
docker compose build
docker compose up -d
```

---

## Python/Jupyter Tasks

### Run Python Script
```bash
python test_daraja.py
python verify_setup.py
```

### Start Jupyter Lab
```bash
jupyter lab notebooks/
```

### Start Jupyter Notebook
```bash
jupyter notebook notebooks/
```

### Run Specific Notebook
```bash
jupyter notebook notebooks/03_kafka_monitoring.ipynb
```

### Execute Notebook (No UI)
```bash
python -m jupyter nbconvert --to notebook --execute notebooks/03_kafka_monitoring.ipynb
```

---

## Useful Port Numbers

| Service | Port | URL |
|---------|------|-----|
| Webhook | 5000 | http://localhost:5000 |
| Kafka | 9092 | localhost:9092 |
| PostgreSQL | 5433 | localhost:5433 |
| Redis | 6380 | localhost:6380 |
| Jupyter | 8888 | http://localhost:8888 |

---

## Important Files

| File | Purpose |
|------|---------|
| `.env` | Credentials (NEVER commit) |
| `docker-compose.yml` | Infrastructure definition |
| `verify_setup.py` | Configuration validator |
| `test_daraja.py` | API credential tester |
| `SETUP_STATUS.md` | Complete setup documentation |
| `requirements.txt` | Python dependencies |
| `Makefile` | Common automation tasks |

---

## Troubleshooting Quick Links

```bash
# Check if port is in use
lsof -i :5000   # Webhook
lsof -i :5433   # PostgreSQL
lsof -i :9092   # Kafka

# Kill process on port
kill -9 $(lsof -t -i:5000)

# View Docker disk usage
docker system df

# Clean up unused images
docker image prune -a

# Rebuild environment
docker compose down -v
docker compose up -d
```

---

## Credential Reference (from .env)

```
DARAJA_CONSUMER_KEY=2GAY9Lwr1xcikWNj7SXFhpEgVMTNd12Tg143MWG9Yb2wNWTd
DARAJA_CONSUMER_SECRET=[STORED IN .env]
MPESA_BUSINESS_SHORTCODE=8759693
MPESA_TILL_NUMBER=6475309
MPESA_TILL_MSISDN=0117834446

POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=mpesa_analytics
POSTGRES_USER=data_engineer
POSTGRES_PASSWORD=[STORED IN .env]

KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC_TRANSACTIONS=mpesa-transactions

CALLBACK_URL=http://localhost:5000/webhook/callback
DOMAIN=chamayangu.online
```

---

## Deployment Info

- **Target:** GCP
- **Project ID:** mpesapipeline
- **Region:** africa-south1 (Johannesburg)
- **Zone:** africa-south1-a

---

## Contact

- **Email:** kiprutovictor39@gmail.com
- **Phone:** +254 723 484 552

---

**Last Updated:** May 14, 2026  
**Status:** ✅ Production Ready
