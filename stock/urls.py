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
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('catalog/', views.StandardCatalogView.as_view(), name='catalog_list'),
    path('catalog/<str:code>/', views.StandardItemDetailView.as_view(), name='catalog_detail'),
    path('catalog/<str:code>/add_to_inventory/', views.add_to_inventory, name='add_to_inventory'),
]