from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    # Tashkilotlar
    path('', views.organizations_list_view, name='organizations_list'),
    path('add/', views.organizations_add_view, name='organizations_add'),
    path('update/<int:organization_id>/', views.organizations_update_view, name='organizations_update'),
    path('delete/<int:organization_id>/', views.organizations_delete_view, name='organizations_delete'),
    path('detail/<int:organization_id>/', views.organizations_detail_view, name='organizations_detail'),
    
    # Shartnomalar
    path('contracts/', views.contracts_list_view, name='contracts_list'),
    path('contracts/add/', views.contracts_add_view, name='contracts_add'),
    path('contracts/update/<int:contract_id>/', views.contracts_update_view, name='contracts_update'),
    path('contracts/delete/<int:contract_id>/', views.contracts_delete_view, name='contracts_delete'),
    path('contracts/detail/<int:contract_id>/', views.contracts_detail_view, name='contracts_detail'),
    
    # Yuk xatlari
    path('delivery-notes/', views.delivery_notes_list_view, name='delivery_notes_list'),
    path('delivery-notes/add/', views.delivery_notes_add_view, name='delivery_notes_add'),
    path('delivery-notes/detail/<int:delivery_note_id>/', views.delivery_notes_detail_view, name='delivery_notes_detail'),
    path('delivery-notes/delete/<int:delivery_note_id>/', views.delivery_notes_delete_view, name='delivery_notes_delete'),
    path('delivery-notes/pdf/<int:delivery_note_id>/', views.delivery_note_pdf_view, name='delivery_note_pdf'),
    
    # Barcode
    path('barcode/search/', views.barcode_search_view, name='barcode_search'),
    path('barcode/generate/<int:product_id>/', views.barcode_generate_view, name='barcode_generate'),
    
    # To'lovlar
    path('payments/add/<int:delivery_note_id>/', views.payment_add_view, name='payment_add'),
    path('payments/delete/<int:payment_id>/', views.payment_delete_view, name='payment_delete'),
    
    # Hisobotlar
    path('reports/', views.reports_dashboard_view, name='reports_dashboard'),
    path('reports/inventory/', views.reports_inventory_view, name='reports_inventory'),
    path('reports/sales/', views.reports_sales_view, name='reports_sales'),
    
    # Xodimlar
    path('employees/', views.employees_list_view, name='employees_list'),
    path('employees/<int:employee_id>/permissions/', views.employee_permissions_view, name='employee_permissions'),
    
    # Ombor
    path('warehouse/', views.warehouse_inventory_view, name='warehouse_inventory'),
    path('warehouse/receive/', views.warehouse_receive_view, name='warehouse_receive'),
    path('warehouse/product/<int:product_id>/history/', views.warehouse_product_history_view, name='warehouse_product_history'),
]
