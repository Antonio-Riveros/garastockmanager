from django.test import TestCase, override_settings
from .models import Item, Category
from django.core.files.uploadedfile import SimpleUploadedFile
from .views import BulkImportView
from django.urls import reverse
import pandas as pd
from io import BytesIO
import shutil
import tempfile

MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ItemModelTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.category = Category.objects.create(name="IT Equipment", code="IT")

    def test_item_creation_generates_code(self):
        item = Item.objects.create(name="Laptop", category=self.category, quantity=10)
        self.assertTrue(item.code.startswith("IT-"))
        self.assertEqual(len(item.code), 14) # IT- + 11 digits

    def test_qr_code_generated(self):
        item = Item.objects.create(name="Mouse", category=self.category, quantity=5)
        self.assertTrue(item.qr_code)
        self.assertTrue(item.qr_code.name.startswith("qrcodes/qr_"))

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ImportTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.category = Category.objects.create(name="Tools", code="TOL")
    
    def test_bulk_import_logic(self):
        # Create a sample excel file in memory
        df = pd.DataFrame({
            'Elemento': ['Hammer', 'Drill'],
            'Categoría': ['Tools', 'Tools'],
            'Estado': ['Funcional', 'Averiado'],
            'Cantidad': [10, 2],
            'Descripción': ['Heavy duty', 'Cordless']
        })
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        
        file = SimpleUploadedFile("test_import.xlsx", output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Simulating a POST request to the import view
        response = self.client.post('/import/', {'excel_file': file})
        
        # Check if items were created
        self.assertEqual(Item.objects.count(), 2)
        hammer = Item.objects.get(name="Hammer")
        self.assertEqual(hammer.category.name, "Tools")
        self.assertEqual(hammer.quantity, 10)
        self.assertEqual(hammer.status, 'FUNCIONAL')

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ViewTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.new_cat_placeholder = Category.objects.create(name="Nueva Categoría", code="NUE")

    def test_create_item_with_new_category(self):
        # Post data to create item with "Nueva Categoría" selected and a new name provided
        response = self.client.post(reverse('item_add'), {
            'name': 'New Thing',
            'category': self.new_cat_placeholder.id,
            'new_category_name': 'My New Cat',
            'status': 'FUNCIONAL',
            'quantity': 1,
            'description': 'Test'
        })
        
        # Check redirection (success)
        self.assertEqual(response.status_code, 302)
        
        # Verify item created
        item = Item.objects.get(name='New Thing')
        self.assertEqual(item.category.name, 'My New Cat')
        self.assertTrue(item.category.code.startswith('MY')) # Helper generates code from name
