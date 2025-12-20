from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class PingView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({'pong': True})

urlpatterns = [
    path('ping/', PingView.as_view()),
]
