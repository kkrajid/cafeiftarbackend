"""
Test Search Functionality
Run: python test_search.py
"""
import requests
import json

BASE_URL = 'http://localhost:8000/api'

print("=" * 70)
print("🔍 Testing SEARCH Functionality")
print("=" * 70)

# First, let's create some test data via admin
print("\n📝 Note: Make sure you have some data in the database first!")
print("   Use Django admin to add menu items, reservations, etc.")
print("-" * 70)

# Test 1: Search Menu Items
print("\n🍽️  TEST 1: Search Menu by Name/Description")
print("-" * 70)

test_queries = ['chicken', 'biryani', 'spicy', 'rice']

for query in test_queries:
    try:
        response = requests.get(f'{BASE_URL}/menu/', params={'search': query})
        data = response.json()
        
        results = data.get('results', data) if isinstance(data, dict) else data
        count = data.get('count', len(results)) if isinstance(data, dict) else len(results)
        
        print(f"   Search '{query}': Found {count} items")
        if results:
            for item in results[:2]:  # Show first 2
                print(f"      - {item.get('name', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error searching '{query}': {e}")

# Test 2: Search Reservations
print("\n📅 TEST 2: Search Reservations")
print("-" * 70)

search_terms = ['CI', 'john', '9876543210', 'test@example.com']

for term in search_terms:
    try:
        # Need to authenticate for reservations
        response = requests.get(f'{BASE_URL}/reservations/', params={'search': term})
        
        if response.status_code == 401:
            print(f"   Search '{term}': ⚠️  Requires authentication (admin only)")
            break
        
        data = response.json()
        results = data.get('results', data) if isinstance(data, dict) else data
        count = data.get('count', len(results)) if isinstance(data, dict) else len(results)
        
        print(f"   Search '{term}': Found {count} reservations")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Test 3: Search Inquiries
print("\n📧 TEST 3: Search Inquiries")
print("-" * 70)

try:
    response = requests.get(f'{BASE_URL}/inquiries/', params={'search': 'booking'})
    
    if response.status_code == 401:
        print("   ⚠️  Requires authentication (admin only)")
    else:
        data = response.json()
        results = data.get('results', data) if isinstance(data, dict) else data
        count = data.get('count', len(results)) if isinstance(data, dict) else len(results)
        print(f"   Search 'booking': Found {count} inquiries")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Demonstrate Search Fields
print("\n📋 TEST 4: What Fields are Searchable?")
print("-" * 70)
print("""
   Menu Items:
      - name
      - description
   
   Reservations:
      - confirmation_id
      - customer_name
      - phone
      - email
   
   Inquiries:
      - name
      - email
      - subject
""")

# Test 5: Advanced Search Examples
print("\n🎯 TEST 5: Advanced Search + Filter Combinations")
print("-" * 70)

examples = [
    {
        'url': f'{BASE_URL}/menu/',
        'params': {'search': 'chicken', 'category': 'Main Course'},
        'desc': 'Search "chicken" in Main Course category'
    },
    {
        'url': f'{BASE_URL}/menu/',
        'params': {'search': 'spicy', 'is_veg': 'true'},
        'desc': 'Search "spicy" in vegetarian items'
    }
]

for example in examples:
    try:
        response = requests.get(example['url'], params=example['params'])
        data = response.json()
        results = data.get('results', data) if isinstance(data, dict) else data
        count = data.get('count', len(results)) if isinstance(data, dict) else len(results)
        
        print(f"   {example['desc']}")
        print(f"   → Found {count} items")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ Search Testing Complete!")
print("=" * 70)
print("\n💡 Tips:")
print("   - Use ?search=query to search across multiple fields")
print("   - Combine with filters: ?search=chicken&category=Main")
print("   - Search is case-insensitive by default")
print("=" * 70)
