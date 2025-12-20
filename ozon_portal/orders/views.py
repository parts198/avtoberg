from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order, set_order_status
from .serializers import OrderSerializer, OrderStatusSerializer

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(store__user=self.request.user).prefetch_related('items')

class OrderSetStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = Order.objects.filter(store__user=request.user, pk=pk).first()
        if not order:
            return Response({'detail': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        set_order_status(order, serializer.validated_data['status'])
        return Response(OrderSerializer(order).data)
