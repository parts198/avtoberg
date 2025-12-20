from django.urls import path
from .views import StockListView, StockUploadView

urlpatterns = [
    path('', StockListView.as_view(), name='stock-list'),
    path('upload/', StockUploadView.as_view(), name='stock-upload'),
]
