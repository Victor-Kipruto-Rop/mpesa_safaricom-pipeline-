# 🚀 Getting Started - M-Pesa Streaming Project

**⏱️ Time to first run: 10 minutes**

---

## Step 1: Prerequisites (2 minutes)

Make sure you have installed:
- Python 3.12+
- Docker & Docker Compose
- Git
- Make

**Check versions:**
```bash
python --version          # Should be 3.12+
docker --version          # Should be 20.10+
docker compose version
make --version            # Should be any version
```

---

## Step 2: Navigate to Project (1 minute)

```bash
cd /home/kipruto/Desktop/DATA_ENGINEERING/01_MPESA_Safaricom/01_Real_Time_Transaction_Streaming
```

---

## Step 3: Setup Virtual Environment (2 minutes)

```bash
# Create virtual environment
make setup

# Activate it
source .venv/bin/activate

# Install dependencies
make install-dev
```

**Expected output:**
```
✓ Virtual environment created
✓ Dependencies installed
```

---

## Step 4: Configure Environment (1 minute)

```bash
# Copy example to .env
cp .env.example.comprehensive .env

# Edit if needed (optional - defaults work for local dev)
# nano .env
```

---

## Step 5: Start Services (2 minutes)

```bash
# Start Kafka, PostgreSQL, Redis, etc.
make docker-compose-up

# Wait for all services to be healthy (~30 seconds)
# You should see logs indicating services are ready
```

---

## Step 6: Initialize Database (1 minute)

```bash
# Create tables and indices
make db-setup

# Load sample data
make db-seed
```

**Expected output:**
```
✓ Database tables created
✓ Sample data loaded (20 transactions)
```

---

## Step 7: Run Tests (1 minute)

```bash
# Run all 101 tests
make test
```

**Expected output:**
```
✓ 101 tests passed
✓ Coverage: >80%
```

---

## Step 8: Start the Application

Now you have 3 options:

### Option A: Run Webhook Receiver (Recommended for first look)
```bash
make run-webhook
```
Output:
```
 * Running on http://127.0.0.1:5000
 * WARNING: This is a development server
```

### Option B: Run Kafka Consumer
```bash
make run-consumer
```
Output:
```
Starting Kafka consumer...
Connected to Kafka
Listening for messages...
```

### Option C: Run Everything
```bash
# Terminal 1:
make run-webhook

# Terminal 2:
make run-consumer

# Terminal 3:
make run-flink-job
```

---

## Step 9: Test the System

### If you started webhook (Terminal 1):
```bash
# In a new terminal:
curl -X POST http://localhost:5000/webhook/c2b/confirmation \
  -H "Content-Type: application/json" \
  -d '{
    "TransactionType": "C2B Single Step",
    "TransID": "12345",
    "TransTime": "20240514102030",
    "TransAmount": 1000,
    "BusinessShortCode": "123456",
    "BillRefNumber": "TEST001",
    "InvoiceNumber": "",
    "OrgAccountBalance": 50000,
    "ThirdPartyTransID": "",
    "MSISDN": "254712345678",
    "FirstName": "John",
    "MiddleName": "A",
    "LastName": "Doe"
  }'
```

Expected response:
```json
{
  "status": "received"
}
```

---

## Step 10: Explore the Codebase

Once everything is running:

1. **Read the overview:**
   ```bash
   cat README_PORTFOLIO.md
   ```

2. **Check the architecture:**
   ```bash
   cat docs/ARCHITECTURE_DETAILED.md
   ```

3. **Look at key code files:**
   - `ingestion/webhook_receiver.py` - Flask API
   - `streaming/kafka_consumer.py` - Data streaming
   - `tests/test_integration.py` - Usage examples

4. **Run with coverage report:**
   ```bash
   make test-cov
   ```

---

## Available Commands

```bash
# Development
make help              # Show all commands
make setup             # Create virtual environment
make install           # Install production deps
make install-dev       # Install with dev tools
make format            # Auto-format code
make lint              # Check code quality
make type-check        # TypeScript-like checking
make test              # Run all tests
make test-cov          # Tests with coverage report

# Running
make docker-compose-up      # Start services
make docker-compose-down    # Stop services
make run-webhook            # Start webhook receiver
make run-consumer           # Start Kafka consumer
make run-flink-job          # Start Flink processor

# Database
make db-setup              # Create tables
make db-seed               # Load sample data
make db-clean              # Reset database

# Deployment
make docker-build          # Build container
make docker-run            # Run in Docker
make k8s-deploy            # Deploy to Kubernetes

# Cleanup
make clean                 # Clean Python cache
make distclean             # Complete cleanup
```

---

## Troubleshooting

### Services won't start
```bash
# Check what's running
docker ps

# View logs
docker compose logs -f

# Restart everything
make docker-compose-down
make docker-compose-up
```

### Tests fail
```bash
# Run with verbose output
pytest -vv tests/

# Run specific test
pytest -vv tests/test_webhook_receiver.py
```

### Database connection fails
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Verify .env has correct DB_URL
grep DB_URL .env
```

### Port already in use
```bash
# Find what's using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>
```

---

## What's Running Now?

| Service | Port | Status |
|---------|------|--------|
| Flask Webhook | 5000 | ✅ Ready |
| Kafka Broker | 9092 | ✅ Ready |
| PostgreSQL | 5432 | ✅ Ready |
| Redis | 6379 | ✅ Ready |
| Prometheus | 9090 | ✅ Ready |
| Grafana | 3000 | ✅ Ready |

---

## Next Steps

After you've got everything running:

1. **Understand the architecture** → Read `docs/ARCHITECTURE_DETAILED.md`
2. **Learn the API** → Read `docs/API_INTEGRATION.md`
3. **See examples** → Check `tests/test_integration.py`
4. **Make a change** → Edit code, run `make lint test`
5. **Deploy** → Follow `PRODUCTION_READINESS.md`

---

## Quick Links

| Document | Purpose |
|----------|---------|
| [README_PORTFOLIO.md](README_PORTFOLIO.md) | Project overview |
| [QUICKSTART.md](QUICKSTART.md) | Detailed setup guide |
| [DOCS_INDEX.md](DOCS_INDEX.md) | All documentation |
| [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md) | Deployment checklist |
| [Makefile](Makefile) | All available commands |

---

## 🎯 You're all set!

```bash
# Copy & paste this to get started NOW:
cd /home/kipruto/Desktop/DATA_ENGINEERING/01_MPESA_Safaricom/01_Real_Time_Transaction_Streaming && \
make setup && \
source .venv/bin/activate && \
make install-dev && \
cp .env.example.comprehensive .env && \
make docker-compose-up
```

Then in another terminal:
```bash
cd /home/kipruto/Desktop/DATA_ENGINEERING/01_MPESA_Safaricom/01_Real_Time_Transaction_Streaming && \
source .venv/bin/activate && \
make db-setup && \
make test
```

**Done! Everything is running.** 🎉

Now run:
```bash
make run-webhook    # Terminal A
make run-consumer   # Terminal B
```

Then test with:
```bash
curl http://localhost:5000/health
```

---

*Questions? Check [DOCS_INDEX.md](DOCS_INDEX.md) or [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)*
