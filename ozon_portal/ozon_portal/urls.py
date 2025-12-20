from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('accounts.urls')),
    path('api/stores/', include('stores.urls')),
    path('api/products/', include('catalog.urls')),
    path('api/warehouses/', include('warehouses.urls')),
    path('api/stocks/', include('stocks.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/prices/', include('prices.urls')),
    path('api/promotions/', include('promotions.urls')),
    path('api/logs/', include('audit.urls')),
    path('api/ozon/', include('ozon.urls')),
]
