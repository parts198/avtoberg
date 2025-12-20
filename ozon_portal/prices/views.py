from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PriceExpenseSnapshot, ExpensePolicySettings
from .serializers import PriceExpenseSnapshotSerializer, ExpensePolicySettingsSerializer
from catalog.models import Product
from django.db import transaction

class PriceSnapshotView(generics.ListAPIView):
    serializer_class = PriceExpenseSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PriceExpenseSnapshot.objects.filter(product__store__user=self.request.user)

class ExpensePolicyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        policy, _ = ExpensePolicySettings.objects.get_or_create(user=request.user)
        return Response(ExpensePolicySettingsSerializer(policy).data)

    def put(self, request):
        policy, _ = ExpensePolicySettings.objects.get_or_create(user=request.user)
        serializer = ExpensePolicySettingsSerializer(policy, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class DesiredPriceUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        offer_id = request.data.get('offer_id')
        price = request.data.get('desired_marketing_seller_price')
        if not offer_id:
            return Response({'detail': 'offer_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        product = Product.objects.filter(store__user=request.user, offer_id=offer_id).first()
        if not product:
            return Response({'detail': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        snapshot, _ = PriceExpenseSnapshot.objects.get_or_create(product=product)
        snapshot.desired_marketing_seller_price = price or 0
        snapshot.save()
        return Response(PriceExpenseSnapshotSerializer(snapshot).data)

class PriceRecalcView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_ids = request.data.get('product_ids', [])
        qs = PriceExpenseSnapshot.objects.filter(product__store__user=request.user)
        if product_ids:
            qs = qs.filter(product_id__in=product_ids)
        with transaction.atomic():
            for snap in qs.select_for_update():
                if snap.net_price:
                    snap.total_ozon_expenses = snap.marketing_seller_price * (snap.commissions_percent_fbs or 0) / 100 + snap.acquiring
                    snap.markup_ratio = (snap.marketing_seller_price - snap.total_ozon_expenses) / (snap.net_price or 1)
                    snap.save()
        return Response({'detail': 'Пересчитано'})
