# GARA Stock Manager

MVP de control de stock simple e intuitivo, orientado a uso móvil (Mobile First).

## Funcionalidades

- **Gestión de Stock**: Alta, baja y modificación de elementos con categorización y estado.
- **Códigos Únicos**: Generación automática de códigos tipo `XXX-12345678901` no secuenciales.
- **Códigos QR**: Generación automática de QR para cada elemento, escaneable desde celulares.
- **Importación Masiva**: Carga de inventario desde archivos Excel (.xlsx).
- **Diseño Móvil**: Interfaz optimizada para pantallas pequeñas.

## Requisitos Previos

- Python 3.8+
- pip

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/mirendarodrigo/garastockmanager.git
   cd garastockmanager
   ```

2. Crear un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Aplicar migraciones:
   ```bash
   python manage.py migrate
   ```

5. Crear un superusuario (para acceder al admin):
   ```bash
   python manage.py createsuperuser
   ```

## Ejecución

Para ejecutar el servidor de desarrollo:

```bash
python manage.py runserver 0.0.0.0:8000
```
- Acceder desde el navegador en `http://localhost:8000` (o la IP de su red para probar desde el celular).
- Para acceder desde el celular, asegúrese de que el teléfono esté en la misma red Wi-Fi y use la IP de su PC (ej: `http://192.168.1.X:8000`).

## Formato Excel para Importación

El archivo Excel debe tener las siguientes columnas exactas en la primera fila:

| Elemento | Categoría | Estado | Cantidad | Descripción |
|----------|-----------|--------|----------|-------------|
| Taladro  | Herramientas | Funcional | 5 | Taladro percutor |
| Laptop   | IT | Averiado | 1 | Pantalla rota |

- **Categoría**: Si la categoría no existe, se creará automáticamente intentando generar un código de 3 letras.
- **Estado**: Funcional, Averiado, Obsoleto, Venta, Descarte.

## Estructura del Proyecto

```
gara_stock/
│
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
├── gara_stock/       # Configuración del proyecto
├── stock/            # Aplicación principal
│   ├── models.py     # Definición de datos (Item, Category)
│   ├── views.py      # Lógica de vistas e importación
│   ├── forms.py      # Formularios
│   ├── utils.py      # Generadores de códigos y QR
│   ├── admin.py      # Configuración del panel de administración
│   └── tests.py      # Tests unitarios
├── templates/        # Plantillas HTML (base, listas, detalles)
└── static/           # Archivos CSS e imágenes estáticas
```

## Próximos pasos

- Implementar autenticación de usuarios.
- Mejorar la detección de IP para la URL del QR en entornos de producción.
- Despliegue en servidor.
