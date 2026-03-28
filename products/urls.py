from django.urls import path

from . import views
from . import barcode_views

app_name = "products"
urlpatterns = [
    # List categories
    path('categories', views.categories_list_view, name='categories_list'),
    # Add category
    path('categories/add', views.categories_add_view, name='categories_add'),
    # Update category
    path('categories/update/<str:category_id>',
         views.categories_update_view, name='categories_update'),
    # Delete category
    path('categories/delete/<str:category_id>',
         views.categories_delete_view, name='categories_delete'),

    # List products
    path('', views.products_list_view, name='products_list'),
    # Add product
    path('add', views.products_add_view, name='products_add'),
    # Update product
    path('update/<str:product_id>',
         views.products_update_view, name='products_update'),
    # Delete product
    path('delete/<str:product_id>',
         views.products_delete_view, name='products_delete'),
    # Get products AJAX
    path("get", views.get_products_ajax_view, name="get_products"),
    
    # Barcode URLs
    path('barcode/download/<int:product_id>/', barcode_views.download_product_barcode, name='download_barcode'),
    path('barcode/bulk/<int:product_id>/', barcode_views.download_bulk_barcode, name='download_bulk_barcode'),
    path('barcode/multiple/', barcode_views.download_multiple_barcodes, name='download_multiple_barcodes'),
    path('barcode/new-stock/<int:product_id>/', barcode_views.print_new_stock_barcodes, name='print_new_stock_barcodes'),
    path('barcode/generate/<int:product_id>/', barcode_views.generate_barcode_for_product, name='generate_barcode'),
]
