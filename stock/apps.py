from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_nue_category(sender, **kwargs):
    from .models import Category
    if not Category.objects.filter(code='NUE').exists():
        Category.objects.create(name='Nueva Categoría', code='NUE')

class StockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stock'
    def ready(self):
        post_migrate.connect(create_nue_category, sender=self)