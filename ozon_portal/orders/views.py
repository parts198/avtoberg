from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Sum
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Order, OrderItem, set_order_status
from .serializers import OrderSerializer, OrderStatusSerializer


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(store__user=self.request.user)
            .select_related('store')
            .prefetch_related(Prefetch('items', queryset=OrderItem.objects.select_related('product')))
        )


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


@method_decorator(login_required, name='dispatch')
class OrdersDashboardDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def get(self, request):
        queryset = (
            Order.objects.filter(store__user=request.user)
            .select_related('store')
            .prefetch_related(Prefetch('items', queryset=OrderItem.objects.select_related('product')))
            .order_by('-created_at')
        )

        store = request.query_params.get('store', '').strip()
        if store:
            queryset = queryset.filter(store_id=store)

        date_from = request.query_params.get('date_from', '').strip()
        if date_from:
            parsed_from = parse_date(date_from)
            if parsed_from:
                queryset = queryset.filter(created_at__date__gte=parsed_from)

        date_to = request.query_params.get('date_to', '').strip()
        if date_to:
            parsed_to = parse_date(date_to)
            if parsed_to:
                queryset = queryset.filter(created_at__date__lte=parsed_to)

        schema = request.query_params.get('schema', '').strip().upper()
        if schema and schema != 'ALL':
            queryset = queryset.filter(schema=schema)

        offer_id = request.query_params.get('offer_id', '').strip()
        if offer_id:
            queryset = queryset.filter(items__product__offer_id__icontains=offer_id)

        total_orders = queryset.values('id').distinct().count()
        totals = queryset.aggregate(
            total_items=Sum('items__qty'),
            total_revenue=Sum('items__revenue'),
            total_expenses=Sum('items__expenses_allocated'),
        )
        status_breakdown = list(
            queryset.values('status').annotate(count=Count('id', distinct=True)).order_by('-count', 'status')
        )

        orders_data = OrderSerializer(queryset.distinct(), many=True).data
        stores_data = list(
            request.user.stores.values('id', 'name').order_by('name')
        )

        return Response(
            {
                'stores': stores_data,
                'filters': {
                    'store': store,
                    'date_from': date_from,
                    'date_to': date_to,
                    'schema': schema or 'ALL',
                    'offer_id': offer_id,
                },
                'summary': {
                    'total_orders': total_orders,
                    'total_items': totals['total_items'] or 0,
                    'total_revenue': totals['total_revenue'] or 0,
                    'total_expenses': totals['total_expenses'] or 0,
                    'status_breakdown': status_breakdown,
                },
                'orders': orders_data,
            }
        )


@login_required
def orders_page(request):
    return render(request, 'orders/orders_page.html')
