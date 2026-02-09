from django.urls import path
from . import views

urlpatterns = [
    path('', views.ItemListView.as_view(), name='item_list'),
    path('add/', views.ItemCreateView.as_view(), name='item_add'),
    path('import/', views.BulkImportView.as_view(), name='import_excel'),
    path('scan/', views.ScannerView.as_view(), name='scanner'),
    path('set_language/<str:lang_code>/', views.set_language, name='set_language'),
    path('items/<str:code>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('items/<str:code>/edit/', views.ItemUpdateView.as_view(), name='item_edit'),
]
