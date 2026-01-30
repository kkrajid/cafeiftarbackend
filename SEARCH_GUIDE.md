# 🔍 Search Functionality Documentation

## ✅ YES - Search is FULLY ENABLED!

Your backend has comprehensive search functionality across multiple endpoints.

---

## 📋 Search-Enabled Endpoints

### 1. 🍽️ Menu Items (`/api/menu/`)

**Search Fields:**

- `name` - Item name
- `description` - Item description

**Example:**

```bash
GET /api/menu/?search=chicken
GET /api/menu/?search=biryani
GET /api/menu/?search=spicy
```

**Response:** Searches both name AND description fields

---

### 2. 📅 Reservations (`/api/reservations/`)

**Search Fields:**

- `confirmation_id` - Booking confirmation code (e.g., CI8A3F2B1D)
- `customer_name` - Customer's name
- `phone` - Phone number
- `email` - Email address

**Example:**

```bash
GET /api/reservations/?search=CI8A3F2B1D
GET /api/reservations/?search=john
GET /api/reservations/?search=9876543210
GET /api/reservations/?search=customer@email.com
```

**Note:** Requires admin authentication

---

### 3. 📧 Inquiries (`/api/inquiries/`)

**Search Fields:**

- `name` - Customer name
- `email` - Customer email
- `subject` - Inquiry subject

**Example:**

```bash
GET /api/inquiries/?search=booking
GET /api/inquiries/?search=john@example.com
GET /api/inquiries/?search=event
```

**Note:** Requires admin authentication

---

## 💡 How Search Works

### Case-Insensitive

```bash
# These all work the same:
?search=CHICKEN
?search=chicken
?search=ChIcKeN
```

### Multi-Field Search

Search queries automatically look across ALL configured fields:

```bash
# Searches in BOTH name AND description
GET /api/menu/?search=spicy
```

### Partial Matching

Search finds partial matches:

```bash
# Finds "Chicken Biryani", "Grilled Chicken", "Chicken Tikka"
GET /api/menu/?search=chicken
```

---

## 🎯 Combining Search with Filters

You can combine search with filters for powerful queries:

### Menu Examples

```bash
# Search for "chicken" only in Main Course
GET /api/menu/?search=chicken&category=Main Course

# Search for "spicy" only in vegetarian items
GET /api/menu/?search=spicy&is_veg=true

# Search for "rice" items that are in stock
GET /api/menu/?search=rice&status=in_stock
```

### Reservation Examples

```bash
# Search for customer "john" with pending status
GET /api/reservations/?search=john&status=pending

# Search confirmation IDs at specific branch
GET /api/reservations/?search=CI&branch=1

# Search by date and customer
GET /api/reservations/?search=john&date=2026-01-30
```

---

## 🔧 Technical Implementation

### Configuration

**File:** `config/settings.py`

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',  # ← Search enabled here
        'rest_framework.filters.OrderingFilter',
    ),
}
```

### ViewSet Configuration

**Example from** `apps/menu/views.py`:

```python
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_fields = ['category', 'status', 'is_veg', 'is_spicy']
    search_fields = ['name', 'description']  # ← Defines searchable fields
```

---

## 📱 Frontend Integration

### Basic Search

```javascript
async function searchMenu(query) {
  const response = await fetch(
    `http://localhost:8000/api/menu/?search=${encodeURIComponent(query)}`,
  );
  const data = await response.json();
  return data.results; // Returns matching items
}

// Usage
const results = await searchMenu("chicken");
```

### Search + Filters

```javascript
async function searchMenuWithFilters(query, filters) {
  const params = new URLSearchParams({
    search: query,
    ...filters,
  });

  const response = await fetch(`http://localhost:8000/api/menu/?${params}`);
  const data = await response.json();
  return data.results;
}

// Usage
const results = await searchMenuWithFilters("spicy", {
  category: "Main Course",
  is_veg: true,
});
```

### Search with Debouncing (React Example)

```javascript
import { useState, useEffect } from "react";
import { debounce } from "lodash";

function SearchMenu() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  useEffect(() => {
    const searchDebounced = debounce(async (searchQuery) => {
      if (searchQuery.length < 2) return;

      const response = await fetch(
        `http://localhost:8000/api/menu/?search=${searchQuery}`,
      );
      const data = await response.json();
      setResults(data.results);
    }, 300);

    searchDebounced(query);
  }, [query]);

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search menu..."
      />
      {results.map((item) => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}
```

---

## 🧪 Testing Search

### Test Script

Run the test script to verify search:

```bash
python test_search.py
```

### Manual Testing

```bash
# 1. Add some data via Django admin
http://localhost:8000/admin/

# 2. Test search
curl "http://localhost:8000/api/menu/?search=chicken"

# 3. Test with filters
curl "http://localhost:8000/api/menu/?search=chicken&category=Main"
```

---

## 📊 Search Performance Tips

### 1. Use Specific Searches

```bash
# Better (more specific)
?search=chicken biryani

# Less efficient (too broad)
?search=a
```

### 2. Combine with Filters

```bash
# Better (narrows results)
?search=rice&category=Main Course

# Less efficient (searches everything)
?search=rice
```

### 3. Database Indexing

For production, add database indexes on frequently searched fields:

```python
class MenuItem(models.Model):
    name = models.CharField(max_length=100, db_index=True)  # ← Add index
    description = models.TextField()
```

---

## 🎓 Search Examples by Use Case

### Customer Looking for Food

```bash
# "I want biryani"
GET /api/menu/?search=biryani

# "Show me vegetarian appetizers"
GET /api/menu/?search=appetizer&is_veg=true

# "What spicy dishes do you have?"
GET /api/menu/?search=spicy
```

### Admin Managing Reservations

```bash
# "Find reservation CI8A3F2B1D"
GET /api/reservations/?search=CI8A3F2B1D

# "Show all bookings for John"
GET /api/reservations/?search=john

# "Find reservations with this phone number"
GET /api/reservations/?search=9876543210
```

### Admin Checking Inquiries

```bash
# "Find inquiry from john@example.com"
GET /api/inquiries/?search=john@example.com

# "Show inquiries about booking"
GET /api/inquiries/?search=booking
```

---

## ✅ Summary

**Search Status:** FULLY FUNCTIONAL ✅

**Available On:**

- ✅ Menu Items (name, description)
- ✅ Reservations (confirmation_id, name, phone, email)
- ✅ Inquiries (name, email, subject)

**Features:**

- ✅ Case-insensitive
- ✅ Partial matching
- ✅ Multi-field search
- ✅ Works with filters
- ✅ Works with pagination

**Performance:** Optimized with DRF's built-in SearchFilter

---

## 🚀 Ready to Use!

Search is production-ready and can be integrated into your frontend immediately!
