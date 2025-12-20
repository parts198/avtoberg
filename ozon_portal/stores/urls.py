from django.urls import path
from .views import StoreListCreateView

urlpatterns = [
    path('', StoreListCreateView.as_view(), name='store-list-create'),
]
