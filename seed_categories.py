import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.menu.models import Category

categories = [
  {"name": "Soup", "icon": "Soup"},
  {"name": "Salad", "icon": "Salad"},
  {"name": "Coastal Cuisine", "icon": "Fish"},
  {"name": "Malabar Cuisine", "icon": "Leaf"},
  {"name": "Andhra Aroma", "icon": "Flame"},
  {"name": "Signature Platters", "icon": "Award"},
  {"name": "Asian & Chinese", "icon": "UtensilsCrossed"},
  {"name": "Arabic & BBQ", "icon": "Beef"},
  {"name": "Tandoor Cuisine", "icon": "Flame"},
  {"name": "Shawarma & Grills", "icon": "Sandwich"},
  {"name": "Fried Rice & Noodles", "icon": "UtensilsCrossed"},
  {"name": "Indo-Arabian Gravy", "icon": "Soup"},
  {"name": "Breads", "icon": "Cookie"},
  {"name": "Rice & Biryani", "icon": "UtensilsCrossed"},
  {"name": "Mandi Mehfil", "icon": "Beef"},
  {"name": "Desserts", "icon": "IceCreamCone"},
]

for cat in categories:
    obj, created = Category.objects.get_or_create(name=cat["name"], defaults={"icon": cat["icon"]})
    if created:
        print(f"Created category: {cat['name']}")
    else:
        print(f"Category exists: {cat['name']}")
