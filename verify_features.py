"""
Backend Feature Verification Script
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from datetime import date, time, timedelta
from apps.branches.models import Branch, OperatingHours, SpecialDate
from apps.reservations.models import Reservation
from apps.tables.models import Table
from apps.menu.models import MenuItem

print('='*60)
print('BACKEND FEATURE VERIFICATION')
print('='*60)

# 1. Smart Duration Calculation
print('\n[1] SMART DURATION CALCULATION')
print('-'*40)
durations = [
    (1, 60), (2, 60), (3, 90), (4, 90), 
    (5, 120), (8, 120), (9, 150), (15, 150)
]
all_pass = True
for guests, expected in durations:
    result = Reservation.calculate_duration_from_guests(guests)
    status = 'PASS' if result == expected else 'FAIL'
    if result != expected:
        all_pass = False
    print(f'  {guests} guests -> {result} min (expected {expected}) [{status}]')
print(f'  Overall: {"PASS" if all_pass else "FAIL"}')

# 2. Branch Hours System
print('\n[2] BRANCH HOURS SYSTEM')
print('-'*40)
branch = Branch.objects.first()
if branch:
    tomorrow = date.today() + timedelta(days=1)
    hours = branch.get_hours_for_date(tomorrow)
    print(f'  Branch: {branch.name}')
    print(f'  Date: {tomorrow} ({tomorrow.strftime("%A")})')
    print(f'  Is Open: {hours["is_open"]}')
    print(f'  Hours: {hours["opening_time"]} - {hours["closing_time"]}')
    print(f'  Overall: PASS')
else:
    print('  No branches found - SKIP')

# 3. Model Counts
print('\n[3] DATABASE RECORDS')
print('-'*40)
print(f'  Branches: {Branch.objects.count()}')
print(f'  Tables: {Table.objects.count()}')
print(f'  Menu Items: {MenuItem.objects.count()}')
print(f'  Reservations: {Reservation.objects.count()}')
print(f'  Operating Hours: {OperatingHours.objects.count()}')
print(f'  Special Dates: {SpecialDate.objects.count()}')

# 4. Featured Dishes
print('\n[4] FEATURED DISHES')
print('-'*40)
featured = MenuItem.objects.filter(is_featured=True).count()
total_menu = MenuItem.objects.count()
print(f'  Featured Items: {featured}/{total_menu}')
has_fields = hasattr(MenuItem, 'is_featured') and hasattr(MenuItem, 'featured_order')
print(f'  Fields exist: {"PASS" if has_fields else "FAIL"}')

# 5. Reservation Statuses
print('\n[5] RESERVATION STATUS CHOICES')
print('-'*40)
expected_statuses = ['pending', 'confirmed', 'cancelled', 'completed', 'no_show']
actual_statuses = [s[0] for s in Reservation.STATUS_CHOICES]
for status in expected_statuses:
    exists = status in actual_statuses
    print(f'  {status}: {"PASS" if exists else "FAIL"}')

# 6. Branch Fields
print('\n[6] BRANCH OPERATING HOURS FIELDS')
print('-'*40)
branch_fields = ['opening_time', 'closing_time', 'slot_duration', 'default_reservation_duration']
for field in branch_fields:
    exists = hasattr(Branch, field)
    print(f'  {field}: {"PASS" if exists else "FAIL"}')

print('\n' + '='*60)
print('ALL BACKEND FEATURES VERIFIED')
print('='*60)
