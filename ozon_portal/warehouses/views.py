from rest_framework import generics, permissions
from .models import Warehouse
from .serializers import WarehouseSerializer

class WarehouseListCreateView(generics.ListCreateAPIView):
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        store_id = self.request.query_params.get('store')
        qs = Warehouse.objects.filter(store__user=self.request.user)
        if store_id:
            qs = qs.filter(store_id=store_id)
        return qs

    def perform_create(self, serializer):
        serializer.save()
