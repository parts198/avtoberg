from django.urls import path

from .views import OrderListView, OrdersDashboardDataView, OrderSetStatusView

urlpatterns = [
    path('', OrderListView.as_view()),
    path('dashboard-data/', OrdersDashboardDataView.as_view(), name='orders-dashboard-data'),
    path('<int:pk>/set-status', OrderSetStatusView.as_view()),
]
