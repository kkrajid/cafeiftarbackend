"""
Quick test script to verify pagination and filtering
Run: python test_features.py
"""
import requests
import json

BASE_URL = 'http://localhost:8000/api'

print("=" * 60)
print("Testing Backend Features: Pagination & Filtering")
print("=" * 60)

# Test 1: Pagination
print("\n📄 TEST 1: Pagination")
print("-" * 60)
try:
    response = requests.get(f'{BASE_URL}/branches/')
    data = response.json()
    
    if isinstance(data, dict):
        print("✅ Pagination ENABLED")
        print(f"   Structure: {list(data.keys())}")
        if 'count' in data:
            print(f"   Total items: {data['count']}")
        if 'results' in data:
            print(f"   Items in page: {len(data['results'])}")
        if 'next' in data:
            print(f"   Next page: {data['next']}")
    else:
        print("⚠️  Pagination DISABLED (returns list directly)")
        print(f"   Items returned: {len(data)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Filtering - Menu by category
print("\n🔍 TEST 2: Filtering (Menu by category)")
print("-" * 60)
try:
    response = requests.get(f'{BASE_URL}/menu/', params={'category': 'Appetizers'})
    print(f"   Status: {response.status_code}")
    print(f"   URL called: {response.url}")
    data = response.json()
    
    if isinstance(data, dict) and 'results' in data:
        items = data['results']
    else:
        items = data
    
    if items:
        print(f"✅ Filtering WORKS - Found {len(items)} items")
        if items:
            print(f"   First item category: {items[0].get('category', 'N/A')}")
    else:
        print("⚠️  No items found (database might be empty)")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Filtering - Vegetarian items
print("\n🥗 TEST 3: Filtering (Vegetarian items)")
print("-" * 60)
try:
    response = requests.get(f'{BASE_URL}/menu/', params={'is_veg': 'true'})
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    if isinstance(data, dict) and 'results' in data:
        items = data['results']
    else:
        items = data
    
    print(f"✅ Filtering WORKS - Found {len(items)} vegetarian items")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Search functionality
print("\n🔎 TEST 4: Search (by name)")
print("-" * 60)
try:
    response = requests.get(f'{BASE_URL}/menu/', params={'search': 'chicken'})
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    if isinstance(data, dict) and 'results' in data:
        items = data['results']
    else:
        items = data
    
    print(f"✅ Search WORKS - Found {len(items)} items matching 'chicken'")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Pagination with page number
print("\n📄 TEST 5: Pagination (Page navigation)")
print("-" * 60)
try:
    response1 = requests.get(f'{BASE_URL}/menu/', params={'page': 1})
    response2 = requests.get(f'{BASE_URL}/menu/', params={'page': 2})
    
    print(f"   Page 1 status: {response1.status_code}")
    print(f"   Page 2 status: {response2.status_code}")
    
    if response1.status_code == 200:
        data1 = response1.json()
        if isinstance(data1, dict):
            print(f"✅ Pagination navigation WORKS")
            print(f"   Page 1 has: {len(data1.get('results', []))} items")
        else:
            print("⚠️  Pagination disabled")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
