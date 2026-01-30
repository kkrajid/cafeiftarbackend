# Cafe Iftar Backend API Documentation

## Authentication

All admin endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Login (Email-based)

```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "admin@cafeiftar.com",
  "password": "Admin@123"
}
```

**Response:**

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

---

## Public Endpoints (No Auth Required)

### Branches

| Method | Endpoint                           | Description                              |
| ------ | ---------------------------------- | ---------------------------------------- |
| GET    | `/api/branches/`                   | List all branches                        |
| GET    | `/api/branches/{id}/`              | Get branch details                       |
| GET    | `/api/branches/{id}/hours/`        | Get weekly schedule + special dates      |
| GET    | `/api/branches/{id}/hours/{date}/` | Get hours for specific date (YYYY-MM-DD) |

### Tables

| Method | Endpoint                       | Description                   |
| ------ | ------------------------------ | ----------------------------- |
| GET    | `/api/tables/`                 | List all tables               |
| GET    | `/api/tables/availability/`    | Check table availability      |
| GET    | `/api/tables/available_slots/` | Get time slots by meal period |

**Query params for availability:**

- `branch` (required): Branch ID
- `date` (required): Date in YYYY-MM-DD
- `time` (required for availability): Time in HH:MM
- `guests` (required): Number of guests

### Menu

| Method | Endpoint                | Description                  |
| ------ | ----------------------- | ---------------------------- |
| GET    | `/api/menu/`            | List all menu items          |
| GET    | `/api/menu/featured/`   | Featured dishes for homepage |
| GET    | `/api/menu/categories/` | List categories              |

### Reservations (Public)

| Method | Endpoint                                                 | Description          |
| ------ | -------------------------------------------------------- | -------------------- |
| POST   | `/api/reservations/`                                     | Create a reservation |
| GET    | `/api/reservations/my_reservations/?email=...`           | Customer's bookings  |
| GET    | `/api/reservations/by_confirmation/?confirmation_id=...` | Lookup by ID         |

### Other Public

| Method | Endpoint          | Description         |
| ------ | ----------------- | ------------------- |
| GET    | `/api/deals/`     | List active deals   |
| GET    | `/api/gallery/`   | Gallery images      |
| POST   | `/api/inquiries/` | Submit contact form |

---

## Admin Endpoints (Auth Required)

### Auth

| Method | Endpoint                     | Description              |
| ------ | ---------------------------- | ------------------------ |
| GET    | `/api/auth/me/`              | Get current user         |
| PATCH  | `/api/auth/me/`              | Update profile           |
| POST   | `/api/auth/password-change/` | Change password          |
| POST   | `/api/auth/logout/`          | Logout (blacklist token) |
| POST   | `/api/auth/token/refresh/`   | Refresh access token     |

### Branches (Admin)

| Method | Endpoint              | Description   |
| ------ | --------------------- | ------------- |
| POST   | `/api/branches/`      | Create branch |
| PATCH  | `/api/branches/{id}/` | Update branch |
| DELETE | `/api/branches/{id}/` | Delete branch |

### Operating Hours (Admin)

| Method | Endpoint                              | Description         |
| ------ | ------------------------------------- | ------------------- |
| GET    | `/api/branches/operating-hours/`      | List all            |
| POST   | `/api/branches/operating-hours/`      | Create weekly hours |
| PATCH  | `/api/branches/operating-hours/{id}/` | Update              |
| DELETE | `/api/branches/operating-hours/{id}/` | Delete              |

### Special Dates (Admin)

| Method | Endpoint                            | Description          |
| ------ | ----------------------------------- | -------------------- |
| GET    | `/api/branches/special-dates/`      | List all             |
| POST   | `/api/branches/special-dates/`      | Create holiday/event |
| PATCH  | `/api/branches/special-dates/{id}/` | Update               |
| DELETE | `/api/branches/special-dates/{id}/` | Delete               |

### Tables (Admin)

| Method | Endpoint            | Description  |
| ------ | ------------------- | ------------ |
| POST   | `/api/tables/`      | Create table |
| PATCH  | `/api/tables/{id}/` | Update table |
| DELETE | `/api/tables/{id}/` | Delete table |

### Menu (Admin)

| Method | Endpoint                          | Description            |
| ------ | --------------------------------- | ---------------------- |
| POST   | `/api/menu/`                      | Create menu item       |
| PATCH  | `/api/menu/{id}/`                 | Update menu item       |
| DELETE | `/api/menu/{id}/`                 | Delete menu item       |
| PATCH  | `/api/menu/{id}/toggle_featured/` | Toggle featured status |
| POST   | `/api/menu/categories/`           | Create category        |
| DELETE | `/api/menu/categories/{slug}/`    | Delete category        |

### Reservations (Admin)

| Method | Endpoint                              | Description           |
| ------ | ------------------------------------- | --------------------- |
| GET    | `/api/reservations/`                  | List all reservations |
| GET    | `/api/reservations/stats/`            | Dashboard statistics  |
| GET    | `/api/reservations/today/?branch=...` | Today's bookings      |
| PATCH  | `/api/reservations/{id}/confirm/`     | Confirm booking       |
| PATCH  | `/api/reservations/{id}/cancel/`      | Cancel booking        |
| PATCH  | `/api/reservations/{id}/complete/`    | Mark completed        |
| PATCH  | `/api/reservations/{id}/noshow/`      | Mark no-show          |

### Deals (Admin)

| Method | Endpoint           | Description |
| ------ | ------------------ | ----------- |
| POST   | `/api/deals/`      | Create deal |
| PATCH  | `/api/deals/{id}/` | Update deal |
| DELETE | `/api/deals/{id}/` | Delete deal |

### Inquiries (Admin)

| Method | Endpoint                             | Description        |
| ------ | ------------------------------------ | ------------------ |
| GET    | `/api/inquiries/`                    | List all inquiries |
| PATCH  | `/api/inquiries/{id}/update_status/` | Update status      |

### Gallery (Admin)

| Method | Endpoint             | Description  |
| ------ | -------------------- | ------------ |
| POST   | `/api/gallery/`      | Upload image |
| DELETE | `/api/gallery/{id}/` | Delete image |

---

## Test Results Summary

| Category         | Tests     | Status      |
| ---------------- | --------- | ----------- |
| Public Endpoints | 18/18     | ✅ 100%     |
| Admin Endpoints  | 35/35     | ✅ 100%     |
| **Total**        | **53/53** | **✅ 100%** |

---

## Default Admin Account

```
Email: admin@cafeiftar.com
Password: Admin@123
```
