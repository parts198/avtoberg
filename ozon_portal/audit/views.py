from rest_framework import generics, permissions
from .models import ApiRequestLog, ApiErrorLog, StockLog, ReservationLog, TaskLog
from .serializers import ApiRequestLogSerializer, ApiErrorLogSerializer, StockLogSerializer, ReservationLogSerializer, TaskLogSerializer

class ApiRequestLogView(generics.ListAPIView):
    serializer_class = ApiRequestLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ApiRequestLog.objects.all().order_by('-created_at')

class ApiErrorLogView(generics.ListAPIView):
    serializer_class = ApiErrorLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ApiErrorLog.objects.all().order_by('-created_at')

class StockLogView(generics.ListAPIView):
    serializer_class = StockLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StockLog.objects.all().order_by('-created_at')

class ReservationLogView(generics.ListAPIView):
    serializer_class = ReservationLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReservationLog.objects.all().order_by('-created_at')

class TaskLogView(generics.ListAPIView):
    serializer_class = TaskLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskLog.objects.all().order_by('-started_at')
