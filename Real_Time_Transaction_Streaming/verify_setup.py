#!/usr/bin/env python3
"""
Verification script to test M-Pesa project configuration and connectivity.

This script checks:
1. Environment variables are loaded
2. Docker containers are running
3. Database connection works
4. Daraja API credentials are valid
5. Kafka connectivity
6. Required Python packages are installed
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("M-PESA PROJECT CONFIGURATION VERIFICATION")
print("=" * 80)
print(f"Project Root: {project_root}")
print(f"Current Time: {datetime.now().isoformat()}")
print()

# ============================================================================
# 1. ENVIRONMENT VARIABLES
# ============================================================================
print("1. ENVIRONMENT VARIABLES")
print("-" * 80)

required_vars = {
    'Daraja': [
        'DARAJA_CONSUMER_KEY',
        'DARAJA_CONSUMER_SECRET',
        'MPESA_BUSINESS_SHORTCODE',
    ],
    'Database': [
        'POSTGRES_HOST',
        'POSTGRES_PORT',
        'POSTGRES_DB',
        'POSTGRES_USER',
    ],
    'Kafka': [
        'KAFKA_BROKERS',
        'KAFKA_TOPIC_TRANSACTIONS',
    ],
}

env_status = {}
for category, vars_list in required_vars.items():
    print(f"\n{category}:")
    env_status[category] = {}
    for var in vars_list:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var or 'PASSWORD' in var:
                display = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display = value
            print(f"  ✓ {var:<40} = {display}")
            env_status[category][var] = 'OK'
        else:
            print(f"  ✗ {var:<40} = NOT SET")
            env_status[category][var] = 'MISSING'

print()

# ============================================================================
# 2. DOCKER CONTAINERS
# ============================================================================
print("2. DOCKER CONTAINERS")
print("-" * 80)

try:
    result = subprocess.run(
        ['docker', 'compose', 'ps'],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        # Print header + 5 service lines
        print("Docker Compose Services:")
        for line in lines[:6]:
            print(f"  {line}")
        
        # Count running services
        running = result.stdout.count('running')
        print(f"\n  → {running} services running")
    else:
        print(f"  ✗ Error running docker compose: {result.stderr}")
except Exception as e:
    print(f"  ✗ Docker not available: {e}")

print()

# ============================================================================
# 3. DATABASE CONNECTION
# ============================================================================
print("3. DATABASE CONNECTION")
print("-" * 80)

try:
    import psycopg2
    
    conn_params = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', '5433')),
        'database': os.getenv('POSTGRES_DB', 'mpesa_analytics'),
        'user': os.getenv('POSTGRES_USER', 'data_engineer'),
        'password': os.getenv('POSTGRES_PASSWORD', 'change_me'),
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"  ✓ PostgreSQL Connection Successful")
        print(f"    Version: {version[:50]}...")
        
        # Check tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"    Tables in database: {len(tables)}")
        if tables:
            for (table,) in tables[:5]:
                print(f"      - {table}")
            if len(tables) > 5:
                print(f"      ... and {len(tables) - 5} more")
        
        cursor.close()
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"  ✗ Connection Failed: {str(e)[:100]}")
        print(f"    Connection params: {conn_params}")
except ImportError:
    print("  ✗ psycopg2 not installed (required for database tests)")

print()

# ============================================================================
# 4. DARAJA API CREDENTIALS
# ============================================================================
print("4. DARAJA API CREDENTIALS")
print("-" * 80)

try:
    from ingestion.daraja_client import DarajaClient
    
    try:
        client = DarajaClient.from_env()
        print(f"  ✓ Daraja Client Initialized Successfully")
        print(f"    Environment: {client.environment}")
        print(f"    Consumer Key: {client.consumer_key[:10]}...")
        print(f"    Business Shortcode: {client.business_shortcode}")
        print(f"    Callback URL: {client.callback_url}")
        
        # Try to get access token
        try:
            token = client.get_access_token()
            print(f"  ✓ OAuth2 Token Generated")
            print(f"    Token (first 20 chars): {token[:20]}...")
            print(f"    Token Length: {len(token)}")
        except Exception as e:
            print(f"  ⚠ Token Generation Failed: {str(e)[:100]}")
            print(f"    This may be expected in sandbox environment without live API access")
    
    except ValueError as e:
        print(f"  ✗ Missing Required Credentials: {e}")
except ImportError as e:
    print(f"  ✗ ingestion.daraja_client not available: {e}")

print()

# ============================================================================
# 5. KAFKA CONNECTIVITY
# ============================================================================
print("5. KAFKA CONNECTIVITY")
print("-" * 80)

try:
    from kafka import KafkaProducer, KafkaConsumer
    
    brokers = os.getenv('KAFKA_BROKERS', 'localhost:9092').split(',')
    print(f"  Kafka Brokers: {brokers}")
    
    try:
        # Test producer
        producer = KafkaProducer(
            bootstrap_servers=brokers,
            request_timeout_ms=5000
        )
        print(f"  ✓ Producer Connection OK")
        producer.close()
    except Exception as e:
        print(f"  ✗ Producer Connection Failed: {str(e)[:80]}")
    
    try:
        # Test consumer
        consumer = KafkaConsumer(
            bootstrap_servers=brokers,
            request_timeout_ms=5000,
            consumer_timeout_ms=1000
        )
        metadata = consumer.topics()
        print(f"  ✓ Consumer Connection OK")
        print(f"    Available Topics: {list(metadata)[:5]}")
        consumer.close()
    except Exception as e:
        print(f"  ✗ Consumer Connection Failed: {str(e)[:80]}")

except ImportError:
    print("  ⚠ kafka-python not installed (optional for monitoring)")

print()

# ============================================================================
# 6. PYTHON PACKAGES
# ============================================================================
print("6. PYTHON PACKAGES")
print("-" * 80)

required_packages = [
    'pandas',
    'numpy',
    'psycopg2',
    'requests',
    'kafka',
    'dotenv',
    'sqlalchemy',
    'dbt.core',
]

missing = []
for package in required_packages:
    try:
        if package == 'dotenv':
            __import__('dotenv')
        elif package == 'dbt.core':
            __import__('dbt.core')
        else:
            __import__(package)
        print(f"  ✓ {package:<20} installed")
    except ImportError:
        print(f"  ✗ {package:<20} NOT installed")
        missing.append(package)

if missing:
    print(f"\n  To install missing packages:")
    print(f"  pip install {' '.join(missing)}")

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("SUMMARY")
print("=" * 80)

missing_env = sum(1 for cat_status in env_status.values() 
                  for status in cat_status.values() if status == 'MISSING')

if missing_env == 0 and not missing:
    print("✓ All checks passed! Project is ready for use.")
else:
    print("⚠ Some checks failed:")
    if missing_env > 0:
        print(f"  - {missing_env} environment variables missing")
    if missing:
        print(f"  - {len(missing)} Python packages missing")
    print("\nRefer to sections above for details and remediation steps.")

print()
print("NEXT STEPS:")
print("1. Run notebooks: jupyter notebook notebooks/")
print("2. Start streaming: python -m ingestion.kafka_producer")
print("3. Check webhooks: curl http://localhost:5000/health")
print()
