from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Store
from .serializers import StoreSerializer

class StoreListCreateView(generics.ListCreateAPIView):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Store.objects.filter(user=self.request.user)
