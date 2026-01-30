"""
Test all public (user-side) endpoints - no authentication required
"""
import requests
import json
from datetime import date, timedelta

BASE = 'http://127.0.0.1:8000/api'

print('='*60)
print('TESTING ALL PUBLIC USER-SIDE ENDPOINTS')
print('='*60)

# Track results
passed = 0
failed = 0
tomorrow = (date.today() + timedelta(days=1)).isoformat()

def test_endpoint(name, method, url, expected_status=200, json_data=None):
    global passed, failed
    try:
        if method == 'GET':
            r = requests.get(url, timeout=5)
        elif method == 'POST':
            r = requests.post(url, json=json_data, timeout=5)
        
        if r.status_code == expected_status:
            print(f'  ✓ {name}: {r.status_code}')
            passed += 1
            try:
                return True, r.json()
            except:
                return True, {}
        else:
            print(f'  ✗ {name}: got {r.status_code}, expected {expected_status}')
            failed += 1
            return False, {}
    except Exception as e:
        print(f'  ✗ {name}: ERROR - {e}')
        failed += 1
        return False, {}

# =============================================
# BRANCHES - PUBLIC
# =============================================
print('\n--- BRANCHES (Public) ---')
ok, data = test_endpoint('GET /branches/', 'GET', f'{BASE}/branches/')
if ok and data.get('results'):
    branch_id = data['results'][0]['id']
    print(f'     Found {data.get("count", 0)} branches')
    
    test_endpoint(f'GET /branches/{branch_id}/', 'GET', f'{BASE}/branches/{branch_id}/')
    test_endpoint(f'GET /branches/{branch_id}/hours/', 'GET', f'{BASE}/branches/{branch_id}/hours/')
    test_endpoint(f'GET /branches/{branch_id}/hours/{tomorrow}/', 'GET', f'{BASE}/branches/{branch_id}/hours/{tomorrow}/')

# =============================================
# TABLES - PUBLIC
# =============================================
print('\n--- TABLES (Public) ---')
ok, data = test_endpoint('GET /tables/', 'GET', f'{BASE}/tables/')
if ok:
    print(f'     Found {data.get("count", 0)} tables')

test_endpoint('GET /tables/availability/', 'GET', 
              f'{BASE}/tables/availability/?branch=2&date={tomorrow}&time=19:00&guests=4')
test_endpoint('GET /tables/available_slots/', 'GET', 
              f'{BASE}/tables/available_slots/?branch=2&date={tomorrow}&guests=4')

# =============================================
# MENU - PUBLIC
# =============================================
print('\n--- MENU (Public) ---')
ok, data = test_endpoint('GET /menu/', 'GET', f'{BASE}/menu/')
if ok:
    print(f'     Found {data.get("count", 0)} menu items')

ok, data = test_endpoint('GET /menu/featured/', 'GET', f'{BASE}/menu/featured/')
if ok:
    print(f'     Featured items: {data.get("count", 0)}')

test_endpoint('GET /menu/categories/', 'GET', f'{BASE}/menu/categories/')

# =============================================
# DEALS - PUBLIC
# =============================================
print('\n--- DEALS (Public) ---')
ok, data = test_endpoint('GET /deals/', 'GET', f'{BASE}/deals/')
if ok:
    print(f'     Found {data.get("count", 0)} deals')

# =============================================
# GALLERY - PUBLIC
# =============================================
print('\n--- GALLERY (Public) ---')
ok, data = test_endpoint('GET /gallery/', 'GET', f'{BASE}/gallery/')
if ok:
    print(f'     Found {data.get("count", 0)} gallery images')

# =============================================
# RESERVATIONS - PUBLIC
# =============================================
print('\n--- RESERVATIONS (Public) ---')
test_endpoint('GET /reservations/my_reservations/', 'GET', 
              f'{BASE}/reservations/my_reservations/?email=test@example.com')
test_endpoint('GET /reservations/by_confirmation/', 'GET', 
              f'{BASE}/reservations/by_confirmation/?confirmation_id=TEST123', expected_status=404)

# Test reservation creation (validation error expected - missing fields)
test_endpoint('POST /reservations/ (validation)', 'POST', 
              f'{BASE}/reservations/', expected_status=400, json_data={})

# =============================================
# INQUIRIES - PUBLIC (Create only)
# =============================================
print('\n--- INQUIRIES (Public Create) ---')
test_endpoint('POST /inquiries/ (validation)', 'POST', 
              f'{BASE}/inquiries/', expected_status=400, json_data={})

# =============================================
# AUTH - PUBLIC
# =============================================
print('\n--- AUTH (Public) ---')
test_endpoint('POST /auth/login/ (invalid)', 'POST', 
              f'{BASE}/auth/login/', expected_status=400, 
              json_data={'email': 'fake@test.com', 'password': 'wrong'})
test_endpoint('POST /auth/register/ (validation)', 'POST', 
              f'{BASE}/auth/register/', expected_status=400, json_data={})

# =============================================
# SUMMARY
# =============================================
print('\n' + '='*60)
total = passed + failed
print(f'RESULTS: {passed}/{total} PASSED ({passed/total*100:.0f}%)')
if failed == 0:
    print('ALL PUBLIC ENDPOINTS WORKING! ✓')
else:
    print(f'{failed} endpoint(s) need attention')
print('='*60)
