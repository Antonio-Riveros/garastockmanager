from django.db import models
from django.conf import settings
from .utils import generate_unique_numeric_part, generate_qr_code
import socket

class Category(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True, help_text="Sigla de 2 o 3 letras (ej: IT, VEH)")

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name_plural = "Categories"

class Item(models.Model):
    STATUS_CHOICES = [
        ('FUNCIONAL', 'Funcional'),
        ('AVERIADO', 'Averiado'),
        ('OBSOLETO', 'Obsoleto'),
        ('VENTA', 'Apto para venta'),
        ('DESCARTE', 'Apto para descarte'),
    ]

    code = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200, verbose_name="Elemento")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='FUNCIONAL')
    quantity = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # 1. Generate Code if new
        if is_new and not self.code:
            numeric_part = generate_unique_numeric_part()
            new_code = f"{self.category.code}-{numeric_part}"
            
            # Simple collision check loop
            while Item.objects.filter(code=new_code).exists():
                numeric_part = generate_unique_numeric_part()
                new_code = f"{self.category.code}-{numeric_part}"
            
            self.code = new_code
            
        # 2. Generate QR if new or code changed (usually code doesn't change)
        if not self.qr_code:
            # Determine base URL. This is tricky for local dev.
            # Using socket to guess local IP is a decent heuristic for an MVP running locally.
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                base_url = f"http://{local_ip}:8000"
            except:
                base_url = "http://localhost:8000"
                
            # Construct URL for the item detail view
            # Note: We haven't defined the URL pattern yet but let's assume '/stock/items/<code >/'
            qr_target_url = f"{base_url}/stock/items/{self.code}/"
            
            # Use code for filename to avoid invalid characters in URL
            qr_filename = f"qr_{self.code}.png"
            self.qr_code = generate_qr_code(qr_target_url, filename=qr_filename)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"
