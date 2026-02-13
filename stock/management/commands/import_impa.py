import json
from django.core.management.base import BaseCommand
from stock.models import StandardItem

class Command(BaseCommand):
    help = 'Importa códigos IMPA desde un archivo JSON'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Ruta al archivo JSON')

    def handle(self, *args, **options):
        filepath = options['json_file']
        items = []

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()

            if not content:
                self.stderr.write(self.style.ERROR('El archivo está vacío'))
                return

            # 1. Array JSON (lista)
            if content.startswith('['):
                data = json.loads(content)
                if isinstance(data, list):
                    items = data
                else:
                    self.stderr.write(self.style.ERROR('El archivo no contiene un array en la raíz'))
                    return

            # 2. Objeto JSON (diccionario)
            elif content.startswith('{'):
                data = json.loads(content)
                if isinstance(data, dict):
                    # Buscar la primera clave que contenga una lista
                    found = False
                    for key, value in data.items():
                        if isinstance(value, list):
                            items = value
                            found = True
                            self.stdout.write(self.style.WARNING(
                                f'Usando la lista bajo la clave "{key}"'
                            ))
                            break
                    if not found:
                        self.stderr.write(self.style.ERROR(
                            'No se encontró ninguna lista dentro del objeto JSON'
                        ))
                        return
                else:
                    self.stderr.write(self.style.ERROR('Formato JSON no reconocido'))
                    return

            # 3. JSON Lines (cada línea es un objeto)
            else:
                # Volver al inicio del archivo y leer línea por línea
                f.seek(0)
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            items.append(obj)
                        else:
                            self.stderr.write(self.style.WARNING(
                                f'Línea {line_num}: no es un objeto, se ignora'
                            ))
                    except json.JSONDecodeError:
                        self.stderr.write(self.style.WARNING(
                            f'Línea {line_num}: JSON inválido, se ignora'
                        ))

        # Procesar los ítems
        created_count = 0
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                self.stderr.write(self.style.WARNING(f'Ítem {idx}: no es un diccionario, se ignora'))
                continue

            code = item.get('impa_code')
            if not code:
                self.stderr.write(self.style.WARNING(f'Ítem {idx}: no tiene "impa_code", se ignora'))
                continue

            obj, created = StandardItem.objects.update_or_create(
                code=str(code),
                defaults={
                    'description': item.get('description', ''),
                    'category': item.get('category', ''),
                    'sub_category': item.get('sub_category', ''),
                    'unit': item.get('unit', ''),
                    'keywords': item.get('keywords', []),
                    'notes': item.get('notes', ''),
                    'catalog': 'IMPA',
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Importación completada: {created_count} códigos nuevos, {len(items) - created_count} actualizados/saltados'
        ))