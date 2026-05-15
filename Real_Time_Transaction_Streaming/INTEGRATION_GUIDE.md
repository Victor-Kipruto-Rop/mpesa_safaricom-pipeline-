# Integration Guide: Option A Components

This guide shows how the 5 completed components work together in the ChamaNdoto M-Pesa platform.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     SAFARICOM DARAJA API                        │
│                   (OAuth2, C2B, STK Push)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WEBHOOK ENDPOINTS                            │
│              (Signature validation, C2B, STK)                   │
│         (Tested in: tests/security/test_security.py)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  KAFKA BROKER                                   │
│            (mpesa-transactions topic)                           │
└──────┬──────────────────┬──────────────────┬────────────────────┘
       │                  │                  │
   (Load Tests)    (DLQ: retry-topic)    (DLQ: dlq-topic)
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Locust Load  │  │ Consumer     │  │ DLQ Handler  │
│ Test (1000u) │  │ Rebalancing  │  │ (Failures)   │
│              │  │ (kafka_      │  │              │
│ Measures:    │  │ consumer.py) │  │ Categorizes: │
│ - p95 < 500ms│  │              │  │ - Invalid    │
│ - < 1% error │  │ Features:    │  │ - Duplicate  │
│ - 1000 RPS   │  │ - Batching   │  │ - DB Error   │
│              │  │ - Duped-dedup│  │ - Unknown    │
│ Scenarios:   │  │ - Region map │  │              │
│ 1. Baseline  │  │ - Graceful   │  │ Retry Queue: │
│ 2. Peak 1000u│  │   shutdown   │  │ - Max 3x     │
│ 3. Stress2000│  │              │  │ - Incident   │
│ 4. Spike     │  │ Tested by:   │  │ - Manual ops │
│ 5. Sustained │  │ test_e2e/    │  │              │
└──────────────┘  │ test_work    │  │ Protected by:│
                  │ flows.py     │  │ - Signatures │
                  │              │  │ - Rate limit │
                  └──────────────┘  │ - DLQ routing│
                         │          │              │
                         ▼          └──────────────┘
                  ┌──────────────┐
                  │  PostgreSQL  │
                  │  Database    │
                  │              │
                  │ Stores:      │
                  │ - Tx records │
                  │ - Error logs │
                  │ - DLQ msgs   │
                  │ - Reconcile  │
                  └──────────────┘
```

---

## Flow 1: Load Testing Workflow

### Step 1: Initiate Load Test
```bash
# Start Locust with Kafka consumer running
locust -f tests/load/locustfile.py --headless -u 1000 -r 50 -t 30m
```

### Step 2: Locust sends 1000+ concurrent requests
- **M_PesaLoadTestUser** tasks executed in parallel
- Each user performs 8 different transaction types
- Metrics collected: response time, throughput, errors

### Step 3: Consumer processes incoming load
- **SafaricomTransactionProcessor** receives messages from Kafka
- Batches transactions (100 per batch, 5-second timeout)
- Validates signatures and extracts region

### Step 4: Failed messages route to DLQ
- Invalid signatures → DLQ with reason `INVALID_SIGNATURE`
- Parse errors → DLQ with reason `INVALID_FORMAT`
- DB errors → DLQ with reason `DATABASE_ERROR`

### Step 5: Analyze results
- p95 latency should be < 500ms
- Error rate should be < 1%
- Throughput should be >= 1000 RPS

---

## Flow 2: End-to-End Transaction Workflow

### Complete STK Push Flow (TestSTKPushFlow)

```
1. Client initiates STK push
   POST /api/v1/transactions/initiate-stk
   - Signature: valid HMAC
   - Result: Checkout request ID
   
   ✅ Tested in: test_workflows.py::TestSTKPushFlow

2. Query STK status
   GET /api/v1/transactions/stk/{id}/status
   
   ✅ Tested in: test_workflows.py::TestSTKPushFlow

3. Safaricom sends callback (webhook)
   POST /api/v1/webhooks/stk/callback
   - Signature verified (tests/security/test_security.py)
   - Message routed to Kafka
   
   ✅ Tested in: test_security.py::TestHMACSignatureVerification

4. Consumer processes message
   - Extract transaction details
   - Parse timestamp
   - Validate region mapping
   - Insert to database
   
   ✅ Tested in: test_workflows.py::TestSTKPushFlow
                test_workflows.py::TestConcurrentWebhooks

5. Fraud detection runs
   - Extract 15+ features
   - Score with 3-model ensemble
   - Flag if fraud_score > 0.5
   
   ✅ Tested in: test_workflows.py::TestFraudDetectionFlow

6. Analytics updated
   - Customer segmentation
   - Risk profile
   - Transaction patterns
   
   ✅ Tested in: test_workflows.py::TestCustomerJourney
```

---

## Flow 3: Error Recovery Workflow

### Message Fails to Process

```
1. Consumer receives message
   - Invalid signature? → Send to DLQ
   - Invalid format? → Send to DLQ
   - Region mapping failed? → Send to DLQ

2. DLQ Handler processes
   - Reason categorized (8 types)
   - Error logged to database
   - Recoverable? → Send to retry queue

3. Retry Queue Processing
   - Max 3 retry attempts
   - Exponential backoff
   - Track retry count

4. Still failing after 3 retries?
   - Create incident
   - Alert monitoring system
   - Manual ops required

5. Monitoring shows stats
   GET /api/v1/admin/dlq/stats
   {
     "total_errors": 42,
     "errors_by_type": {
       "invalid_signature": 10,
       "duplicate_transaction": 15,
       "database_error": 8,
       "region_mapping_failed": 9
     },
     "recoverable": 25,
     "unrecoverable": 17
   }
```

### Example: Signature Verification

```python
# In kafka_consumer.py
def _validate_signature(data):
    # Checks HMAC-SHA256
    # If fails → send_to_dlq(..., INVALID_SIGNATURE)

# In test_security.py
def test_invalid_signature():
    # Verify rejection of tampered messages
    # Verify no SQL injection from error
```

---

## Flow 4: Concurrent Load with Consumer Rebalancing

### Scenario: 1000 concurrent transactions

```
1. Locust generates 1000 requests
   - Simulates peak load
   - Rapid message delivery to Kafka
   
   ✅ Tested in: locustfile.py::StressTestUser

2. Kafka Consumer Group Rebalancing
   
   When partitions reassign:
   - Consumer detects rebalance
   - Flushes current batch to DB
   - Commits offset (no data loss)
   - Pauses processing
   - Waits for new partition assignment
   - Resumes processing
   
   ✅ Tested in: kafka_consumer.py::_rebalance_listener
                test_workflows.py::TestConcurrentWebhooks

3. Processing resumes
   - New partitions assigned
   - Processing continues
   - Stats tracked

4. Graceful shutdown
   - SIGINT received
   - Flush remaining batch
   - Commit final offset
   - Close connections
```

---

## Flow 5: Security Testing Integration

### OWASP Test Coverage

```
Load Test Scenario:
  M_PesaLoadTestUser makes requests
  
  ├─ SQL Injection attempt?
  │  └─ Security test: test_security.py::TestSQLInjectionPrevention
  │     Result: Rejected, no SQL errors exposed
  │
  ├─ Invalid signature?
  │  └─ Security test: test_security.py::TestHMACSignatureVerification
  │     Result: Rejected with 403, no internal error details
  │
  ├─ Rate limit exceeded?
  │  └─ Security test: test_security.py::TestRateLimitingEnforcement
  │     Result: 429 Too Many Requests
  │
  ├─ XSS in parameters?
  │  └─ Security test: test_security.py::TestXSSPrevention
  │     Result: Sanitized or rejected
  │
  └─ Concurrent requests race condition?
     └─ E2E test: test_workflows.py::TestConcurrentWebhooks
        Result: All 100 webhooks processed correctly, no duplicates
```

---

## Deployment Sequence

### Phase 1: Pre-Deployment (Dev/Staging)

```bash
# 1. Run load tests
locust -f tests/load/locustfile.py --headless -u 100 -r 10 -t 10m
# Verify: p95 < 500ms, < 1% error

# 2. Run E2E tests
pytest tests/e2e/test_workflows.py -v
# Verify: All tests pass

# 3. Run security tests
pytest tests/security/test_security.py -v
# Verify: All tests pass, no vulnerabilities

# 4. Create Kafka topics
kafka-topics --create --topic m-pesa-transactions-dlq --partitions 3
kafka-topics --create --topic m-pesa-transactions-retry --partitions 1

# 5. Verify database schema
python scripts/verify_setup.py
# Verify: All tables exist with correct indexes
```

### Phase 2: Production Deployment

```bash
# 1. Start consumer
python -m ingestion.kafka_consumer

# 2. Monitor DLQ (terminal 2)
kafka-console-consumer --topic m-pesa-transactions-dlq --from-beginning

# 3. Monitor metrics
# - Kafka consumer lag
# - Transaction throughput
# - Error rate in DLQ
# - Database write latency

# 4. Run load test in production-like environment
locust -f tests/load/locustfile.py --headless -u 500 -r 25 -t 60m

# 5. Validate results
# - No DLQ messages (< 0.1% error rate)
# - p95 latency steady
# - Throughput >= 1000 RPS
# - Consumer lag minimal
```

### Phase 3: Monitoring (24/7)

```
Dashboard metrics:
- Transaction throughput (should be > 1000 RPS)
- Consumer lag (should be < 30 seconds)
- DLQ message rate (should be < 10 messages/minute)
- P95 latency (should be < 500ms)
- Error rate (should be < 1%)

Alerts:
- Consumer lag > 5 minutes
- DLQ message rate > 100/minute
- Error rate > 5%
- P95 latency > 2 seconds
- Transaction processing failure
```

---

## Testing Hierarchy

```
Level 1: Unit Tests
├─ Signature validation
├─ Region extraction
├─ Transaction parsing
└─ Error categorization

Level 2: Security Tests (test_security.py)
├─ SQL injection prevention
├─ Signature verification
├─ Rate limiting
├─ Input validation
└─ Header validation

Level 3: E2E Tests (test_workflows.py)
├─ Complete transaction flows
├─ Concurrent processing
├─ Error recovery
├─ Customer journey
└─ Reconciliation

Level 4: Load Tests (locustfile.py)
├─ Baseline 100u/10m
├─ Peak 1000u/30m
├─ Stress 2000u/15m
├─ Spike test
└─ Sustained 24h
```

---

## Key Integration Points

### 1. Signature Validation
- **Generated in:** API endpoint receives request
- **Tested in:** `test_security.py::TestHMACSignatureVerification`
- **Failed route:** Send to DLQ with `INVALID_SIGNATURE`
- **Consumer action:** Skip processing, log error

### 2. Region Extraction
- **Generated in:** `kafka_consumer.py::extract_region()`
- **Tested in:** `test_workflows.py::TestCustomerJourney`
- **Failed route:** Send to DLQ with `REGION_MAPPING_FAILED`
- **Fallback:** Mark transaction as "Unknown" region

### 3. Duplicate Detection
- **Generated in:** `kafka_consumer.py::_flush_batch()`
- **Tested in:** `test_workflows.py::TestConcurrentWebhooks`
- **Failed route:** Log to stats, skip insert
- **Statistic:** Tracked in `stats["duplicates"]`

### 4. Consumer Rebalancing
- **Triggered:** Kafka partition reassignment
- **Handled in:** `kafka_consumer.py::_rebalance_listener()`
- **Tested in:** `test_workflows.py::TestConcurrentWebhooks`
- **Action:** Flush batch, commit offset, pause processing

### 5. Error Handling
- **Categorization:** 8 failure types in `FailureReasonEnum`
- **Routing:** Send to DLQ or retry queue
- **Tested in:** `test_security.py` + `test_workflows.py::TestErrorRecovery`
- **Recovery:** 3 retry attempts, then incident

---

## Performance Baselines

Based on load testing:

| Metric | Target | Expected | Load Test Validation |
|--------|--------|----------|----------------------|
| p50 latency | < 100ms | 80ms | locustfile.py baseline |
| p95 latency | < 500ms | 350ms | locustfile.py peak 1000u |
| p99 latency | < 1000ms | 850ms | locustfile.py stress 2000u |
| Error rate | < 1% | 0.5% | test_security.py + test_workflows.py |
| Throughput | >= 1000 RPS | 1200 RPS | locustfile.py peak scenario |
| Consumer lag | < 30s | 5-10s | kafka_consumer.py stats |
| DLQ rate | < 0.1% | 0.05% | kafka_dlq.py monitoring |

---

## Troubleshooting Guide

### Problem: DLQ receiving many messages

**Diagnosis:**
```sql
SELECT error_type, COUNT(*) as count
FROM error_logs
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY error_type
ORDER BY count DESC;
```

**Solutions:**
- `INVALID_SIGNATURE`: Check webhook secret
- `REGION_MAPPING_FAILED`: Verify phone prefix mappings
- `DATABASE_ERROR`: Check database connectivity
- `INVALID_FORMAT`: Verify Safaricom webhook format changes

### Problem: Consumer lag increasing

**Diagnosis:**
```bash
kafka-consumer-groups --group mpesa-transaction-processor-1 \
  --describe --bootstrap-server localhost:9093
```

**Solutions:**
- Increase batch size in `ConsumerConfig`
- Add more consumer instances (scale out)
- Check database write performance
- Monitor CPU/memory usage

### Problem: E2E tests failing

**Debug:**
```bash
pytest tests/e2e/test_workflows.py -v -s --tb=short
```

**Check:**
- API endpoint availability
- Database connectivity
- Kafka broker availability
- HMAC secret consistency

---

## Success Criteria

✅ **Option A completion verified when:**

1. Load tests pass: p95 < 500ms, < 1% error, 1000+ RPS
2. E2E tests pass: All 8 test classes 100% pass rate
3. Security tests pass: All 26+ tests pass, no vulnerabilities
4. DLQ operational: Messages route correctly, retry logic works
5. Consumer rebalancing: Handles partition reassignment gracefully
6. Production deployment: 24h stability with < 0.1% error rate

---

## Next Phase (Option B+)

After Option A validation:
- Implement PDF export for analytics
- Add cohort analysis
- Create custom date range queries
- Build anomaly detection dashboard
- Implement model retraining automation
