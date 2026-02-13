from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView,DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
import pandas as pd
from .models import Item, Category, StandardItem
from .forms import ItemForm, ImportForm

class ItemListView(ListView):
    model = Item
    template_name = 'stock/item_list.html'
    context_object_name = 'items'
    ordering = ['-created_at']
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q) | Q(description__icontains=q))
        return qs

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
                        if count > 9:
                            break
                    new_category = Category.objects.create(name=new_cat_name, code=code_candidate)
                    item.category = new_category
                    messages.info(self.request, f"Nueva categoría '{new_cat_name}' creada.")
            else:
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
                        if count > 9:
                            break
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
            required_cols = ['Elemento', 'Categoría', 'Estado', 'Cantidad', 'Descripción']
            if not all(col in df.columns for col in required_cols):
                messages.error(self.request, f"El archivo debe contener las columnas: {', '.join(required_cols)}")
                return self.form_invalid(form)
            with transaction.atomic():
                for _, row in df.iterrows():
                    cat_name = str(row['Categoría']).strip()
                    category = Category.objects.filter(name__iexact=cat_name).first()
                    if not category:
                        code_candidate = cat_name[:3].upper()
                        count = 1
                        orig_code = code_candidate
                        while Category.objects.filter(code=code_candidate).exists():
                            code_candidate = f"{orig_code[:2]}{count}"
                            count += 1
                            if count > 9:
                                break
                        category = Category.objects.create(name=cat_name, code=code_candidate)
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

class CategoryListView(ListView):
    model = Category
    template_name = 'stock/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']

class CategoryCreateView(CreateView):
    model = Category
    fields = ['name', 'code']
    template_name = 'stock/category_form.html'
    success_url = reverse_lazy('category_list')
    def form_valid(self, form):
        if not form.cleaned_data['code']:
            name = form.cleaned_data['name']
            code_candidate = name[:3].upper()
            count = 1
            orig_code = code_candidate
            while Category.objects.filter(code=code_candidate).exists():
                code_candidate = f"{orig_code[:2]}{count}"
                count += 1
                if count > 9:
                    code_candidate = orig_code + str(count)
            form.instance.code = code_candidate
        messages.success(self.request, f"Categoría '{form.instance.name}' creada correctamente.")
        return super().form_valid(form)

class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['name', 'code']
    template_name = 'stock/category_form.html'
    success_url = reverse_lazy('category_list')
    def form_valid(self, form):
        messages.success(self.request, f"Categoría '{form.instance.name}' actualizada.")
        return super().form_valid(form)

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'stock/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')
    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(request, f"Categoría '{category.name}' eliminada.")
        return super().delete(request, *args, **kwargs)

class StandardCatalogView(ListView):
    model = StandardItem
    template_name = 'stock/catalog_list.html'
    context_object_name = 'items'
    paginate_by = 20
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(code__icontains=q) |
                Q(description__icontains=q) |
                Q(category__icontains=q) |
                Q(sub_category__icontains=q) |
                Q(keywords__icontains=q)
            )
        cat = self.request.GET.get('category')
        if cat:
            qs = qs.filter(category__iexact=cat)
        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = StandardItem.objects.values_list('category', flat=True).distinct().order_by('category')
        return ctx

class StandardItemDetailView(DetailView):
    model = StandardItem
    template_name = 'stock/catalog_detail.html'
    slug_field = 'code'
    slug_url_kwarg = 'code'

def add_to_inventory(request, code):
    std_item = get_object_or_404(StandardItem, code=code)
    cat_name = std_item.category
    category = Category.objects.filter(name__iexact=cat_name).first()
    if not category:
        code_candidate = cat_name[:3].upper()
        count = 1
        orig = code_candidate
        while Category.objects.filter(code=code_candidate).exists():
            code_candidate = f"{orig[:2]}{count}"
            count += 1
            if count > 9:
                code_candidate = orig + str(count)
        category = Category.objects.create(name=cat_name, code=code_candidate)
        messages.info(request, f"Categoría '{cat_name}' creada automáticamente.")
    item = Item.objects.create(
        name=std_item.description[:200],
        category=category,
        status='FUNCIONAL',
        quantity=1,
        description=std_item.notes or std_item.description,
    )
    messages.success(request, f"Ítem '{item.name}' añadido al inventario con código {item.code}.")
    return redirect('item_detail', code=item.code)