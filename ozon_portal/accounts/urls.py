from django.urls import path
from .views import RegisterView, BootstrapAdminView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('bootstrap/', BootstrapAdminView.as_view(), name='bootstrap-admin'),
]
