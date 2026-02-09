from django import template

register = template.Library()

TRANSLATIONS = {
    'es': {
        'Inventory': 'Inventario',
        'New': '+ Nuevo',
        'Import': 'Importar',
        'Scan': '📷 Escanear',
        'Edit': '✏️ Editar',
        'Back': 'Volver',
        'Save': 'Guardar',
        'Search': 'Buscar...',
        'No items found': 'No se encontraron elementos.',
        'Name': 'Nombre',
        'Code': 'Código',
        'Category': 'Categoría',
        'Status': 'Estado',
        'Quantity': 'Cantidad',
        'Description': 'Descripción',
        'Created At': 'Fecha Alta',
        'Actions': 'Acciones',
        'View': 'Ver',
        'Download QR': 'Descargar QR',
        'New Item': 'Nuevo Elemento',
        'Edit Item': 'Editar Elemento',
        'Import Items': 'Importar Elementos',
        'Upload Excel': 'Subir Excel',
        'Upload': 'Subir',
        'Scan QR Code': 'Escanear Código QR',
        'Detected Code': 'Código detectado',
        'GARA Stock': 'GARA Stock',
        'Language': 'Idioma',
        'Dark Mode': 'Modo Oscuro',
        'QR Code': 'Código QR',
        'Search placeholder': 'Buscar...',
    },
    'en': {
        'Inventory': 'Inventory',
        'New': '+ New',
        'Import': 'Import',
        'Scan': '📷 Scan',
        'Edit': '✏️ Edit',
        'Back': 'Back',
        'Save': 'Save',
        'Search': 'Search...',
        'No items found': 'No items found.',
        'Name': 'Name',
        'Code': 'Code',
        'Category': 'Category',
        'Status': 'Status',
        'Quantity': 'Quantity',
        'Description': 'Description',
        'Created At': 'Created At',
        'Actions': 'Actions',
        'View': 'View',
        'Download QR': 'Download QR',
        'New Item': 'New Item',
        'Edit Item': 'Edit Item',
        'Import Items': 'Import Items',
        'Upload Excel': 'Upload Excel',
        'Upload': 'Upload',
        'Scan QR Code': 'Scan QR Code',
        'Detected Code': 'Detected Code',
        'GARA Stock': 'GARA Stock',
        'Language': 'Language',
        'Dark Mode': 'Dark Mode',
        'QR Code': 'QR Code',
        'Search placeholder': 'Search...',
    }
}

@register.filter
def translate(text, lang_code='es'):
    # Default to 'es' if lang_code is not provided or not found
    if not lang_code:
        lang_code = 'es'
    # Handle 'es-ar' etc by taking first 2 chars
    lang_code = lang_code[:2]
    
    return TRANSLATIONS.get(lang_code, TRANSLATIONS['es']).get(text, text)
