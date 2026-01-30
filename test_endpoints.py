"""
Comprehensive API Endpoint Test Script
Tests all endpoints for Cafe Iftar backend
"""
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

import requests
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BLUE = "\033[94m"

def test_endpoint(name, method, url, expected_status=200, auth_token=None, data=None):
    """Test a single endpoint"""
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data, timeout=5)
        else:
            response = requests.request(method, url, headers=headers, json=data, timeout=5)
        
        if response.status_code == expected_status:
            print(f"  {GREEN}✓{RESET} {name}: {method} {url} -> {response.status_code}")
            return True, response
        else:
            print(f"  {RED}✗{RESET} {name}: {method} {url} -> {response.status_code} (expected {expected_status})")
            return False, response
    except Exception as e:
        print(f"  {RED}✗{RESET} {name}: {method} {url} -> ERROR: {e}")
        return False, None

def run_tests():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}   CAFE IFTAR API ENDPOINT TESTS{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    results = {"passed": 0, "failed": 0}
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # ============================================
    # PUBLIC ENDPOINTS (No Auth Required)
    # ============================================
    print(f"{YELLOW}PUBLIC ENDPOINTS{RESET}")
    print("-" * 40)
    
    # Branches
    ok, _ = test_endpoint("List Branches", "GET", f"{BASE_URL}/branches/")
    results["passed" if ok else "failed"] += 1
    
    ok, resp = test_endpoint("Branch Details", "GET", f"{BASE_URL}/branches/2/")
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Branch Hours", "GET", f"{BASE_URL}/branches/2/hours/")
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Branch Hours for Date", "GET", f"{BASE_URL}/branches/2/hours/{tomorrow}/")
    results["passed" if ok else "failed"] += 1
    
    # Tables
    ok, _ = test_endpoint("List Tables", "GET", f"{BASE_URL}/tables/")
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Table Availability", "GET", f"{BASE_URL}/tables/availability/?branch=2&date={tomorrow}&time=19:00&guests=4")
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Available Slots", "GET", f"{BASE_URL}/tables/available_slots/?branch=2&date={tomorrow}&guests=4")
    results["passed" if ok else "failed"] += 1
    
    # Menu
    ok, _ = test_endpoint("List Menu Items", "GET", f"{BASE_URL}/menu/")
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Featured Dishes", "GET", f"{BASE_URL}/menu/featured/")
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Featured (with limit)", "GET", f"{BASE_URL}/menu/featured/?limit=3")
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Menu Categories", "GET", f"{BASE_URL}/menu/categories/")
    results["passed" if ok else "failed"] += 1
    
    # Deals
    ok, _ = test_endpoint("List Deals", "GET", f"{BASE_URL}/deals/")
    results["passed" if ok else "failed"] += 1
    
    # Gallery
    ok, _ = test_endpoint("List Gallery", "GET", f"{BASE_URL}/gallery/")
    results["passed" if ok else "failed"] += 1
    
    # Reservations (public)
    ok, _ = test_endpoint("My Reservations", "GET", f"{BASE_URL}/reservations/my_reservations/?email=test@test.com")
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Lookup by Confirmation", "GET", f"{BASE_URL}/reservations/by_confirmation/?confirmation_id=INVALID", expected_status=404)
    results["passed" if ok else "failed"] += 1
    
    # ============================================
    # AUTH ENDPOINTS
    # ============================================
    print(f"\n{YELLOW}AUTH ENDPOINTS{RESET}")
    print("-" * 40)
    
    # Try login with test credentials
    ok, resp = test_endpoint("Login (invalid)", "POST", f"{BASE_URL}/auth/login/", 
                              expected_status=401, data={"username": "test", "password": "wrong"})
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Get Current User (no auth)", "GET", f"{BASE_URL}/auth/me/", expected_status=401)
    results["passed" if ok else "failed"] += 1
    
    # ============================================
    # ADMIN-ONLY ENDPOINTS (should return 401/403)
    # ============================================
    print(f"\n{YELLOW}ADMIN-ONLY ENDPOINTS (expecting 401/403){RESET}")
    print("-" * 40)
    
    ok, _ = test_endpoint("Reservation Stats (no auth)", "GET", f"{BASE_URL}/reservations/stats/", expected_status=401)
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Today's Reservations (no auth)", "GET", f"{BASE_URL}/reservations/today/?branch=2", expected_status=401)
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Create Menu Item (no auth)", "POST", f"{BASE_URL}/menu/", expected_status=401,
                          data={"name": "Test", "description": "Test", "price": 100})
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Operating Hours Admin (no auth)", "GET", f"{BASE_URL}/branches/operating-hours/", expected_status=401)
    results["passed" if ok else "failed"] += 1
    
    ok, _ = test_endpoint("Special Dates Admin (no auth)", "GET", f"{BASE_URL}/branches/special-dates/", expected_status=401)
    results["passed" if ok else "failed"] += 1
    
    # ============================================
    # RESERVATION CREATION (Public)
    # ============================================
    print(f"\n{YELLOW}RESERVATION CREATION{RESET}")
    print("-" * 40)
    
    # Test reservation creation with validation error (missing fields)
    ok, _ = test_endpoint("Create Reservation (invalid)", "POST", f"{BASE_URL}/reservations/", 
                          expected_status=400, data={})
    results["passed" if ok else "failed"] += 1
    
    # ============================================
    # SUMMARY
    # ============================================
    print(f"\n{BLUE}{'='*60}{RESET}")
    total = results["passed"] + results["failed"]
    pass_rate = (results["passed"] / total * 100) if total > 0 else 0
    
    if results["failed"] == 0:
        print(f"{GREEN}ALL {total} TESTS PASSED! ✓{RESET}")
    else:
        print(f"Tests: {results['passed']}/{total} passed ({pass_rate:.0f}%)")
        print(f"{GREEN}Passed: {results['passed']}{RESET} | {RED}Failed: {results['failed']}{RESET}")
    
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    return results["failed"] == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
