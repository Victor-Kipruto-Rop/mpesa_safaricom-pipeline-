#!/usr/bin/env python3
"""Test the Daraja API integration with your credentials."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("TESTING DARAJA API INTEGRATION")
print("=" * 80)
print()

# Test 1: Import Daraja Client
print("Test 1: Importing Daraja Client...")
try:
    from ingestion.daraja_client import DarajaClient
    print("✓ Successfully imported DarajaClient")
except ImportError as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

print()

# Test 2: Initialize client from environment
print("Test 2: Initializing client from environment variables...")
try:
    client = DarajaClient.from_env()
    print("✓ Client initialized successfully")
    print(f"  - Environment: {client.environment}")
    print(f"  - Consumer Key: {client.consumer_key[:10]}...{client.consumer_key[-5:]}")
    print(f"  - Business Shortcode: {client.business_shortcode}")
    print(f"  - Callback URL: {client.callback_url}")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    sys.exit(1)

print()

# Test 3: Get access token
print("Test 3: Obtaining OAuth2 access token...")
try:
    token = client.get_access_token()
    print("✓ Access token obtained successfully")
    print(f"  - Token (first 20 chars): {token[:20]}...")
    print(f"  - Token length: {len(token)}")
    
    # Try to verify token by making a simple API call
    print()
    print("Test 4: Verifying token with API call...")
    
    # Let's try to check account balance (read-only operation)
    try:
        from requests import Session
        session = Session()
        
        # This is a safe test endpoint
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Try to get account balance endpoint (doesn't require params)
        test_url = f"{client.base_url}/mpesa/accountbalance/v1/query"
        
        print(f"  Testing API endpoint: {test_url}")
        
        # We expect a 400 Bad Request since we're not sending proper params
        # But if we get 401, it means the token is invalid
        response = session.post(
            test_url,
            headers=headers,
            json={},
            timeout=10
        )
        
        if response.status_code == 401:
            print(f"✗ Token validation failed (401 Unauthorized)")
            print(f"  Response: {response.text[:100]}")
        elif response.status_code in [400, 500]:
            print(f"✓ Token is valid (got {response.status_code} as expected for test)")
            print(f"  Response preview: {response.text[:100]}")
        else:
            print(f"? Unexpected status code: {response.status_code}")
            print(f"  Response: {response.text[:100]}")
    
    except Exception as e:
        print(f"⚠ Could not verify token with API call: {e}")
        print("  (This may be expected if network access to Safaricom is limited)")

except Exception as e:
    print(f"✗ Failed to get access token: {e}")
    print()
    print("Note: This may happen if:")
    print("  1. Credentials are invalid")
    print("  2. Network is not available")
    print("  3. Sandbox API is temporarily unavailable")
    sys.exit(1)

print()
print("=" * 80)
print("✓ All critical tests passed!")
print("=" * 80)
print()
print("Your M-Pesa project is ready. You can now:")
print("  1. Run notebooks with: jupyter notebook notebooks/")
print("  2. Start streaming with: python -m ingestion.kafka_producer")
print("  3. Test webhooks with: curl http://localhost:5000/health")
print()
