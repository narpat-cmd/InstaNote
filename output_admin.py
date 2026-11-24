#!/usr/bin/env python3
import re

with open('D:/InstaNote/src/admin_panel.py', 'r') as f:
    content = f.read()

# Find the login function
login_match = re.search(r'def login\(\):.*?(?=\n@app\.route|\ndef |\Z)', content, re.DOTALL)
if login_match:
    print('=== LOGIN FUNCTION ===')
    print(login_match.group(0))

# Find the root route
root_match = re.search(r"@app\.route\('/'\).*?(?=\n@app\.route|\ndef |\Z)", content, re.DOTALL)
if root_match:
    print('\n=== ROOT ROUTE ===')
    print(root_match.group(0))

# Find the dashboard route
dashboard_match = re.search(r"@app\.route\('/dashboard'\).*?(?=\n@app\.route|\ndef |\Z)", content, re.DOTALL)
if dashboard_match:
    print('\n=== DASHBOARD ROUTE ===')
    print(dashboard_match.group(0))
else:
    # Try to find topics route
    topics_match = re.search(r"@app\.route\('/topics'\).*?(?=\n@app\.route|\ndef |\Z)", content, re.DOTALL)
    if topics_match:
        print('\n=== TOPICS ROUTE ===')
        print(topics_match.group(0))