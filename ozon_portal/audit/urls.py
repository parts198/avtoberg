from django.urls import path
from .views import ApiRequestLogView, ApiErrorLogView, StockLogView, ReservationLogView, TaskLogView

urlpatterns = [
    path('ozon-requests', ApiRequestLogView.as_view()),
    path('errors', ApiErrorLogView.as_view()),
    path('stocks', StockLogView.as_view()),
    path('reservations', ReservationLogView.as_view()),
    path('tasks', TaskLogView.as_view()),
]
