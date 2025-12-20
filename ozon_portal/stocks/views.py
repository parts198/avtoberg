import csv
from io import StringIO
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Stock
from .serializers import StockSerializer, StockUploadSerializer
from catalog.models import Product
from warehouses.models import Warehouse

class StockListView(generics.ListAPIView):
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Stock.objects.filter(product__store__user=self.request.user)

class StockUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'Нужен CSV файл'}, status=status.HTTP_400_BAD_REQUEST)
        data = file.read().decode('utf-8')
        reader = csv.DictReader(StringIO(data), fieldnames=['offer_id', 'warehouse', 'quantity'])
        for row in reader:
            offer_id = row['offer_id']
            wh_external = row['warehouse']
            qty = int(row['quantity'])
            product = Product.objects.filter(store__user=request.user, offer_id=offer_id).first()
            warehouse = Warehouse.objects.filter(store__user=request.user, external_id=wh_external).first()
            if product and warehouse:
                stock, _ = Stock.objects.get_or_create(product=product, warehouse=warehouse)
                stock.quantity = qty
                stock.save()
        return Response({'detail': 'Загружено'})
