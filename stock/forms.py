from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    new_category_name = forms.CharField(
        label="Nombre de nueva categoría", 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Solo si seleccionaste Nueva Categoría'})
    )

    class Meta:
        model = Item
        fields = ['name', 'category', 'status', 'quantity', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ImportForm(forms.Form):
    excel_file = forms.FileField(label="Archivo Excel (.xlsx)")
