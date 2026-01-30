"""
Complete Admin Endpoints Test Suite
Tests ALL admin-side endpoints with full CRUD operations
"""
import requests
import json
from datetime import date, timedelta

BASE = 'http://127.0.0.1:8000/api'

print('='*70)
print('COMPLETE ADMIN ENDPOINTS TEST SUITE')
print('='*70)

# Login
print('\n[LOGIN]')
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
        r = requests.request(method, url, headers=headers, json=data, timeout=10)
        if r.status_code == expected:
            print(f'  ✓ {name}')
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
# 1. AUTH ADMIN
# =============================================
print('\n--- 1. AUTH ---')
test('GET /auth/me/', 'GET', f'{BASE}/auth/me/')
test('PATCH /auth/me/', 'PATCH', f'{BASE}/auth/me/', data={'first_name': 'Super'})

# =============================================
# 2. DASHBOARD STATS
# =============================================
print('\n--- 2. DASHBOARD STATS ---')
test('GET /dashboard/stats/', 'GET', f'{BASE}/dashboard/stats/')
test('GET /dashboard/stats/reservation-trends/', 'GET', f'{BASE}/dashboard/stats/reservation-trends/')
test('GET /dashboard/stats/branch-performance/', 'GET', f'{BASE}/dashboard/stats/branch-performance/')
test('GET /dashboard/stats/menu-analytics/', 'GET', f'{BASE}/dashboard/stats/menu-analytics/')

# =============================================
# 3. BRANCHES
# =============================================
print('\n--- 3. BRANCHES ---')
test('GET /branches/', 'GET', f'{BASE}/branches/')

ok, branch = test('POST /branches/', 'POST', f'{BASE}/branches/', 201, data={
    'name': 'Admin Test Branch',
    'address': '999 Admin St',
    'phone': '+911234567899',
    'status': 'active',
    'hours': '10:00 AM - 10:00 PM',
    'opening_time': '10:00:00',
    'closing_time': '22:00:00'
})
if ok:
    bid = branch.get('id')
    test(f'GET /branches/{bid}/', 'GET', f'{BASE}/branches/{bid}/')
    test(f'PATCH /branches/{bid}/', 'PATCH', f'{BASE}/branches/{bid}/', data={'name': 'Updated Test Branch'})
    test(f'DELETE /branches/{bid}/', 'DELETE', f'{BASE}/branches/{bid}/', 204)

# =============================================
# 4. OPERATING HOURS
# =============================================
print('\n--- 4. OPERATING HOURS ---')
test('GET /branches/operating-hours/', 'GET', f'{BASE}/branches/operating-hours/')

ok, oh = test('POST /branches/operating-hours/', 'POST', f'{BASE}/branches/operating-hours/', 201, data={
    'branch': 2,
    'day_of_week': 6,
    'opening_time': '12:00:00',
    'closing_time': '20:00:00',
    'is_closed': False
})
if ok:
    ohid = oh.get('id')
    test(f'GET /branches/operating-hours/{ohid}/', 'GET', f'{BASE}/branches/operating-hours/{ohid}/')
    test(f'PATCH /branches/operating-hours/{ohid}/', 'PATCH', f'{BASE}/branches/operating-hours/{ohid}/', 
         data={'opening_time': '11:00:00'})
    test(f'DELETE /branches/operating-hours/{ohid}/', 'DELETE', f'{BASE}/branches/operating-hours/{ohid}/', 204)

# =============================================
# 5. SPECIAL DATES
# =============================================
print('\n--- 5. SPECIAL DATES ---')
test('GET /branches/special-dates/', 'GET', f'{BASE}/branches/special-dates/')

ok, sd = test('POST /branches/special-dates/', 'POST', f'{BASE}/branches/special-dates/', 201, data={
    'branch': 2,
    'date': next_month,
    'type': 'holiday',
    'is_closed': True,
    'note': 'Admin Test Holiday'
})
if ok:
    sdid = sd.get('id')
    test(f'GET /branches/special-dates/{sdid}/', 'GET', f'{BASE}/branches/special-dates/{sdid}/')
    test(f'PATCH /branches/special-dates/{sdid}/', 'PATCH', f'{BASE}/branches/special-dates/{sdid}/', 
         data={'note': 'Updated Holiday'})
    test(f'DELETE /branches/special-dates/{sdid}/', 'DELETE', f'{BASE}/branches/special-dates/{sdid}/', 204)

# =============================================
# 6. TABLES
# =============================================
print('\n--- 6. TABLES ---')
test('GET /tables/', 'GET', f'{BASE}/tables/')
test('GET /tables/availability/', 'GET', f'{BASE}/tables/availability/?branch=2&date={tomorrow}&time=19:00&guests=4')
test('GET /tables/available_slots/', 'GET', f'{BASE}/tables/available_slots/?branch=2&date={tomorrow}&guests=4')

ok, table = test('POST /tables/', 'POST', f'{BASE}/tables/', 201, data={
    'branch': 2,
    'table_id': 'ADM-T01',
    'name': 'Admin Test Table',
    'seats': 6,
    'status': 'active',
    'location': 'outdoor'
})
if ok:
    tid = table.get('id')
    test(f'GET /tables/{tid}/', 'GET', f'{BASE}/tables/{tid}/')
    test(f'PATCH /tables/{tid}/', 'PATCH', f'{BASE}/tables/{tid}/', data={'seats': 8})
    test(f'DELETE /tables/{tid}/', 'DELETE', f'{BASE}/tables/{tid}/', 204)

# =============================================
# 7. RESERVATIONS
# =============================================
print('\n--- 7. RESERVATIONS ---')
test('GET /reservations/', 'GET', f'{BASE}/reservations/')
test('GET /reservations/stats/', 'GET', f'{BASE}/reservations/stats/')
test('GET /reservations/today/?branch=2', 'GET', f'{BASE}/reservations/today/?branch=2')
test('GET /reservations/my_reservations/?email=test@test.com', 'GET', 
     f'{BASE}/reservations/my_reservations/?email=test@test.com')

# =============================================
# 8. MENU CATEGORIES
# =============================================
print('\n--- 8. MENU CATEGORIES ---')
test('GET /menu/categories/', 'GET', f'{BASE}/menu/categories/')

ok, cat = test('POST /menu/categories/', 'POST', f'{BASE}/menu/categories/', 201, data={
    'name': 'Admin Test Category',
    'description': 'Test category',
    'icon': 'Utensils'
})
if ok:
    catslug = cat.get('slug')
    test(f'GET /menu/categories/{catslug}/', 'GET', f'{BASE}/menu/categories/{catslug}/')
    test(f'PATCH /menu/categories/{catslug}/', 'PATCH', f'{BASE}/menu/categories/{catslug}/', 
         data={'description': 'Updated description'})
    test(f'DELETE /menu/categories/{catslug}/', 'DELETE', f'{BASE}/menu/categories/{catslug}/', 204)

# =============================================
# 9. MENU ITEMS
# =============================================
print('\n--- 9. MENU ITEMS ---')
test('GET /menu/', 'GET', f'{BASE}/menu/')
test('GET /menu/featured/', 'GET', f'{BASE}/menu/featured/')

ok, item = test('POST /menu/', 'POST', f'{BASE}/menu/', 201, data={
    'name': 'Admin Test Dish',
    'description': 'Delicious admin test dish',
    'price': '599.00',
    'category_text': 'Starters',
    'is_veg': False,
    'is_spicy': True,
    'is_featured': True,
    'featured_order': 1
})
if ok:
    itemid = item.get('id')
    test(f'GET /menu/{itemid}/', 'GET', f'{BASE}/menu/{itemid}/')
    test(f'PATCH /menu/{itemid}/', 'PATCH', f'{BASE}/menu/{itemid}/', data={'price': '649.00'})
    test(f'PATCH /menu/{itemid}/toggle_featured/', 'PATCH', f'{BASE}/menu/{itemid}/toggle_featured/')
    test(f'DELETE /menu/{itemid}/', 'DELETE', f'{BASE}/menu/{itemid}/', 204)

# =============================================
# 10. DEALS
# =============================================
print('\n--- 10. DEALS ---')
test('GET /deals/', 'GET', f'{BASE}/deals/')

ok, deal = test('POST /deals/', 'POST', f'{BASE}/deals/', 201, data={
    'title': 'Admin Test Deal',
    'description': 'Amazing admin test deal!',
    'code': 'ADMINTEST99',
    'discount_type': 'percentage',
    'discount_value': '25.00',
    'valid_from': date.today().isoformat(),
    'valid_until': next_month,
    'tag': 'Test',
    'status': 'active'
})
if ok:
    dealid = deal.get('id')
    test(f'GET /deals/{dealid}/', 'GET', f'{BASE}/deals/{dealid}/')
    test(f'PATCH /deals/{dealid}/', 'PATCH', f'{BASE}/deals/{dealid}/', data={'discount_value': '30.00'})
    test(f'DELETE /deals/{dealid}/', 'DELETE', f'{BASE}/deals/{dealid}/', 204)

# =============================================
# 11. INQUIRIES
# =============================================
print('\n--- 11. INQUIRIES ---')
test('GET /inquiries/', 'GET', f'{BASE}/inquiries/')

# =============================================
# 12. GALLERY
# =============================================
print('\n--- 12. GALLERY ---')
test('GET /gallery/', 'GET', f'{BASE}/gallery/')

# =============================================
# SUMMARY
# =============================================
print('\n' + '='*70)
total = passed + failed
pct = (passed/total*100) if total > 0 else 0
print(f'FINAL RESULTS: {passed}/{total} PASSED ({pct:.0f}%)')
if failed == 0:
    print('✅ ALL ADMIN ENDPOINTS WORKING CORRECTLY!')
else:
    print(f'⚠️  {failed} endpoint(s) need attention')
print('='*70)
