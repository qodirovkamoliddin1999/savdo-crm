from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication: Login and Logout
    path('', include('authentication.urls')),
    # Index
    path('', include('pos.urls')),
    # Products
    path('products/', include('products.urls')),
    # Customers
    path('customers/', include('customers.urls')),
    # Sales
    path('sales/', include('sales.urls')),
    # Organizations
    path('organizations/', include('organizations.urls')),
    # Debt
    path('debt/', include('debt.urls')),
]

# Media fayllarni development rejimida xizmat qilish
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
