import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gara_stock.settings')
django.setup()

from stock.models import Category

categories = [
    {'name': 'Herramientas', 'code': 'HER'},
    {'name': 'Partes de Motor', 'code': 'MOT'},
    {'name': 'Partes de Botes', 'code': 'BOT'},
    {'name': 'Pintura y Acabados', 'code': 'PIN'},
    {'name': 'Seguridad', 'code': 'SEG'},
    {'name': 'Electrónica', 'code': 'ELE'},
    {'name': 'Otros', 'code': 'OTR'},
    {'name': 'Nueva Categoría', 'code': 'NUE'},
]

for cat_data in categories:
    cat, created = Category.objects.get_or_create(
        code=cat_data['code'],
        defaults={'name': cat_data['name']}
    )
    if created:
        print(f"Created: {cat.name} ({cat.code})")
    else:
        print(f"Exists: {cat.name} ({cat.code})")
        # Update name just in case
        if cat.name != cat_data['name']:
            cat.name = cat_data['name']
            cat.save()
            print(f"Updated name: {cat.name}")

print("Done.")
