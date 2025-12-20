from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ozon_portal import settings
from .serializers import RegisterSerializer, BootstrapSerializer
from .models import BootstrapState
from prices.models import ExpensePolicySettings

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class BootstrapAdminView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = BootstrapSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        if token != settings.BOOTSTRAP_TOKEN:
            return Response({'detail': 'Неверный токен'}, status=status.HTTP_403_FORBIDDEN)
        state, _ = BootstrapState.objects.get_or_create(id=1)
        if state.executed:
            return Response({'detail': 'Bootstrap уже выполнен'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            state = BootstrapState.objects.select_for_update().get(id=state.id)
            if state.executed:
                return Response({'detail': 'Bootstrap уже выполнен'}, status=status.HTTP_400_BAD_REQUEST)
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            email = serializer.validated_data.get('email', '')
            if User.objects.filter(username=username).exists():
                return Response({'detail': 'Пользователь существует'}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create_superuser(username=username, password=password, email=email)
            ExpensePolicySettings.objects.get_or_create(user=user, defaults={'policy': 'USE_MAX'})
            state.executed = True
            state.executed_at = timezone.now()
            state.save()
        return Response({'detail': 'Администратор создан'}, status=status.HTTP_201_CREATED)
