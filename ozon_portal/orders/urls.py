from django.urls import path
from .views import OrderListView, OrderSetStatusView

urlpatterns = [
    path('', OrderListView.as_view()),
    path('<int:pk>/set-status', OrderSetStatusView.as_view()),
]
