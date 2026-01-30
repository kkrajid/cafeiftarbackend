# Pagination & Filtering Guide

## ✅ Status: BOTH WORKING!

Pagination and filtering are both fully functional in your backend.

---

## 📄 Pagination

**Status:** ✅ ENABLED

### How It Works

All list endpoints return paginated responses:

```json
{
  "count": 100,           // Total items
  "next": "http://...?page=2",    // Next page URL
  "previous": null,        // Previous page URL
  "results": [...]         // Current page items
}
```

### Configuration

- **Page Size:** 20 items per page
- **Default Pagination Class:** `PageNumberPagination`
- **Location:** `config/settings.py`

### Usage Examples

```bash
# Get first page (default)
GET /api/menu/

# Get specific page
GET /api/menu/?page=2

# Results will be in the 'results' array
```

### Frontend Integration

```javascript
const response = await fetch("http://localhost:8000/api/menu/");
const data = await response.json();

console.log(data.count); // Total items
console.log(data.results); // Current page items
console.log(data.next); // Next page URL

// Load next page
if (data.next) {
  const nextPage = await fetch(data.next);
  const nextData = await nextPage.json();
}
```

---

## 🔍 Filtering

**Status:** ✅ ENABLED

### Available Filters by Endpoint

#### `/api/menu/`

- `category` - Filter by category
- `status` - Filter by stock status
- `is_veg` - Filter vegetarian items (true/false)
- `is_spicy` - Filter spicy items (true/false)
- `search` - Search in name and description

**Examples:**

```bash
GET /api/menu/?category=Appetizers
GET /api/menu/?is_veg=true
GET /api/menu/?search=chicken
GET /api/menu/?category=Main%20Course&is_veg=true
```

#### `/api/tables/`

- `branch` - Filter by branch ID
- `status` - Filter by status

**Examples:**

```bash
GET /api/tables/?branch=1
GET /api/tables/?status=active
GET /api/tables/?branch=1&status=active
```

#### `/api/reservations/`

- `branch` - Filter by branch ID
- `status` - Filter by status (pending/confirmed/cancelled)
- `date` - Filter by date
- `search` - Search by confirmation_id, name, phone, email

**Examples:**

```bash
GET /api/reservations/?status=pending
GET /api/reservations/?branch=1&date=2026-01-30
GET /api/reservations/?search=CI8A3F2B1D
```

#### `/api/deals/`

- `status` - Filter by status (active/paused/expired)
- `tag` - Filter by tag

**Examples:**

```bash
GET /api/deals/?status=active
GET /api/deals/?tag=Limited
```

#### `/api/inquiries/`

- `status` - Filter by status (new/read/replied)
- `search` - Search in name, email, subject

**Examples:**

```bash
GET /api/inquiries/?status=new
GET /api/inquiries/?search=john@example.com
```

#### `/api/gallery/`

- `category` - Filter by category (culinary/ambience/moments)

**Examples:**

```bash
GET /api/gallery/?category=culinary
```

---

## 🔎 Search Functionality

Search is available on endpoints with `search_fields` configured:

### Searchable Endpoints

1. **Menu** - Searches in: name, description
2. **Reservations** - Searches in: confirmation_id, customer_name, phone, email
3. **Inquiries** - Searches in: name, email, subject

**Usage:**

```bash
GET /api/menu/?search=biryani
GET /api/reservations/?search=john
GET /api/inquiries/?search=booking
```

---

## 🎯 Combining Filters, Search & Pagination

You can combine all features:

```bash
# Get page 2 of vegetarian appetizers
GET /api/menu/?category=Appetizers&is_veg=true&page=2

# Search for pending reservations at branch 1
GET /api/reservations/?status=pending&branch=1&search=CI8A

# Get active deals with limited tag
GET /api/deals/?status=active&tag=Limited
```

---

## 📊 Response Structure

### With Pagination (List endpoints)

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/menu/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Chicken Biryani",
      "category": "Main Course",
      ...
    },
    // ... 19 more items
  ]
}
```

### Single Item (Detail endpoints)

```json
{
  "id": 1,
  "name": "Chicken Biryani",
  "category": "Main Course",
  ...
}
```

---

## 🛠️ Testing

Run the test script to verify everything works:

```bash
python test_features.py
```

This will test:

- ✅ Pagination structure
- ✅ Filtering by category
- ✅ Filtering by boolean fields
- ✅ Search functionality
- ✅ Page navigation

---

## 💡 Tips for Frontend

### 1. Handle Both Paginated and Direct Responses

```javascript
function getItems(data) {
  // If paginated, use results array
  if (data.results) {
    return data.results;
  }
  // If direct array (shouldn't happen with pagination enabled)
  return data;
}
```

### 2. Build Filter URLs Dynamically

```javascript
const filters = {
  category: "Appetizers",
  is_veg: true,
  page: 2,
};

const queryString = new URLSearchParams(filters).toString();
const url = `http://localhost:8000/api/menu/?${queryString}`;
```

### 3. Implement Infinite Scroll

```javascript
async function loadNextPage(nextUrl) {
  if (!nextUrl) return; // No more pages

  const response = await fetch(nextUrl);
  const data = await response.json();

  appendItems(data.results);
  nextUrl = data.next;
}
```

---

## ⚙️ Configuration Reference

**File:** `config/settings.py`

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',  # filtering
        'rest_framework.filters.SearchFilter',                # searching
        'rest_framework.filters.OrderingFilter',              # ordering
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,  # Items per page
}
```

---

## 📝 Summary

✅ **Pagination:** Enabled (20 items/page)  
✅ **Filtering:** Working on all configured endpoints  
✅ **Search:** Working on menu, reservations, inquiries  
✅ **Combining:** Can combine pagination + filters + search

All features are production-ready!
