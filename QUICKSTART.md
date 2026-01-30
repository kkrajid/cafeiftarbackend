# Quick Start Guide - Cafe Iftar Backend

## Prerequisites

1. **Install PostgreSQL** (if not already installed)
   - Download from: https://www.postgresql.org/download/windows/
   - During installation, remember the password you set for `postgres` user
   - Default port: 5432

## Database Setup

1. **Create Database**:

   ```bash
   # Open Command Prompt or PowerShell
   psql -U postgres
   # Enter your postgres password when prompted

   # Then create the database:
   CREATE DATABASE cafe_iftar_db;
   \q
   ```

   **OR use pgAdmin** (GUI):
   - Open pgAdmin
   - Right-click on "Databases" → "Create" → "Database"
   - Name: `cafe_iftar_db`
   - Click "Save"

2. **Update `.env` file**:
   Open `backend\.env` and update:
   ```
   DATABASE_PASSWORD=your_actual_postgres_password
   ```

## Running the Backend

1. **Open terminal in backend folder**:

   ```bash
   cd "D:\CAFEIFTART NEW\backend"
   ```

2. **Activate virtual environment**:

   ```bash
   .\venv\Scripts\activate
   ```

3. **Create migrations** (if not done):

   ```bash
   python manage.py makemigrations
   ```

4. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Create admin user**:

   ```bash
   python manage.py createsuperuser
   ```

   - Enter username (e.g., `admin`)
   - Enter email
   - Enter password (remember this!)

6. **Run the server**:

   ```bash
   python manage.py runserver
   ```

7. **Test it!**:
   - Backend API: http://localhost:8000/api/
   - Admin panel: http://localhost:8000/admin/
   - Login with the superuser credentials you created

## Quick Test

Once server is running, test the API:

```bash
# Get all branches (should be empty initially)
curl http://localhost:8000/api/branches/

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"your_password\"}"
```

## Next Steps

1. Use the Django admin panel to add initial data (branches, tables)
2. Connect your frontend to `http://localhost:8000/api/`
3. Replace all `localStorage` calls in frontend with API calls

## Troubleshooting

### "password authentication failed"

- Check your PostgreSQL password in `.env`
- Make sure PostgreSQL is running

### "database does not exist"

- Run the CREATE DATABASE command again
- Check database name in `.env` matches `cafe_iftar_db`

### Port 8000 already in use

- Kill the existing process or use different port:
  ```bash
  python manage.py runserver 8001
  ```
