# 📋 REQUIREMENTS FROM YOU - M-Pesa Streaming Pipeline

> **Complete this checklist to get the project fully operational**

---

## 🔐 1. SAFARICOM DARAJA API CREDENTIALS (Required)

These must be obtained from https://developer.safaricom.co.ke

### 1.1 Daraja App Credentials
```
Consumer Key:           ___________________________________
Consumer Secret:        ___________________________________
```

**How to get:**
1. Go to https://developer.safaricom.co.ke
2. Sign up / Login
3. Create new app (M-Pesa Sandbox or Production)
4. Copy Consumer Key and Consumer Secret

### 1.2 M-Pesa Business Details
```
Business Shortcode:     ___________________________________
                        (Example: 174379 for sandbox)
                        
Lipa Na M-Pesa Passkey: ___________________________________
                        (32-character alphanumeric key)
```

**How to get:**
1. Register M-Pesa account with Safaricom
2. Request Paybill or Till number
3. Generate Lipa Na M-Pesa Passkey from Safaricom portal

### 1.3 Webhook/Callback URL (Required)
```
Public Callback URL:    ___________________________________
                        Example: https://yourdomain.com/webhook/c2b/confirmation
                        
Note: Must be HTTPS in production
      For local testing use: http://localhost:5000
```

---

## 🌐 2. NETWORK & DEPLOYMENT

### 2.1 Production Deployment (Optional)
```
Cloud Provider:         □ AWS  □ GCP  □ Azure  □ Other: _______

Domain Name:            ___________________________________
                        (If deploying to cloud)

SSL Certificate:        □ Self-signed  □ Let's Encrypt  □ Commercial: _______
```

### 2.2 Firewall & Security
```
Allowed IP Ranges:      ___________________________________
                        (For webhook calls from Safaricom)
                        Safaricom IPs: Contact support

VPN Required:           □ Yes  □ No

Firewall Rules:         □ Port 5000 (Webhook) - Allow
                        □ Port 9092 (Kafka) - Internal only
                        □ Port 5432 (PostgreSQL) - Internal only
                        □ Port 6379 (Redis) - Internal only
```

---

## 💾 3. DATABASE CONFIGURATION (Optional - Defaults Provided)

### 3.1 PostgreSQL Settings
```
Hostname:               localhost (or: ___________________)
Port:                   5433 (or: ___________________)
Database Name:          mpesa_analytics (or: ___________________)
Username:               data_engineer (or: ___________________)
Password:               change_me (or: ___________________)
                        ⚠️ CHANGE THIS IN PRODUCTION

Backup Strategy:        □ Daily  □ Weekly  □ None
Backup Location:        ___________________________________
```

### 3.2 Connection String
```
PostgreSQL URI:         postgresql://data_engineer:change_me@localhost:5433/mpesa_analytics

Or provide:             ___________________________________
```

---

## 📊 4. KAFKA CONFIGURATION (Optional - Defaults Provided)

### 4.1 Kafka Settings
```
Broker Address:         kafka:29092 (internal) or localhost:9092
Number of Partitions:   3 (or: _____  for higher throughput)
Replication Factor:     1 (or: _____  for redundancy)
Topic Name:             mpesa-transactions (or: ___________________)
Consumer Group:         mpesa_streaming_group (or: ___________________)
Retention Period:       7 days (or: _____  days)
```

### 4.2 Performance Tuning
```
Message Batch Size:     ___________________________________
Linger Time (ms):       ___________________________________
Compression Type:       □ None  □ gzip  □ snappy  □ lz4
```

---

## 🔧 5. APPLICATION CONFIGURATION

### 5.1 Logging & Monitoring
```
Log Level:              □ DEBUG  □ INFO (default)  □ WARNING  □ ERROR

Sentry Integration:     □ Yes  □ No
Sentry DSN:             ___________________________________

Rate Limiting:          ___________________________________
                        (Requests per minute, default: 120)
```

### 5.2 Feature Flags (Optional)
```
Enable STK Push:        □ Yes  □ No
Enable B2C Payments:    □ Yes  □ No
Enable Fraud Detection: □ Yes  □ No
Enable Real-time Dashboard: □ Yes  □ No
```

---

## 🎯 6. DATA & TESTING

### 6.1 Sample/Test Data
```
Load Sample Data:       □ Yes  □ No

Sample Transaction Count: _____ (default: 20)

Test Phone Numbers:     ___________________________________ 
                        (Format: 254712345678 - Include country code)

Test Amounts:           ___________________________________
                        (In KES, e.g., 100, 500, 1000)
```

### 6.2 Test Credentials (Safaricom Sandbox)
```
Test Phone Number:      ___________________________________
                        (Provided by Safaricom for sandbox)

Test PIN:               ___________________________________

Test USSD Code:         ___________________________________
                        (If testing USSD integration)
```

---

## 📈 7. OPTIONAL INTEGRATIONS

### 7.1 Analytics & BI Tools
```
Grafana Integration:    □ Yes  □ No
Grafana URL:            ___________________________________
Grafana API Key:        ___________________________________

Tableau Integration:    □ Yes  □ No
Tableau Server:         ___________________________________

Looker Integration:     □ Yes  □ No
Looker Instance URL:    ___________________________________
```

### 7.2 External Services
```
Email Alerts To:        ___________________________________
                        (Comma-separated: email@domain.com)

Slack Webhook URL:      ___________________________________
                        (For alerts)

PagerDuty Integration:  □ Yes  □ No
PagerDuty API Key:      ___________________________________
```

### 7.3 Data Warehouse (Optional)
```
BigQuery Project ID:    ___________________________________
BigQuery Dataset:       ___________________________________

Snowflake Account:      ___________________________________
Snowflake Database:     ___________________________________
```

---

## 🔐 8. SECURITY & COMPLIANCE

### 8.1 Authentication & Authorization
```
API Authentication:     □ API Key  □ OAuth2  □ JWT

API Key (if applicable): ___________________________________

OAuth2 Scopes:          ___________________________________

Admin Email:            ___________________________________
                        (For first user setup)
```

### 8.2 Data Privacy
```
Data Retention Period:  ___________________________________
                        (Days to keep raw data before archival)

GDPR Compliance:        □ Yes  □ No

PII Masking:            □ Yes  □ No

Encryption at Rest:     □ Yes  □ No
KMS Key ID:             ___________________________________
```

### 8.3 Audit & Compliance
```
Audit Logging:          □ Yes  □ No

Compliance Framework:   □ GDPR  □ CCPA  □ SOC2  □ None

Audit Trail Location:   ___________________________________
```

---

## 🚀 9. DEPLOYMENT OPTIONS

### 9.1 Where Will This Run?
```
□ Local Development (Laptop/Desktop)
□ On-Premises Server
  Server Address: _________________________________
  
□ AWS
  Region: __________________ Account ID: _________
  
□ Google Cloud Platform
  Project ID: ________________________
  Region: _____________________________
  
□ Microsoft Azure
  Subscription ID: ____________________________
  Region: _____________________________
  
□ DigitalOcean
  Region: _____________________________
  
□ Heroku / Render / Other PaaS: _____________________________
```

### 9.2 Scaling Requirements
```
Expected Daily Transactions:   ________________
Expected Peak TPS (Tx/sec):    ________________
Expected Users:                ________________
Uptime Requirement:            □ 99%  □ 99.9%  □ 99.99%
```

---

## 📋 10. QUICK REFERENCE TEMPLATE

Print this section and fill it out for quick reference:

```
═══════════════════════════════════════════════════════════════
DARAJA CREDENTIALS
═══════════════════════════════════════════════════════════════
Consumer Key:           _________________________________
Consumer Secret:        _________________________________
Business Shortcode:     _________________________________
Passkey:                _________________________________
Environment:            □ Sandbox  □ Production
Callback URL:           _________________________________

═══════════════════════════════════════════════════════════════
DATABASE
═══════════════════════════════════════════════════════════════
PostgreSQL URI:         _________________________________
Admin Password:         _________________________________

═══════════════════════════════════════════════════════════════
DEPLOYMENT
═══════════════════════════════════════════════════════════════
Target Environment:     □ Local  □ Cloud: ______________
Domain/URL:             _________________________________
SSL Enabled:            □ Yes  □ No

═══════════════════════════════════════════════════════════════
CONTACTS
═══════════════════════════════════════════════════════════════
Primary Contact:        _________________________________
Email:                  _________________________________
Phone:                  _________________________________
Support Email:          _________________________________
```

---

## 📝 11. SETUP INSTRUCTIONS

Once you've completed this form, follow these steps:

### Step 1: Create .env file
```bash
cp .env.example.comprehensive .env
```

### Step 2: Fill in the .env file with your values
```bash
nano .env
```

Copy values from this form into the corresponding variables:
- `DARAJA_CONSUMER_KEY=` (from section 1.1)
- `DARAJA_CONSUMER_SECRET=` (from section 1.1)
- `MPESA_BUSINESS_SHORTCODE=` (from section 1.2)
- `MPESA_PASSKEY=` (from section 1.2)
- `CALLBACK_URL=` (from section 1.3)
- `POSTGRES_PASSWORD=` (from section 3.1)
- And others as needed

### Step 3: Save and verify
```bash
# Check syntax
python -c "from dotenv import load_dotenv; load_dotenv('.env'); print('✓ .env loaded successfully')"
```

### Step 4: Start services
```bash
docker compose up -d
```

### Step 5: Verify connection
```bash
curl http://localhost:5000/health
```

---

## ✅ CHECKLIST BEFORE GOING LIVE

- [ ] All Daraja credentials obtained from Safaricom
- [ ] `.env` file created and filled with all required values
- [ ] `.env` file added to `.gitignore` (never commit secrets)
- [ ] Docker containers running (`docker compose ps`)
- [ ] Database connection verified
- [ ] Kafka topics created
- [ ] Webhook endpoint tested
- [ ] Sample transaction sent and received
- [ ] All tests passing (`make test`)
- [ ] Logging configured
- [ ] Monitoring/alerting set up
- [ ] Backup strategy in place
- [ ] Security review completed
- [ ] Load testing done (if needed)
- [ ] Documentation updated
- [ ] Team trained on system

---

## 📞 SUPPORT RESOURCES

- **Safaricom Daraja Docs**: https://developer.safaricom.co.ke/docs
- **Kafka Docs**: https://kafka.apache.org/documentation/
- **DBT Docs**: https://docs.getdbt.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Project Issues**: Check `IMPLEMENTATION_CHECKLIST.md`

---

## 📧 NEXT STEPS

1. **Print or save this file**
2. **Complete all sections above**
3. **Share with your team**
4. **Fill in missing information**
5. **Create .env file with your values**
6. **Run `make setup && make install-dev`**
7. **Start with `make docker-compose-up`**
8. **Run tests with `make test`**
9. **Begin streaming with `make run-webhook`**

---

**Generated:** May 14, 2026  
**Project:** M-Pesa Real-Time Transaction Streaming (Project 01)  
**Status:** Ready for configuration
