#!/usr/bin/env python3
import sys
sys.path.insert(0, 'D:/InstaNote')

with open('D:/InstaNote/src/admin_panel.py', 'r') as f:
    lines = f.readlines()

# Print login function (lines 59-75)
print('=== LOGIN FUNCTION (lines 59-75) ===')
for i in range(58, 75):
    print(f'{i+1}| {lines[i]}', end='')

print('\n\n=== ROOT ROUTE (lines 76-80) ===')
for i in range(75, 80):
    print(f'{i+1}| {lines[i]}', end='')

print('\n\n=== DASHBOARD ROUTE (lines 81-103) ===')
for i in range(80, 103):
    print(f'{i+1}| {lines[i]}', end='')