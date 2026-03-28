from django.urls import path
from . import views

app_name = 'debt'

urlpatterns = [
    # Asosiy sahifalar
    path('', views.debt_dashboard_view, name='debt_dashboard'),
    path('list/', views.debt_list_view, name='debt_list'),
    
    # CRUD amallari
    path('add/', views.debt_add_view, name='debt_add'),
    path('detail/<int:debt_id>/', views.debt_detail_view, name='debt_detail'),
    path('update/<int:debt_id>/', views.debt_update_view, name='debt_update'),
    path('delete/<int:debt_id>/', views.debt_delete_view, name='debt_delete'),
    
    # AJAX endpointlar
    path('ajax/organization-search/', views.ajax_organization_search, name='ajax_organization_search'),
    path('ajax/debt-list/', views.ajax_debt_list, name='ajax_debt_list'),
    path('ajax/add-payment/<int:debt_id>/', views.ajax_add_payment, name='ajax_add_payment'),
    path('ajax/statistics/', views.ajax_debt_statistics, name='ajax_statistics'),
]
