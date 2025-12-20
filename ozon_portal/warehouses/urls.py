from django.urls import path
from .views import WarehouseListCreateView

urlpatterns = [
    path('', WarehouseListCreateView.as_view(), name='warehouse-list-create'),
]
