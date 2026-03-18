from collections import defaultdict
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef, Prefetch, Sum
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Order, OrderItem, set_order_status
from .serializers import OrderItemSerializer, OrderSerializer, OrderStatusSerializer


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
        order_filters = {'store__user': request.user}

        store = request.query_params.get('store', '').strip()
        if store:
            order_filters['store_id'] = store

        date_from = request.query_params.get('date_from', '').strip()
        parsed_from = parse_date(date_from) if date_from else None
        if parsed_from:
            order_filters['created_at__date__gte'] = parsed_from

        date_to = request.query_params.get('date_to', '').strip()
        parsed_to = parse_date(date_to) if date_to else None
        if parsed_to:
            order_filters['created_at__date__lte'] = parsed_to

        schema = request.query_params.get('schema', '').strip().upper()
        if schema and schema != 'ALL':
            order_filters['schema'] = schema

        offer_id = request.query_params.get('offer_id', '').strip()

        base_orders_qs = Order.objects.filter(**order_filters)
        if offer_id:
            matched_items_subquery = OrderItem.objects.filter(
                order_id=OuterRef('pk'),
                product__offer_id__icontains=offer_id,
            )
            base_orders_qs = base_orders_qs.annotate(has_offer_match=Exists(matched_items_subquery)).filter(has_offer_match=True)

        orders_qs = (
            base_orders_qs.select_related('store')
            .order_by('-created_at', '-id')
        )

        filtered_items_qs = (
            OrderItem.objects.filter(order__in=orders_qs)
            .select_related('product', 'order')
            .order_by('id')
        )
        if offer_id:
            filtered_items_qs = filtered_items_qs.filter(product__offer_id__icontains=offer_id)

        items_by_order = defaultdict(list)
        item_rows = list(filtered_items_qs)
        for item in item_rows:
            items_by_order[item.order_id].append(item)

        order_items_count = defaultdict(int)
        order_qty_total = defaultdict(int)
        order_revenue_total = defaultdict(Decimal)
        order_expenses_total = defaultdict(Decimal)
        order_markup_sum = defaultdict(Decimal)
        order_markup_count = defaultdict(int)
        for item in item_rows:
            order_items_count[item.order_id] += 1
            order_qty_total[item.order_id] += item.qty
            order_revenue_total[item.order_id] += item.revenue
            order_expenses_total[item.order_id] += item.expenses_allocated
            order_markup_sum[item.order_id] += item.markup_ratio_fact
            order_markup_count[item.order_id] += 1

        orders_data = []
        for order in orders_qs:
            filtered_items = items_by_order.get(order.id, [])
            first_offer_id = filtered_items[0].product.offer_id if filtered_items else ''
            avg_markup = None
            if order_markup_count[order.id]:
                avg_markup = order_markup_sum[order.id] / order_markup_count[order.id]

            orders_data.append(
                {
                    'id': order.id,
                    'posting_number': order.posting_number,
                    'status': order.status,
                    'schema': order.schema,
                    'store_name': order.store.name,
                    'created_at': order.created_at,
                    'updated_at': order.updated_at,
                    'items': OrderItemSerializer(filtered_items, many=True).data,
                    'first_offer_id': first_offer_id,
                    'items_count': order_items_count[order.id],
                    'qty_total': order_qty_total[order.id],
                    'revenue_total': order_revenue_total[order.id],
                    'expenses_total': order_expenses_total[order.id],
                    'markup_ratio_avg': avg_markup,
                }
            )

        status_breakdown = list(
            orders_qs.values('status').annotate(count=Count('id')).order_by('-count', 'status')
        )

        total_revenue = sum((item.revenue for item in item_rows), Decimal('0'))
        total_expenses = sum((item.expenses_allocated for item in item_rows), Decimal('0'))

        hourly_breakdown = [0] * 24
        for order in orders_qs:
            local_dt = order.created_at.astimezone()
            hourly_breakdown[local_dt.hour] += 1

        stores_data = list(request.user.stores.values('id', 'name').order_by('name'))
        summary_scope = 'matched_items' if offer_id else 'all_items_in_filtered_orders'

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
                    'total_orders': len(orders_data),
                    'total_items': len(item_rows),
                    'total_units': sum(item.qty for item in item_rows),
                    'total_revenue': total_revenue,
                    'total_expenses': total_expenses,
                    'status_breakdown': status_breakdown,
                    'scope': summary_scope,
                    'scope_label': (
                        'Итоги посчитаны только по позициям, совпавшим с фильтром offer_id.'
                        if offer_id
                        else 'Итоги посчитаны по всем позициям в отфильтрованных заказах.'
                    ),
                },
                'hourly': hourly_breakdown,
                'orders': orders_data,
            }
        )


@login_required
def orders_page(request):
    return render(request, 'orders/orders_page.html')
