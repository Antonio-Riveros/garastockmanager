from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
import pandas as pd
from .models import Item, Category
from .forms import ItemForm, ImportForm

class ItemListView(ListView):
    model = Item
    template_name = 'stock/item_list.html'
    context_object_name = 'items'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | 
                Q(code__icontains=q) |
                Q(description__icontains=q)
            )
        return queryset

class ItemDetailView(DetailView):
    model = Item
    template_name = 'stock/item_detail.html'
    slug_field = 'code'
    slug_url_kwarg = 'code'

class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'stock/item_form.html'
    success_url = reverse_lazy('item_list')

    def form_valid(self, form):
        item = form.save(commit=False)
        
        # Check if "Nueva Categoría" is selected (Code='NUE')
        if item.category.code == 'NUE':
            new_cat_name = form.cleaned_data.get('new_category_name')
            if new_cat_name:
                # 1. Check if it already exists by name
                existing_cat = Category.objects.filter(name__iexact=new_cat_name).first()
                if existing_cat:
                    item.category = existing_cat
                else:
                    # 2. Create new category
                    # Generate code from name (first 3 chars, upper)
                    code_candidate = new_cat_name[:3].upper()
                    # Ensure unique
                    count = 1
                    orig_code = code_candidate
                    while Category.objects.filter(code=code_candidate).exists():
                         code_candidate = f"{orig_code[:2]}{count}"
                         count += 1
                         if count > 9: break 
                    
                    new_category = Category.objects.create(name=new_cat_name, code=code_candidate)
                    item.category = new_category
                    messages.info(self.request, f"Nueva categoría '{new_cat_name}' creada.")
            else:
                # If no name provided, revert error
                form.add_error('new_category_name', "Debe ingresar un nombre para la nueva categoría.")
                return self.form_invalid(form)
        
        item.save()
        messages.success(self.request, "Elemento creado correctamente.")
        return redirect(self.success_url)

class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'stock/item_form.html'
    slug_field = 'code'
    slug_url_kwarg = 'code'
    
    def get_success_url(self):
        return reverse('item_detail', kwargs={'code': self.object.code})

    def form_valid(self, form):
        # Handle new category logic for update as well
        item = form.save(commit=False)
        if item.category.code == 'NUE':
            new_cat_name = form.cleaned_data.get('new_category_name')
            if new_cat_name:
                existing_cat = Category.objects.filter(name__iexact=new_cat_name).first()
                if existing_cat:
                    item.category = existing_cat
                else:
                    code_candidate = new_cat_name[:3].upper()
                    count = 1
                    orig_code = code_candidate
                    while Category.objects.filter(code=code_candidate).exists():
                         code_candidate = f"{orig_code[:2]}{count}"
                         count += 1
                         if count > 9: break 
                    new_category = Category.objects.create(name=new_cat_name, code=code_candidate)
                    item.category = new_category
                    messages.info(self.request, f"Nueva categoría '{new_cat_name}' creada.")
            else:
                form.add_error('new_category_name', "Debe ingresar un nombre para la nueva categoría.")
                return self.form_invalid(form)
        
        messages.success(self.request, "Elemento actualizado correctamente.")
        return super().form_valid(form)

class ScannerView(TemplateView):
    template_name = 'stock/scan.html'

def set_language(request, lang_code):
    from django.conf import settings
    from django.utils import translation
    
    if lang_code in [l[0] for l in settings.LANGUAGES]:
        translation.activate(lang_code)
        request.session['_language'] = lang_code
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

class BulkImportView(FormView):
    template_name = 'stock/import.html'
    form_class = ImportForm
    success_url = reverse_lazy('item_list')

    def form_valid(self, form):
        excel_file = form.cleaned_data['excel_file']
        try:
            df = pd.read_excel(excel_file)
            
            # Expected columns: Elemento, Categoría, Estado, Cantidad, Descripción
            required_cols = ['Elemento', 'Categoría', 'Estado', 'Cantidad', 'Descripción']
            if not all(col in df.columns for col in required_cols):
                messages.error(self.request, f"El archivo debe contener las columnas: {', '.join(required_cols)}")
                return self.form_invalid(form)

            with transaction.atomic():
                for index, row in df.iterrows():
                    # Get or Create Category (by name, assume code needs to be derived or exists)
                    # Issue: Category needs a code. If category strictly matches existing ones, we are fine.
                    # Or we create new ones. For MVP, let's assume valid categories exist or we auto-generate a code?
                    # Generating a code for a category is tricky without user input (2-3 chars).
                    # Let's take the first 3 chars of name as code if creating new.
                    
                    cat_name = str(row['Categoría']).strip()
                    category = Category.objects.filter(name__iexact=cat_name).first()
                    if not category:
                        # Auto-create category
                        code_candidate = cat_name[:3].upper()
                        # Ensure uniqueness of code
                        if Category.objects.filter(code=code_candidate).exists():
                            # If collision, try adding a number or something.
                            # For MVP simplicity, just fail if exact category doesn't exist?
                            # Requirement says "Validar datos".
                            # Let's try to be smart: use existing category if name matches closely, else create.
                            count = 1
                            original_code = code_candidate
                            while Category.objects.filter(code=code_candidate).exists():
                                code_candidate = f"{original_code[:2]}{count}"
                                count += 1
                                if count > 9: break # fallback
                        
                        category = Category.objects.create(name=cat_name, code=code_candidate)

                    # Status map
                    status_map = {
                        'Funcional': 'FUNCIONAL',
                        'Averiado': 'AVERIADO',
                        'Obsoleto': 'OBSOLETO',
                        'Venta': 'VENTA',
                        'Descarte': 'DESCARTE'
                    }
                    status_raw = str(row['Estado']).capitalize()
                    status = status_map.get(status_raw, 'FUNCIONAL')

                    Item.objects.create(
                        name=row['Elemento'],
                        category=category,
                        status=status,
                        quantity=int(row['Cantidad']),
                        description=str(row['Descripción']) if pd.notna(row['Descripción']) else ""
                    )
            
            messages.success(self.request, f"Se importaron {len(df)} elementos exitosamente.")
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Error al importar: {str(e)}")
            return self.form_invalid(form)
