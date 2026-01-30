# Cafe Iftar Backend API

Complete Django REST Framework backend for the Cafe Iftar management system.

## Setup

1. **Install PostgreSQL** and create database:

```sql
CREATE DATABASE cafe_iftar_db;
```

2. **Install dependencies**:

```bash
.\venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**:

- Copy `.env.example` to `.env`
- Update database credentials in `.env`

4. **Run migrations**:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**:

```bash
python manage.py createsuperuser
```

6. **Run server**:

```bash
python manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/token/refresh/` - Refresh token
- `POST /api/auth/register/` - Register new user
- `GET /api/auth/me/` - Get current user
- `POST /api/auth/logout/` - Logout

### Branches

- `GET /api/branches/` - List all branches
- `POST /api/branches/` - Create branch (admin)
- `GET /api/branches/{id}/` - Get branch details
- `PUT /api/branches/{id}/` - Update branch (admin)
- `DELETE /api/branches/{id}/` - Delete branch (admin)

### Tables

- `GET /api/tables/?branch={id}` - List tables by branch
- `GET /api/tables/availability/?branch={id}&date={date}&time={time}&guests={num}` - Check availability
- `POST /api/tables/` - Create table (admin)
- `PUT /api/tables/{id}/` - Update table (admin)
- `DELETE /api/tables/{id}/` - Delete table (admin)

### Reservations

- `POST /api/reservations/` - Create reservation (public)
- `GET /api/reservations/` - List reservations (admin)
- `GET /api/reservations/by_confirmation/?confirmation_id={id}` - Lookup by ID
- `PATCH /api/reservations/{id}/confirm/` - Confirm (admin)
- `PATCH /api/reservations/{id}/cancel/` - Cancel (admin)

### Menu

- `GET /api/menu/?category={cat}` - List menu items
- `POST /api/menu/` - Create item (admin)
- `PUT /api/menu/{id}/` - Update item (admin)
- `DELETE /api/menu/{id}/` - Delete item (admin)

### Deals

- `GET /api/deals/` - List active deals
- `POST /api/deals/validate/` - Validate promo code
- `POST /api/deals/` - Create deal (admin)
- `PUT /api/deals/{id}/` - Update deal (admin)
- `DELETE /api/deals/{id}/` - Delete deal (admin)

### Inquiries

- `POST /api/inquiries/` - Submit inquiry (public)
- `GET /api/inquiries/` - List inquiries (admin)
- `PATCH /api/inquiries/{id}/update_status/` - Update status (admin)

### Gallery

- `GET /api/gallery/?category={cat}` - List gallery images
- `POST /api/gallery/` - Upload image (admin)
- `DELETE /api/gallery/{id}/` - Delete image (admin)

## Features

- ✅ JWT Authentication
- ✅ Role-based permissions (Admin, Branch Manager, Staff)
- ✅ PostgreSQL database
- ✅ Email notifications for reservations
- ✅ Image upload support
- ✅ CORS enabled for frontend
- ✅ Filtering and search
- ✅ Admin panel at `/admin/`

## Tech Stack

- Django 6.0
- Django REST Framework
- PostgreSQL
- JWT Authentication
- SMTP Email
