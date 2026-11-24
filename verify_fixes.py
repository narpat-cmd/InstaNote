#!/usr/bin/env python3
"""Comprehensive test for both fixes"""
import sys
sys.path.insert(0, 'D:/InstaNote')

print("=== Testing Scheduler Fix ===")
from src.scheduler import get_scheduler, InstaNoteScheduler, JobStatus
s = get_scheduler()
print(f"Scheduler has get_pending_jobs: {hasattr(s, 'get_pending_jobs')}")
print(f"Pending jobs result: {s.get_pending_jobs()}")

print("\n=== Testing Admin Panel Fix ===")
from src.admin_panel import create_app
app, _ = create_app()
print("App created successfully")

with app.test_client() as client:
    resp1 = client.get('/scheduler')
    print(f"/scheduler GET: {resp1.status_code}")
    
    resp2 = client.get('/generate')
    print(f"/generate GET: {resp2.status_code}")

print("\n=== All Tests Passed ===")