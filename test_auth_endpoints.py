"""
Test all authenticated (admin) endpoints
"""
import requests
import json
from datetime import date, timedelta

BASE = 'http://127.0.0.1:8000/api'

print('='*60)
print('TESTING ALL AUTHENTICATED ENDPOINTS')
print('='*60)

# Login first
print('\n[LOGIN] Getting access token...')
r = requests.post(f'{BASE}/auth/login/', json={
    'email': 'admin@cafeiftar.com',
    'password': 'Admin@123'
})

if r.status_code != 200:
    print(f'  Login failed: {r.text}')
    exit(1)

data = r.json()
token = data['access']
headers = {'Authorization': f'Bearer {token}'}
print(f'  Logged in as: {data["user"]["email"]} (role: {data["user"]["role"]})')

# Track results
passed = 0
failed = 0

def test_endpoint(name, method, url, expected_status=200, json_data=None):
    global passed, failed
    try:
        if method == 'GET':
            r = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            r = requests.post(url, headers=headers, json=json_data, timeout=5)
        elif method == 'PATCH':
            r = requests.patch(url, headers=headers, json=json_data, timeout=5)
        elif method == 'DELETE':
            r = requests.delete(url, headers=headers, timeout=5)
        
        if r.status_code == expected_status:
            print(f'  ✓ {name}: {r.status_code}')
            passed += 1
            return True, r.json() if r.text else {}
        else:
            print(f'  ✗ {name}: got {r.status_code}, expected {expected_status}')
            failed += 1
            return False, {}
    except Exception as e:
        print(f'  ✗ {name}: ERROR - {e}')
        failed += 1
        return False, {}

tomorrow = (date.today() + timedelta(days=1)).isoformat()

# =============================================
# AUTH ENDPOINTS
# =============================================
print('\n--- AUTH ENDPOINTS ---')
test_endpoint('GET /auth/me/', 'GET', f'{BASE}/auth/me/')
test_endpoint('PATCH /auth/me/', 'PATCH', f'{BASE}/auth/me/', json_data={'first_name': 'Super'})

# =============================================
# RESERVATION ADMIN ENDPOINTS
# =============================================
print('\n--- RESERVATION ENDPOINTS ---')
test_endpoint('GET /reservations/', 'GET', f'{BASE}/reservations/')
test_endpoint('GET /reservations/stats/', 'GET', f'{BASE}/reservations/stats/')
test_endpoint('GET /reservations/today/', 'GET', f'{BASE}/reservations/today/?branch=2')

# =============================================
# BRANCH ADMIN ENDPOINTS
# =============================================
print('\n--- BRANCH ADMIN ENDPOINTS ---')
test_endpoint('GET /branches/operating-hours/', 'GET', f'{BASE}/branches/operating-hours/')
test_endpoint('GET /branches/special-dates/', 'GET', f'{BASE}/branches/special-dates/')

# =============================================
# MENU ADMIN ENDPOINTS
# =============================================
print('\n--- MENU ADMIN ENDPOINTS ---')
test_endpoint('GET /menu/ (list)', 'GET', f'{BASE}/menu/')
# Test toggle featured on item 8 (if exists)
ok, _ = test_endpoint('PATCH /menu/8/toggle_featured/', 'PATCH', f'{BASE}/menu/8/toggle_featured/')

# =============================================
# INQUIRIES ADMIN ENDPOINTS
# =============================================
print('\n--- INQUIRIES ENDPOINTS ---')
test_endpoint('GET /inquiries/', 'GET', f'{BASE}/inquiries/')

# =============================================
# DEALS ADMIN ENDPOINTS
# =============================================
print('\n--- DEALS ENDPOINTS ---')
test_endpoint('GET /deals/', 'GET', f'{BASE}/deals/')

# =============================================
# GALLERY ADMIN ENDPOINTS
# =============================================
print('\n--- GALLERY ENDPOINTS ---')
test_endpoint('GET /gallery/', 'GET', f'{BASE}/gallery/')

# =============================================
# TABLES ADMIN ENDPOINTS
# =============================================
print('\n--- TABLES ENDPOINTS ---')
test_endpoint('GET /tables/', 'GET', f'{BASE}/tables/')

# =============================================
# SUMMARY
# =============================================
print('\n' + '='*60)
total = passed + failed
print(f'RESULTS: {passed}/{total} PASSED ({passed/total*100:.0f}%)')
if failed == 0:
    print('ALL AUTHENTICATED ENDPOINTS WORKING! ✓')
else:
    print(f'{failed} endpoint(s) need attention')
print('='*60)
