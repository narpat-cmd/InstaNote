#!/usr/bin/env python3
"""Analyze admin_panel.py to understand login flow"""

with open('D:/InstaNote/src/admin_panel.py', 'r') as f:
    lines = f.readlines()

# Print lines 49-100 (login function and dashboard)
print("=== LOGIN FUNCTION AND DASHBOARD ===")
for i in range(48, 100):
    print(f'{i+1}| {lines[i]}', end='')

print("\n\n=== ROOT ROUTE ===")
for i in range(75, 90):
    print(f'{i+1}| {lines[i]}', end='')

print("\n\n=== LOGIN FUNCTION COMPLETE ===")
for i in range(58, 75):
    print(f'{i+1}| {lines[i]}', end='')