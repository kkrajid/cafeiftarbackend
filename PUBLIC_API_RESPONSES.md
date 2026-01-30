# Public API Response Data Structures

## 1. GET /api/branches/

```json
{
  "count": 9,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "name": "API Test Branch",
      "address": "123 API Test St",
      "phone": "+1234567890",
      "email": null,
      "maps_url": null,
      "status": "active",
      "hours": "10 AM - 10 PM",
      "opening_time": "11:00:00",
      "closing_time": "22:00:00",
      "slot_duration": 30,
      "default_reservation_duration": 90,
      "seating_capacity": null,
      "image": null,
      "created_at": "2026-01-27 05:57:49",
      "updated_at": "2026-01-27 05:57:53"
    }
  ]
}
```

## 2. GET /api/branches/{id}/

```json
{
  "id": 2,
  "name": "API Test Branch",
  "address": "123 API Test St",
  "phone": "+1234567890",
  "status": "active",
  "hours": "10 AM - 10 PM",
  "opening_time": "11:00:00",
  "closing_time": "22:00:00",
  "slot_duration": 30,
  "default_reservation_duration": 90
}
```

## 3. GET /api/branches/{id}/hours/

```json
{
  "branch_id": 2,
  "branch_name": "API Test Branch",
  "default_opening": "11:00",
  "default_closing": "22:00",
  "weekly_schedule": [],
  "special_dates": [],
  "is_open_today": true,
  "today_hours": {
    "is_open": true,
    "opening_time": "11:00",
    "closing_time": "22:00"
  }
}
```

## 4. GET /api/branches/{id}/hours/{date}/

```json
{
  "branch_id": 2,
  "branch_name": "API Test Branch",
  "date": "2026-01-31",
  "day_name": "Friday",
  "is_open": true,
  "opening_time": "11:00",
  "closing_time": "22:00",
  "is_special_date": false,
  "special_note": null
}
```

## 5. GET /api/tables/

```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "branch": 2,
      "table_id": "T1",
      "name": "Table 1",
      "seats": 4,
      "status": "active",
      "location": "Main Hall"
    }
  ]
}
```

## 6. GET /api/tables/availability/

Query: `?branch=2&date=2026-01-31&time=19:00&guests=4`

```json
{
  "available": true,
  "tables": [
    {
      "id": 1,
      "table_id": "T1",
      "name": "Table 1",
      "seats": 4
    }
  ],
  "total_available": 1,
  "requested_time": "19:00",
  "reservation_duration_minutes": 90
}
```

## 7. GET /api/tables/available_slots/

Query: `?branch=2&date=2026-01-31&guests=4`

```json
{
  "date": "2026-01-31",
  "branch_id": 2,
  "guests": 4,
  "slots": {
    "lunch": [
      { "time": "12:00", "display": "12:00 PM", "available_tables": 1 },
      { "time": "12:30", "display": "12:30 PM", "available_tables": 1 }
    ],
    "dinner": [
      { "time": "19:00", "display": "7:00 PM", "available_tables": 1 },
      { "time": "19:30", "display": "7:30 PM", "available_tables": 1 }
    ]
  }
}
```

## 8. GET /api/menu/

```json
{
  "count": 5,
  "results": [
    {
      "id": 8,
      "name": "Chicken Biryani",
      "description": "Aromatic rice with tender chicken",
      "category_text": "Main Course",
      "category_details": {
        "id": 5,
        "name": "Main Course",
        "icon": "ChefHat",
        "slug": "main-course"
      },
      "price": "349.00",
      "currency": "INR",
      "image": "http://127.0.0.1:8000/media/menu/image.jpg",
      "is_veg": false,
      "is_spicy": true,
      "status": "in_stock",
      "is_featured": true,
      "featured_order": 1
    }
  ]
}
```

## 9. GET /api/menu/featured/

```json
{
  "count": 3,
  "results": [
    {
      "id": 8,
      "name": "Chicken Biryani",
      "price": "349.00",
      "is_featured": true,
      "featured_order": 1
    }
  ]
}
```

## 10. GET /api/menu/categories/

```json
{
  "count": 16,
  "results": [
    {
      "id": 1,
      "name": "Soup",
      "description": "",
      "icon": "Soup",
      "slug": "soup",
      "created_at": "2026-01-27 18:31:26"
    }
  ]
}
```

## 11. GET /api/deals/

```json
{
  "count": 4,
  "results": [
    {
      "id": 6,
      "title": "Weekend Special",
      "description": "20% off on all main courses",
      "code": "WEEKEND20",
      "discount_type": "percentage",
      "discount_value": "20.00",
      "valid_from": "2026-01-28",
      "valid_until": "2026-02-26",
      "image": null,
      "tag": "Special",
      "status": "active"
    }
  ]
}
```

## 12. GET /api/gallery/

```json
{
  "count": 0,
  "results": []
}
```

## 13. GET /api/reservations/my_reservations/

Query: `?email=customer@example.com`

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "confirmation_id": "RES-ABC123",
      "branch": 2,
      "branch_name": "API Test Branch",
      "date": "2026-01-31",
      "time": "19:00:00",
      "guests": 4,
      "status": "confirmed",
      "customer_name": "John Doe",
      "customer_email": "customer@example.com",
      "customer_phone": "+1234567890"
    }
  ]
}
```

## 14. POST /api/reservations/

Request:

```json
{
  "branch": 2,
  "table": 1,
  "date": "2026-01-31",
  "time": "19:00",
  "guests": 4,
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "notes": "Window seat preferred"
}
```

Response:

```json
{
  "id": 1,
  "confirmation_id": "RES-XYZ789",
  "status": "pending",
  "message": "Reservation created successfully"
}
```

## 15. POST /api/inquiries/

Request:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "subject": "Catering Inquiry",
  "message": "I would like to inquire about catering services..."
}
```

Response:

```json
{
  "id": 1,
  "status": "new",
  "message": "Inquiry submitted successfully"
}
```

## 16. POST /api/auth/login/

Request:

```json
{
  "email": "admin@cafeiftar.com",
  "password": "Admin@123"
}
```

Response:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "admin@cafeiftar.com",
    "username": "superadmin",
    "first_name": "Super",
    "last_name": "Admin",
    "role": "admin"
  }
}
```
