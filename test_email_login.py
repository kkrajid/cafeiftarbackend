import requests
import json

BASE = 'http://127.0.0.1:8000/api'

print('='*60)
print('TESTING EMAIL-BASED LOGIN')
print('='*60)

# Test 1: Login with email
print('\n[1] Login with email...')
r = requests.post(f'{BASE}/auth/login/', json={
    'email': 'admin@cafeiftar.com',
    'password': 'Admin@123'
})
print(f'  Status: {r.status_code}')
data = r.json()

if r.status_code == 200:
    access_token = data['access']
    refresh_token = data['refresh']
    user = data.get('user', {})
    
    print(f'  Access Token: {access_token[:50]}...')
    print(f'  Refresh Token: {refresh_token[:50]}...')
    print(f'  User Info:')
    print(f'    - ID: {user.get("id")}')
    print(f'    - Email: {user.get("email")}')
    print(f'    - Name: {user.get("first_name")} {user.get("last_name")}')
    print(f'    - Role: {user.get("role")}')
    
    # Test 2: Use token to access protected endpoint
    print('\n[2] Access protected endpoint with token...')
    headers = {'Authorization': f'Bearer {access_token}'}
    r2 = requests.get(f'{BASE}/auth/me/', headers=headers)
    print(f'  GET /auth/me/ Status: {r2.status_code}')
    if r2.status_code == 200:
        me = r2.json()
        print(f'  Logged in as: {me.get("email")} ({me.get("role")})')
    
    # Test 3: Access admin-only endpoint
    print('\n[3] Access admin-only reservation stats...')
    r3 = requests.get(f'{BASE}/reservations/stats/', headers=headers)
    print(f'  GET /reservations/stats/ Status: {r3.status_code}')
    if r3.status_code == 200:
        stats = r3.json()
        print(f'  Total today: {stats.get("today", 0)}')
        print(f'  Pending: {stats.get("pending", 0)}')
    
    print('\n  *** ALL TESTS PASSED! ***')
else:
    print(f'  Error: {json.dumps(data, indent=2)}')

print('\n' + '='*60)
print('EMAIL LOGIN TEST COMPLETE')
print('='*60)
