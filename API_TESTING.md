# Backend API Testing Guide

## Authentication Endpoints

### 1. Login (Get JWT Token)

```bash
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJ...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJ..."
}
```

### 2. Get Current User

```bash
GET http://localhost:8000/api/auth/me/
Authorization: Bearer <access_token>
```

## Branch Management

### List All Branches (Public)

```bash
GET http://localhost:8000/api/branches/
```

### Create Branch (Admin Only)

```bash
POST http://localhost:8000/api/branches/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Devanahalli",
  "address": "Tippu Circle highway, Devanahalli, Karnataka 562110",
  "phone": "+91 099723 77369",
  "hours": "11:00 AM - 11:00 PM",
  "latitude": "13.242082",
  "longitude": "77.704114",
  "has_floor_plan": true,
  "status": "active"
}
```

## Table Management

### Check Table Availability

```bash
GET http://localhost:8000/api/tables/availability/?branch=1&date=2026-01-30&time=19:00&guests=4
```

### Create Table

```bash
POST http://localhost:8000/api/tables/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "table_id": "T1",
  "name": "Table 1",
  "seats": 4,
  "status": "active",
  "location": "Main Hall",
  "branch": 1,
  "x_position": "40.00",
  "y_position": "14.00"
}
```

## Reservation Management

### Create Reservation (Public)

```bash
POST http://localhost:8000/api/reservations/
Content-Type: application/json

{
  "branch": 1,
  "table": 1,
  "customer_name": "John Doe",
  "phone": "+91 9876543210",
  "email": "john@example.com",
  "date": "2026-01-30",
  "time": "19:00:00",
  "guests": 4,
  "special_requests": "Window seat preferred"
}

Response:
{
  "id": 1,
  "confirmation_id": "CI8A3F2B1D",
  "customer_name": "John Doe",
  "status": "pending",
  ...
}
```

### Confirm Reservation (Admin)

```bash
PATCH http://localhost:8000/api/reservations/1/confirm/
Authorization: Bearer <access_token>
```

### Look Up by Confirmation ID

```bash
GET http://localhost:8000/api/reservations/by_confirmation/?confirmation_id=CI8A3F2B1D
```

## Menu Management

### List Menu Items (Public)

```bash
GET http://localhost:8000/api/menu/
GET http://localhost:8000/api/menu/?category=Signature Mandi
GET http://localhost:8000/api/menu/?is_veg=true
```

### Create Menu Item (Admin)

```bash
POST http://localhost:8000/api/menu/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

name: Royal Mandi
description: Aromatic rice with tender meat
category: Signature Mandi
price: ₹899
is_veg: false
is_spicy: true
status: in_stock
image: <file>
```

## Deals & Offers

### Validate Promo Code (Public)

```bash
POST http://localhost:8000/api/deals/validate/
Content-Type: application/json

{
  "code": "FAMILY15"
}

Response:
{
  "valid": true,
  "deal": {
    "id": 1,
    "title": "Family Feast",
    "discount": "15% OFF",
    ...
  }
}
```

## Inquiries

### Submit Inquiry (Public)

```bash
POST http://localhost:8000/api/inquiries/
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "subject": "Private Event Inquiry",
  "message": "I would like to book for a birthday party..."
}
```

### Update Inquiry Status (Admin)

```bash
PATCH http://localhost:8000/api/inquiries/1/update_status/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "read"
}
```

## Gallery

### List Gallery Images (Public)

```bash
GET http://localhost:8000/api/gallery/
GET http://localhost:8000/api/gallery/?category=culinary
```

### Upload Image (Admin)

```bash
POST http://localhost:8000/api/gallery/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

category: culinary
caption: Our signature dish
image: <file>
```

## Testing with Postman/Thunder Client

1. Create a new request collection
2. Set base URL: `http://localhost:8000/api`
3. For authenticated requests:
   - First call `/auth/login/` to get token
   - Add header: `Authorization: Bearer <access_token>`
4. For file uploads:
   - Use `multipart/form-data`
   - Add files in the "Body" tab

## Common Response Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Need to login
- `403 Forbidden` - No permission
- `404 Not Found` - Resource doesn't exist
- `500 Server Error` - Backend error

## Frontend Integration Example

```javascript
// Example: Create Reservation from your React frontend
const createReservation = async (bookingData) => {
  const response = await fetch("http://localhost:8000/api/reservations/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(bookingData),
  });

  const data = await response.json();
  return data; // Contains confirmation_id
};
```
