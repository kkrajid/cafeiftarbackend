# Superuser Creation Script
# Run this if you want to create an admin user programmatically

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@cafeiftar.com',
        password='admin123',
        role='admin'
    )
    print("Superuser created: username=admin, password=admin123")
else:
    print("Admin user already exists")
