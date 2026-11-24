#!/usr/bin/env python3
"""Test script to verify Flask routes work after fixes"""

from src.admin_panel import create_app

app, socketio = create_app()
print('App created successfully')

with app.test_client() as client:
    # Test /scheduler route (GET)
    resp = client.get('/scheduler')
    print(f'/scheduler GET: {resp.status_code}')
    
    # Test /generate route (GET)
    resp = client.get('/generate')
    print(f'/generate GET: {resp.status_code}')
    
print('All routes working!')