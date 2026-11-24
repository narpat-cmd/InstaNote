#!/usr/bin/env python
"""Test script to verify the API fix for invalid JSON payloads."""
import sys
import json
sys.path.insert(0, 'D:/InstaNote')

# Set required environment variables before importing the app
import os
os.environ['ADMIN_PASSWORD'] = 'test_password'
os.environ['FLASK_SECRET_KEY'] = 'test_secret_key_for_testing'

from src.admin_panel import create_app

def test_api_endpoints():
    """Test /api/generate and /api/settings endpoints with invalid JSON payload."""
    print("Creating Flask app...")
    app, socketio = create_app()

    # Create a test client
    client = app.test_client()

    # First, we need to set up a session for authentication
    with client.session_transaction() as sess:
        sess['logged_in'] = True

    print("\n" + "="*60)
    print("Testing /api/generate endpoint with invalid JSON payload")
    print("="*60)

    all_tests_passed = True

    # Test 1: /api/generate with invalid JSON payload (empty data)
    print("\n1. Testing /api/generate with empty data (invalid JSON)...")
    response = client.post('/api/generate',
                           data='',
                           content_type='application/json')

    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.content_type}")

    try:
        json_data = json.loads(response.data)
        print(f"   Response JSON: {json_data}")

        if response.status_code == 400 and 'error' in json_data:
            print("   PASS: Returns 400 with JSON error message")
        else:
            print(f"   FAIL: Expected 400 with error JSON, got status {response.status_code}")
            all_tests_passed = False
    except json.JSONDecodeError as e:
        print(f"   FAIL: Response is not valid JSON: {e}")
        print(f"   Raw response: {response.data[:200].decode('utf-8', errors='replace')}")
        all_tests_passed = False

    # Test 2: /api/settings POST with invalid JSON payload
    print("\n2. Testing /api/settings POST with empty data (invalid JSON)...")
    response = client.post('/api/settings',
                           data='',
                           content_type='application/json')

    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.content_type}")

    try:
        json_data = json.loads(response.data)
        print(f"   Response JSON: {json_data}")

        if response.status_code == 400 and 'error' in json_data:
            print("   PASS: Returns 400 with JSON error message")
        else:
            print(f"   FAIL: Expected 400 with error JSON, got status {response.status_code}")
            all_tests_passed = False
    except json.JSONDecodeError as e:
        print(f"   FAIL: Response is not valid JSON: {e}")
        all_tests_passed = False

    # Test 3: Verify /api/stats returns proper JSON after the fix
    print("\n3. Testing /api/stats returns proper JSON...")
    response = client.get('/api/stats')
    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.content_type}")

    try:
        json_data = json.loads(response.data)
        print("   PASS: Returns valid JSON")
    except json.JSONDecodeError:
        print("   FAIL: Response is not valid JSON")
        all_tests_passed = False

    # Test 4: Test with malformed JSON
    print("\n4. Testing /api/generate with malformed JSON...")
    response = client.post('/api/generate',
                           data='{bad json}',
                           content_type='application/json')

    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.content_type}")

    try:
        json_data = json.loads(response.data)
        print(f"   Response JSON: {json_data}")

        if response.status_code == 400 and 'error' in json_data:
            print("   PASS: Returns 400 with JSON error message")
        else:
            print(f"   Status: {response.status_code}")
    except json.JSONDecodeError as e:
        print(f"   FAIL: Response is not valid JSON: {e}")
        all_tests_passed = False

    # Test 5: Verify settings GET still works
    print("\n5. Testing /api/settings GET returns proper JSON...")
    response = client.get('/api/settings')
    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.content_type}")

    try:
        json_data = json.loads(response.data)
        if 'instagram' in json_data:
            print("   PASS: Returns proper JSON with config data")
        else:
            print("   WARNING: Returns JSON but unexpected structure")
    except json.JSONDecodeError as e:
        print(f"   FAIL: Response is not valid JSON: {e}")
        all_tests_passed = False

    print("\n" + "="*60)
    if all_tests_passed:
        print("SUCCESS: All tests passed - Fix verified successfully!")
        return 0
    else:
        print("FAILURE: Some tests failed - Fix may not be complete")
        return 1

if __name__ == "__main__":
    exit_code = test_api_endpoints()
    sys.exit(exit_code)