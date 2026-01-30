"""
Test ALL admin-side endpoints - Full CRUD operations
"""
import requests
import json
from datetime import date, timedelta

BASE = 'http://127.0.0.1:8000/api'

print('='*60)
print('TESTING ALL ADMIN ENDPOINTS (Full CRUD)')
print('='*60)

# Login first
print('\n[LOGIN] Authenticating as admin...')
r = requests.post(f'{BASE}/auth/login/', json={
    'email': 'admin@cafeiftar.com',
    'password': 'Admin@123'
})

if r.status_code != 200:
    print(f'  Login failed: {r.text}')
    exit(1)

data = r.json()
token = data['access']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
print(f'  ✓ Logged in as: {data["user"]["email"]} (role: {data["user"]["role"]})')

# Track results
passed = 0
failed = 0
tomorrow = (date.today() + timedelta(days=1)).isoformat()
next_month = (date.today() + timedelta(days=30)).isoformat()

def test(name, method, url, expected=200, data=None):
    global passed, failed
    try:
        r = requests.request(method, url, headers=headers, json=data, timeout=5)
        if r.status_code == expected:
            print(f'  ✓ {name}: {r.status_code}')
            passed += 1
            try:
                return True, r.json()
            except:
                return True, {}
        else:
            print(f'  ✗ {name}: got {r.status_code}, expected {expected}')
            failed += 1
            return False, {}
    except Exception as e:
        print(f'  ✗ {name}: ERROR - {e}')
        failed += 1
        return False, {}

# =============================================
# AUTH ADMIN
# =============================================
print('\n--- AUTH ---')
test('GET /auth/me/', 'GET', f'{BASE}/auth/me/')
test('PATCH /auth/me/', 'PATCH', f'{BASE}/auth/me/', data={'first_name': 'Super'})

# =============================================
# BRANCHES ADMIN (CRUD)
# =============================================
print('\n--- BRANCHES (CRUD) ---')
test('GET /branches/', 'GET', f'{BASE}/branches/')

# CREATE
ok, branch = test('POST /branches/', 'POST', f'{BASE}/branches/', 201, data={
    'name': 'Test Branch Admin',
    'address': '123 Test St',
    'phone': '+911234567890',
    'status': 'active',
    'hours': '10:00 AM - 10:00 PM',
    'opening_time': '10:00:00',
    'closing_time': '22:00:00'
})
if ok:
    bid = branch.get('id')
    test(f'PATCH /branches/{bid}/', 'PATCH', f'{BASE}/branches/{bid}/', data={'name': 'Updated Branch'})
    test(f'DELETE /branches/{bid}/', 'DELETE', f'{BASE}/branches/{bid}/', 204)

# =============================================
# OPERATING HOURS ADMIN
# =============================================
print('\n--- OPERATING HOURS ---')
test('GET /branches/operating-hours/', 'GET', f'{BASE}/branches/operating-hours/')

# CREATE
ok, oh = test('POST /branches/operating-hours/', 'POST', f'{BASE}/branches/operating-hours/', 201, data={
    'branch': 2,
    'day_of_week': 6,  # Sunday
    'opening_time': '12:00:00',
    'closing_time': '20:00:00',
    'is_closed': False
})
if ok:
    ohid = oh.get('id')
    test(f'GET /branches/operating-hours/{ohid}/', 'GET', f'{BASE}/branches/operating-hours/{ohid}/')
    test(f'DELETE /branches/operating-hours/{ohid}/', 'DELETE', f'{BASE}/branches/operating-hours/{ohid}/', 204)

# =============================================
# SPECIAL DATES ADMIN
# =============================================
print('\n--- SPECIAL DATES ---')
test('GET /branches/special-dates/', 'GET', f'{BASE}/branches/special-dates/')

# CREATE
ok, sd = test('POST /branches/special-dates/', 'POST', f'{BASE}/branches/special-dates/', 201, data={
    'branch': 2,
    'date': next_month,
    'type': 'holiday',
    'is_closed': True,
    'note': 'Test Holiday'
})
if ok:
    sdid = sd.get('id')
    test(f'GET /branches/special-dates/{sdid}/', 'GET', f'{BASE}/branches/special-dates/{sdid}/')
    test(f'DELETE /branches/special-dates/{sdid}/', 'DELETE', f'{BASE}/branches/special-dates/{sdid}/', 204)

# =============================================
# TABLES ADMIN (CRUD)
# =============================================
print('\n--- TABLES (CRUD) ---')
test('GET /tables/', 'GET', f'{BASE}/tables/')

# CREATE
ok, table = test('POST /tables/', 'POST', f'{BASE}/tables/', 201, data={
    'branch': 2,
    'table_id': 'TEST-99',
    'name': 'Test Table',
    'seats': 4,
    'status': 'active',
    'location': 'indoor'
})
if ok:
    tid = table.get('id')
    test(f'PATCH /tables/{tid}/', 'PATCH', f'{BASE}/tables/{tid}/', data={'name': 'Updated Table'})
    test(f'DELETE /tables/{tid}/', 'DELETE', f'{BASE}/tables/{tid}/', 204)

# =============================================
# MENU ADMIN (CRUD)
# =============================================
print('\n--- MENU (CRUD) ---')
test('GET /menu/', 'GET', f'{BASE}/menu/')
test('GET /menu/categories/', 'GET', f'{BASE}/menu/categories/')

# CREATE CATEGORY
ok, cat = test('POST /menu/categories/', 'POST', f'{BASE}/menu/categories/', 201, data={
    'name': 'Test Category',
    'description': 'Test desc',
    'icon': 'Utensils'
})
if ok:
    catslug = cat.get('slug')
    test(f'DELETE /menu/categories/{catslug}/', 'DELETE', f'{BASE}/menu/categories/{catslug}/', 204)

# CREATE MENU ITEM
ok, item = test('POST /menu/', 'POST', f'{BASE}/menu/', 201, data={
    'name': 'Test Dish',
    'description': 'Delicious test dish',
    'price': '299.00',
    'category_text': 'Starters',
    'is_veg': True,
    'is_featured': True
})
if ok:
    itemid = item.get('id')
    test(f'PATCH /menu/{itemid}/', 'PATCH', f'{BASE}/menu/{itemid}/', data={'name': 'Updated Dish'})
    test(f'PATCH /menu/{itemid}/toggle_featured/', 'PATCH', f'{BASE}/menu/{itemid}/toggle_featured/')
    test(f'DELETE /menu/{itemid}/', 'DELETE', f'{BASE}/menu/{itemid}/', 204)

# =============================================
# RESERVATIONS ADMIN
# =============================================
print('\n--- RESERVATIONS ---')
test('GET /reservations/', 'GET', f'{BASE}/reservations/')
test('GET /reservations/stats/', 'GET', f'{BASE}/reservations/stats/')
test('GET /reservations/today/?branch=2', 'GET', f'{BASE}/reservations/today/?branch=2')

# =============================================
# DEALS ADMIN (CRUD)
# =============================================
print('\n--- DEALS (CRUD) ---')
test('GET /deals/', 'GET', f'{BASE}/deals/')

ok, deal = test('POST /deals/', 'POST', f'{BASE}/deals/', 201, data={
    'title': 'Test Deal',
    'description': '20% off all items',
    'code': 'TESTCODE99',
    'discount_type': 'percentage',
    'discount_value': '20.00',
    'valid_from': date.today().isoformat(),
    'valid_until': next_month,
    'tag': 'Special',
    'status': 'active'
})
if ok:
    dealid = deal.get('id')
    test(f'PATCH /deals/{dealid}/', 'PATCH', f'{BASE}/deals/{dealid}/', data={'title': 'Updated Deal'})
    test(f'DELETE /deals/{dealid}/', 'DELETE', f'{BASE}/deals/{dealid}/', 204)

# =============================================
# INQUIRIES ADMIN
# =============================================
print('\n--- INQUIRIES ---')
test('GET /inquiries/', 'GET', f'{BASE}/inquiries/')

# =============================================
# GALLERY ADMIN (CRUD)
# =============================================
print('\n--- GALLERY (CRUD) ---')
test('GET /gallery/', 'GET', f'{BASE}/gallery/')

# =============================================
# SUMMARY
# =============================================
print('\n' + '='*60)
total = passed + failed
pct = (passed/total*100) if total > 0 else 0
print(f'RESULTS: {passed}/{total} PASSED ({pct:.0f}%)')
if failed == 0:
    print('ALL ADMIN ENDPOINTS WORKING! ✓')
else:
    print(f'{failed} endpoint(s) need attention')
print('='*60)
