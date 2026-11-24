#!/usr/bin/env python3
import os
import sys
import traceback

os.environ['ADMIN_PASSWORD'] = 'test'

try:
    from src.admin_panel import create_app
    app, s = create_app()
    print('App created successfully')
    
    with app.test_client() as c:
        # Login first
        c.post('/login', data={'password': 'test'})
        print('Logged in')
        
        # Test /scheduler
        r = c.get('/scheduler')
        print(f'/scheduler: {r.status_code}')
        if r.status_code != 200:
            print(f'Error: {r.data[:500]}')
        
        # Test /generate
        r = c.get('/generate')
        print(f'/generate: {r.status_code}')
        if r.status_code != 200:
            print(f'Error: {r.data[:500]}')
            
except Exception as e:
    print(f'Exception: {e}')
    traceback.print_exc()