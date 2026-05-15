# QUICK START GUIDE

> **M-Pesa Streaming Project 1 - Get Running in 10 Minutes**

## ⚡ TL;DR - Fastest Path

```bash
# 1. Setup (3 minutes)
make setup && source .venv/bin/activate && make install-dev

# 2. Configure (1 minute)
cp .env.example.comprehensive .env
# Edit .env with your values (or use defaults for local testing)

# 3. Start services (2 minutes)
make docker-compose-up
docker compose logs -f  # Wait for services to be ready

# 4. Initialize database (2 minutes)
make db-setup
make db-seed

# 5. Run tests (2 minutes)
make test

# 6. Start streaming (run in separate terminals)
make run-webhook    # Terminal A
make run-consumer   # Terminal B
```

**Total Time: ~10 minutes to fully running system** ⏱️

---

## 📋 PREREQUISITES

### Required
- **Python 3.12+**
- **Docker & Docker Compose**
- **PostgreSQL 15** (via Docker, or local)
- **Kafka 7.5** (via Docker)

### Optional but Recommended
- **Git** (for version control)
- **curl** (for testing endpoints)
- **psql** (PostgreSQL CLI)

### Check Installation
```bash
python3 --version       # Should be 3.12+
docker --version        # Should be 20.10+
docker compose version
```

---

## 🚀 STEP-BY-STEP SETUP

### Step 1: Clone Repository
```bash
cd /home/kipruto/Desktop/DATA_ENGINEERING/01_MPESA_Safaricom
cd 01_Real_Time_Transaction_Streaming

# Or clone if not already present
# git clone <your-repo-url> && cd mpesa-streaming
```

### Step 2: Create Virtual Environment
```bash
# Create venv
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Or use Makefile (shorthand)
make setup && source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Production only
make install

# With development tools (recommended)
make install-dev
```

### Step 4: Configure Environment
```bash
# Copy template
cp .env.example.comprehensive .env

# Edit with your values (optional for local development)
nano .env  # Or use your editor

# Key variables for local testing:
ENVIRONMENT=development
POSTGRES_HOST=localhost
POSTGRES_USER=mpesa_user
POSTGRES_PASSWORD=your_password
KAFKA_BROKERS=localhost:9092
LOG_LEVEL=INFO
```

### Step 5: Start Local Services
```bash
# Start Kafka, PostgreSQL, Redis, Airflow
make docker-compose-up

# Check status
docker compose ps

# Watch logs
docker compose logs -f postgres  # Wait for "ready to accept connections"
```

### Step 6: Initialize Database
```bash
# Create schema and tables
make db-setup

# Load sample data
make db-seed

# Verify
psql -h localhost -U mpesa_user -d mpesa_dw \
  -c "SELECT COUNT(*) FROM mpesa_transactions_raw;"
# Should return: count = 20 (from sample data)
```

### Step 7: Run Tests
```bash
# All 101 tests
make test

# With coverage report
make test-cov

# Expected output: 101 passed in ~30s
```

### Step 8: Start Streaming Services

**Terminal A - Webhook Receiver:**
```bash
source .venv/bin/activate
make run-webhook
# Output: " * Running on http://127.0.0.1:5000"
```

**Terminal B - Kafka Consumer:**
```bash
source .venv/bin/activate
make run-consumer
# Output: "Consumer started, waiting for messages..."
```

### Step 9: Test End-to-End

**Terminal C - Send test transaction:**
```bash
# Health check
curl http://localhost:5000/health
# Expected: {"status": "healthy", ...}

# Send test transaction
curl -X POST http://localhost:5000/webhook/c2b/confirmation \
  -H "Content-Type: application/json" \
  -d '{
    "TransactionType": "C2B Payment",
    "TransID": "TEST001",
    "TransTime": "20240514103000",
    "TransAmount": 500.00,
    "BusinessShortCode": "174379",
    "BillRefNumber": "INV-0001",
    "InvoiceNumber": "",
    "MSISDN": "254712345678"
  }'

# Expected: {"status": "received"}
```

### Step 10: Verify Data Pipeline

```bash
# Check PostgreSQL
psql -h localhost -U mpesa_user -d mpesa_dw \
  -c "SELECT * FROM mpesa_transactions_raw ORDER BY created_at DESC LIMIT 1;"

# Check Kafka
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic mpesa-transactions \
  --from-beginning \
  --max-messages 1 \
  --timeout-ms 5000

# View Grafana dashboard
open http://localhost:3000
# Login: admin / admin
```

---

## 🎯 COMMON TASKS

### Run Code Quality Checks
```bash
make check          # All checks
make lint           # Flake8
make format         # Auto-format
make type-check     # MyPy
make security       # Bandit
```

### Run Specific Tests
```bash
make test                    # All tests
make test-cov               # With coverage
make test-integration       # Integration only

# Or use pytest directly
pytest tests/test_webhook_receiver.py -v  # Specific file
pytest tests/ -k "test_producer" -v       # Specific test pattern
```

### Useful Makefile Targets
```bash
make help               # Show all available commands
make docker-compose-up # Start services
make docker-compose-down # Stop services
make db-setup          # Initialize database
make db-seed           # Load sample data
make run-webhook       # Start webhook receiver
make run-consumer      # Start Kafka consumer
make clean             # Remove cache/temp files
```

### View Logs
```bash
# Docker Compose services
docker compose logs -f postgres      # PostgreSQL
docker compose logs -f kafka         # Kafka
docker compose logs -f zookeeper     # Zookeeper

# Application logs
tail -f logs/application.log

# Combined
docker compose logs -f
```

### Connect to Services

**PostgreSQL:**
```bash
psql -h localhost -U mpesa_user -d mpesa_dw
# Commands:
\dt              # List tables
SELECT * FROM mpesa_transactions_raw LIMIT 5;
\q               # Quit
```

**Kafka CLI:**
```bash
# Describe topic
docker compose exec kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic mpesa-transactions

# Consumer group status
docker compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group mpesa_consumer_group \
  --describe
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Port 5000 already in use"
```bash
# Kill process using port 5000
lsof -i :5000
kill -9 <PID>

# Or use different port
FLASK_PORT=5001 make run-webhook
```

### Issue: "Connection refused" to PostgreSQL
```bash
# Check if container is running
docker compose ps

# Restart PostgreSQL
docker compose restart postgres

# Check logs
docker compose logs postgres
```

### Issue: "Kafka broker not available"
```bash
# Restart Kafka
docker compose restart kafka zookeeper

# Check connectivity
docker compose exec kafka kafka-broker-api-versions \
  --bootstrap-server localhost:9092
```

### Issue: Tests fail with "ImportError"
```bash
# Reinstall dependencies
make clean
make install-dev

# Run tests again
make test
```

### Issue: "psycopg2 connection pool exhausted"
```bash
# Increase pool size in .env
DB_POOL_MAX_SIZE=30

# Or reduce batch size
MESSAGE_BATCH_SIZE=25
```

---

## 📊 MONITORING

### Real-Time Metrics
```bash
# Prometheus metrics (if enabled)
curl http://localhost:8000/metrics

# Health check
curl http://localhost:5000/health
```

### Grafana Dashboards
```bash
# Access
open http://localhost:3000

# Login: admin / admin

# Dashboards available:
- M-Pesa Transaction Overview
- System Health
- Performance Metrics
```

### Check Kafka Lag
```bash
docker compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group mpesa_consumer_group \
  --describe
```

---

## 🚀 NEXT STEPS

### Run Full CI/CD Locally
```bash
make all    # Equivalent to CI pipeline
```

### Build Docker Image
```bash
make docker-build
make docker-run
```

### Deploy to Kubernetes (optional)
```bash
# Requires minikube or K8s cluster
kubectl apply -f k8s/
kubectl get pods
```

### Review Documentation
- [README_PORTFOLIO.md](README_PORTFOLIO.md) - Overview
- [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md) - Deployment guide
- [docs/ARCHITECTURE_DETAILED.md](docs/ARCHITECTURE_DETAILED.md) - System design
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Issue resolution

---

## ✅ SUCCESS CHECKLIST

After following this guide, you should have:

- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Environment configured (.env)
- [ ] Docker services running (Kafka, PostgreSQL, etc.)
- [ ] Database initialized with schema
- [ ] Sample data loaded (20 transactions)
- [ ] All 101 tests passing
- [ ] Webhook receiver running on port 5000
- [ ] Kafka consumer running
- [ ] Test transaction sent successfully
- [ ] Data visible in PostgreSQL
- [ ] Grafana dashboards accessible

---

## 💡 TIPS & TRICKS

### Faster Iteration
```bash
# Watch tests (auto-rerun on file change)
make test-watch

# Format code on save (with file watcher)
# Or just run: make format
```

### Development Workflow
```bash
# 1. Make changes to code
nano ingestion/webhook_receiver.py

# 2. Format and lint
make format
make lint

# 3. Run tests
make test

# 4. Commit
git add .
git commit -m "feat: add feature"
```

### Performance Profiling
```bash
# Run with profiling
python -m cProfile -s cumulative -m ingestion.webhook_receiver

# Generate flame graph
pip install py-spy
py-spy record -o profile.svg -- make run-webhook
```

---

## 📞 GETTING HELP

1. **Read Docs**: Start with [README_PORTFOLIO.md](README_PORTFOLIO.md)
2. **Check Troubleshooting**: See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. **Review Code**: Comments in Python files explain complex logic
4. **Run Tests**: Test files show examples of how to use modules
5. **Check Logs**: Application logs often reveal issues

---

**Ready to start?** Run: `make setup && source .venv/bin/activate && make help`

**Happy coding! 🚀**
