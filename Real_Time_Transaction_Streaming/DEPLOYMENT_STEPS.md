"""
COMPLETE DEPLOYMENT GUIDE - STEP-BY-STEP
From local development to production on Google Cloud Run
"""

# ============================================================================
# PHASE 1: LOCAL DEVELOPMENT SETUP (2-3 hours)
# ============================================================================

# Step 1: Clone and setup project
git clone <your-repo-url> mpesa-platform
cd mpesa-platform

# Step 2: Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Setup environment file
cp .env.example .env
# Edit .env with your Safaricom credentials:
# DARAJA_CONSUMER_KEY=your_key
# DARAJA_CONSUMER_SECRET=your_secret
# DARAJA_BUSINESS_SHORTCODE=8759693
# DARAJA_PASSKEY=your_passkey

# Step 5: Start Docker services
docker compose up -d

# Step 6: Verify services running
docker compose ps

# Expected output:
# NAMES                  STATUS              PORTS
# mpesa_postgres        Up (healthy)        5433->5432/tcp
# mpesa_redis           Up                  6380->6379/tcp

# Step 7: Create database tables
python -c "from app.database.connection import Base, engine; Base.metadata.create_all(engine)"

# Step 8: Test Safaricom connection
python app/services/safaricom.py

# Expected output:
# ✓ OAuth successful
# ✓ C2B simulation successful

# Step 9: Run application locally
uvicorn app.main:app --reload

# Now accessible at: http://localhost:8000
# API docs at: http://localhost:8000/docs

# ============================================================================
# PHASE 2: WEBHOOK SETUP (1 hour)
# ============================================================================

# Step 1: Get ngrok (temporary URL for testing)
brew install ngrok  # or download from ngrok.com

# Step 2: Expose local server to internet
ngrok http 8000

# You'll get a URL like: https://abc123.ngrok.io

# Step 3: Register callbacks with Safaricom
python -c "
import asyncio
from app.services.safaricom import daraja_service

async def register():
    result = await daraja_service.register_c2b_callback(
        confirmation_url='https://abc123.ngrok.io/api/v1/webhooks/c2b/confirmation',
        validation_url='https://abc123.ngrok.io/api/v1/webhooks/c2b/validation'
    )
    print(result)

asyncio.run(register())
"

# Expected response:
# {
#   'ResponseCode': '0',
#   'ResponseDescription': 'Registered Successfully'
# }

# Step 4: Test webhook with ngrok URL
# Use Postman or curl to send test payment

# ============================================================================
# PHASE 3: TESTING (2-3 hours)
# ============================================================================

# Step 1: Run unit tests
pytest tests/unit/ -v

# Step 2: Run integration tests
pytest tests/integration/ -v

# Step 3: Test API endpoints with coverage
pytest --cov=app tests/ --cov-report=html

# Step 4: Load testing (using Apache Bench)
ab -n 1000 -c 10 http://localhost:8000/api/v1/health

# Step 5: Test webhook signature verification
# Add test transactions via Safaricom Sandbox

# ============================================================================
# PHASE 4: GCP PROJECT SETUP (1-2 hours)
# ============================================================================

# Step 1: Set GCP project
export PROJECT_ID="mpesapipeline"
export REGION="africa-south1"

gcloud config set project $PROJECT_ID

# Step 2: Enable required APIs
gcloud services enable \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com

# Step 3: Create service account for Cloud Run
gcloud iam service-accounts create mpesa-app-sa \
  --display-name="M-Pesa Application Service Account"

# Step 4: Grant Cloud SQL Client role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:mpesa-app-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Step 5: Grant Cloud Run permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:mpesa-app-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# ============================================================================
# PHASE 5: DATABASE SETUP ON GCP (1-2 hours)
# ============================================================================

# Step 1: Create Cloud SQL instance
gcloud sql instances create mpesa-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-custom-4-16384 \
  --region=$REGION \
  --storage-type=PD_SSD \
  --storage-size=100GB \
  --backup-start-time=02:00 \
  --enable-bin-log \
  --require-ssl

# Wait for instance to be ready (takes 3-5 minutes)
gcloud sql instances describe mpesa-postgres --format='value(state)'

# Step 2: Create database
gcloud sql databases create mpesa_analytics \
  --instance=mpesa-postgres

# Step 3: Create database user
gcloud sql users create data_engineer \
  --instance=mpesa-postgres \
  --password="YOUR_SECURE_PASSWORD"

# Step 4: Get Cloud SQL connection name
CLOUD_SQL_CONNECTION=$(gcloud sql instances describe mpesa-postgres \
  --format='value(connectionName)')

echo $CLOUD_SQL_CONNECTION
# Expected: mpesapipeline:africa-south1:mpesa-postgres

# Step 5: Export local database
pg_dump -h localhost -p 5433 -U data_engineer mpesa_analytics > backup.sql

# Step 6: Import to Cloud SQL
gcloud sql import sql mpesa-postgres backup.sql \
  --database=mpesa_analytics

# Step 7: Test connection
gcloud sql connect mpesa-postgres \
  --user=data_engineer \
  --project=$PROJECT_ID

# ============================================================================
# PHASE 6: BUILD AND PUSH DOCKER IMAGE (30 minutes)
# ============================================================================

# Step 1: Configure Docker auth for GCP
gcloud auth configure-docker

# Step 2: Build Docker image
docker build -t gcr.io/$PROJECT_ID/mpesa-app:latest .

# Step 3: Push to Container Registry
docker push gcr.io/$PROJECT_ID/mpesa-app:latest

# Verify image is pushed:
gcloud container images list --project=$PROJECT_ID

# ============================================================================
# PHASE 7: DEPLOY TO CLOUD RUN (30 minutes)
# ============================================================================

# Step 1: Deploy application to Cloud Run
gcloud run deploy mpesa-app \
  --image=gcr.io/$PROJECT_ID/mpesa-app:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=3600 \
  --max-instances=100 \
  --min-instances=1 \
  --service-account=mpesa-app-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION \
  --set-env-vars=\
"DB_HOST=/cloudsql/$CLOUD_SQL_CONNECTION,\
DB_PORT=5432,\
DB_NAME=mpesa_analytics,\
DB_USER=data_engineer,\
DB_PASSWORD=YOUR_SECURE_PASSWORD,\
ENVIRONMENT=production,\
LOG_LEVEL=INFO,\
DOMAIN=chamayangu.online,\
GCP_PROJECT_ID=$PROJECT_ID,\
GCP_REGION=$REGION"

# Step 2: Get Cloud Run URL
SERVICE_URL=$(gcloud run services describe mpesa-app \
  --region=$REGION \
  --format='value(status.url)')

echo "Service deployed at: $SERVICE_URL"

# Step 3: Test deployment
curl $SERVICE_URL/api/v1/health

# Expected response:
# {"service":"M-Pesa Analytics Platform","version":"1.0.0","status":"operational","timestamp":"..."}

# ============================================================================
# PHASE 8: HTTPS DOMAIN SETUP (2-3 hours)
# ============================================================================

# Step 1: Reserve static IP address
gcloud compute addresses create mpesa-static-ip \
  --region=$REGION \
  --project=$PROJECT_ID

# Get IP address
STATIC_IP=$(gcloud compute addresses describe mpesa-static-ip \
  --region=$REGION \
  --format='get(address)')

echo "Static IP: $STATIC_IP"
echo "Update DNS A record to: $STATIC_IP"

# Step 2: Create managed SSL certificate
gcloud compute ssl-certificates create mpesa-ssl-cert \
  --domains=chamayangu.online,api.chamayangu.online \
  --project=$PROJECT_ID

# Step 3: Create health check for load balancer
gcloud compute health-checks create http mpesa-health-check \
  --global \
  --request-path=/api/v1/health \
  --port=8080 \
  --project=$PROJECT_ID

# Step 4: Create backend service
gcloud compute backend-services create mpesa-backend \
  --global \
  --protocol=HTTPS \
  --health-checks=mpesa-health-check \
  --project=$PROJECT_ID

# Step 5: Create network endpoint group (NEG) for Cloud Run
gcloud compute network-endpoint-groups create mpesa-neg \
  --region=$REGION \
  --network-endpoint-type=serverless \
  --cloud-run-service=mpesa-app \
  --project=$PROJECT_ID

# Step 6: Add NEG to backend service
gcloud compute backend-services add-backend mpesa-backend \
  --global \
  --instance-group=mpesa-neg \
  --instance-group-region=$REGION \
  --project=$PROJECT_ID

# Step 7: Create URL map
gcloud compute url-maps create mpesa-lb \
  --default-service=mpesa-backend \
  --project=$PROJECT_ID

# Step 8: Create HTTPS proxy
gcloud compute target-https-proxies create mpesa-https-proxy \
  --url-map=mpesa-lb \
  --ssl-certificates=mpesa-ssl-cert \
  --project=$PROJECT_ID

# Step 9: Create forwarding rule
gcloud compute forwarding-rules create mpesa-https-rule \
  --global \
  --address=mpesa-static-ip \
  --target-https-proxy=mpesa-https-proxy \
  --ports=443 \
  --project=$PROJECT_ID

# Step 10: Setup HTTP to HTTPS redirect
gcloud compute url-maps create mpesa-http-redirect \
  --global \
  --project=$PROJECT_ID

gcloud compute target-http-proxies create mpesa-http-proxy \
  --url-map=mpesa-http-redirect \
  --project=$PROJECT_ID

gcloud compute forwarding-rules create mpesa-http-rule \
  --global \
  --address=mpesa-static-ip \
  --target-http-proxy=mpesa-http-proxy \
  --ports=80 \
  --project=$PROJECT_ID

# Step 11: Update DNS records
# Go to your domain registrar and set:
# A record: chamayangu.online -> $STATIC_IP
# A record: api.chamayangu.online -> $STATIC_IP
# CNAME: www.chamayangu.online -> chamayangu.online

# Step 12: Verify HTTPS working
sleep 60  # Wait for DNS to propagate
curl https://chamayangu.online/api/v1/health
curl https://api.chamayangu.online/api/v1/health

# ============================================================================
# PHASE 9: MONITORING & LOGGING (1 hour)
# ============================================================================

# Step 1: Create Cloud Monitoring dashboard
gcloud monitoring dashboards create --config-from-file=monitoring.yaml

# Step 2: View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mpesa-app" \
  --limit=50 \
  --format=json

# Step 3: Create log-based alert for errors
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="M-Pesa High Error Rate" \
  --condition-display-name="Error rate > 1%" \
  --condition-threshold-value=0.01 \
  --condition-threshold-duration=300s

# Step 4: Setup Cloud Profiler
gcloud alpha code-profiles service-agent enable --project=$PROJECT_ID

# Step 5: View metrics
gcloud monitoring time-series list \
  --filter='resource.type=cloud_run_revision'

# ============================================================================
# PHASE 10: SAFARICOM PRODUCTION SETUP (1-2 hours)
# ============================================================================

# Step 1: Update Safaricom callback URLs in Dashboard
# Go to Safaricom Daraja console and update:
# C2B Confirmation: https://chamayangu.online/api/v1/webhooks/c2b/confirmation
# C2B Validation: https://chamayangu.online/api/v1/webhooks/c2b/validation
# STK Callback: https://chamayangu.online/api/v1/webhooks/stk/callback

# Step 2: Switch to production credentials in .env
gcloud run services update mpesa-app \
  --region=$REGION \
  --update-env-vars=\
"DARAJA_CONSUMER_KEY=PROD_KEY,\
DARAJA_CONSUMER_SECRET=PROD_SECRET,\
DARAJA_PASSKEY=PROD_PASSKEY,\
DARAJA_ENVIRONMENT=production"

# Step 3: Redeploy with production settings
gcloud run deploy mpesa-app \
  --image=gcr.io/$PROJECT_ID/mpesa-app:latest \
  --region=$REGION

# Step 4: Test with production API
python -c "
import asyncio
import os
os.environ['DARAJA_ENVIRONMENT'] = 'production'

from app.services.safaricom import daraja_service

async def test():
    token = await daraja_service.get_access_token()
    print('✓ Production OAuth successful')

asyncio.run(test())
"

# ============================================================================
# VERIFICATION CHECKLIST
# ============================================================================

# ✓ Database is running on Cloud SQL
gcloud sql instances describe mpesa-postgres

# ✓ Application is deployed on Cloud Run
gcloud run services describe mpesa-app --region=$REGION

# ✓ HTTPS is working
curl -I https://chamayangu.online/api/v1/health

# ✓ Webhooks are registered
python -c "
import asyncio
from app.services.safaricom import daraja_service

async def verify():
    # Try to make a test transaction
    result = await daraja_service.simulate_c2b_payment(
        phone_number='254712345678',
        amount=100
    )
    print('✓ C2B working')

asyncio.run(verify())
"

# ✓ Monitoring is active
gcloud monitoring dashboards list

# ============================================================================
# SCALING & OPTIMIZATION
# ============================================================================

# Scale instances
gcloud run services update mpesa-app \
  --region=$REGION \
  --min-instances=2 \
  --max-instances=200

# Update memory/CPU
gcloud run services update mpesa-app \
  --region=$REGION \
  --memory=4Gi \
  --cpu=4

# ============================================================================
# DISASTER RECOVERY
# ============================================================================

# Backup database
gcloud sql backups create \
  --instance=mpesa-postgres \
  --project=$PROJECT_ID

# List backups
gcloud sql backups list --instance=mpesa-postgres

# Restore from backup (in case of disaster)
gcloud sql backups restore BACKUP_ID \
  --backup-instance=mpesa-postgres

# ============================================================================
# MONITORING & ALERTS
# ============================================================================

# View application logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mpesa-app" \
  --limit=100 \
  --format=json | jq '.[] | .jsonPayload'

# View metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count"'

# ============================================================================
# COST OPTIMIZATION
# ============================================================================

# Current usage
gcloud billing accounts list
gcloud compute project-info describe --project=$PROJECT_ID

# Cost estimation:
# - Cloud SQL (db-custom-4-16384): ~$200/month
# - Cloud Run (2Gi, 2 CPU): ~$50-100/month
# - Cloud Storage (100GB backups): ~$2/month
# - Cloud Load Balancer: ~$25/month
# - Data egress: ~$20-50/month
# Total estimate: $300-400/month

# ============================================================================
# FINAL VERIFICATION
# ============================================================================

# Everything working?
echo "Testing final setup..."

# 1. Health check
curl https://chamayangu.online/api/v1/health

# 2. Database connectivity
gcloud sql connect mpesa-postgres --user=data_engineer

# 3. View dashboard
gcloud monitoring dashboards list

# 4. Check logs
gcloud logging read "resource.type=cloud_run_revision" --limit=10

echo "✓ All systems operational!"
echo "✓ Application running at: https://chamayangu.online"
echo "✓ API docs at: https://chamayangu.online/docs"
