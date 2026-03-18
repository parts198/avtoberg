from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from catalog.models import Product
from orders.models import Order, OrderItem
from stores.models import Store


class OrdersDashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')

        self.store_1 = Store.objects.create(user=self.user, name='Main Store', client_id='c1', api_key='k1')
        self.store_2 = Store.objects.create(user=self.user, name='Second Store', client_id='c2', api_key='k2')
        self.other_store = Store.objects.create(user=self.other_user, name='Other Store', client_id='c3', api_key='k3')

        self.product_1 = Product.objects.create(store=self.store_1, offer_id='offer-apple', name='Apple')
        self.product_2 = Product.objects.create(store=self.store_1, offer_id='offer-banana', name='Banana')
        self.product_3 = Product.objects.create(store=self.store_2, offer_id='offer-orange', name='Orange')
        self.other_product = Product.objects.create(store=self.other_store, offer_id='offer-secret', name='Secret')

        self.order_1 = Order.objects.create(store=self.store_1, posting_number='P-1', status='created', schema='FBS')
        self.order_2 = Order.objects.create(store=self.store_2, posting_number='P-2', status='awaiting_delivery', schema='FBO')
        self.other_order = Order.objects.create(store=self.other_store, posting_number='P-3', status='cancelled', schema='FBS')

        OrderItem.objects.create(order=self.order_1, product=self.product_1, qty=2, price=100, revenue=200, expenses_allocated=50, markup_ratio_fact=1.5)
        OrderItem.objects.create(order=self.order_1, product=self.product_2, qty=1, price=300, revenue=300, expenses_allocated=100, markup_ratio_fact=2.0)
        OrderItem.objects.create(order=self.order_2, product=self.product_3, qty=4, price=80, revenue=320, expenses_allocated=110, markup_ratio_fact=1.2)
        OrderItem.objects.create(order=self.other_order, product=self.other_product, qty=10, price=10, revenue=100, expenses_allocated=20, markup_ratio_fact=0.3)

        now = timezone.now()
        Order.objects.filter(pk=self.order_1.pk).update(created_at=now - timedelta(days=2))
        Order.objects.filter(pk=self.order_2.pk).update(created_at=now - timedelta(days=1))
        Order.objects.filter(pk=self.other_order.pk).update(created_at=now)

    def test_orders_page_for_authorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_data_basic(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/orders/dashboard-data/')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['summary']['total_orders'], 2)
        self.assertEqual(len(payload['orders']), 2)

    def test_dashboard_filter_store(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/orders/dashboard-data/', {'store': self.store_1.id})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['summary']['total_orders'], 1)
        self.assertEqual(payload['orders'][0]['posting_number'], 'P-1')

    def test_dashboard_filter_schema(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/orders/dashboard-data/', {'schema': 'FBO'})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['summary']['total_orders'], 1)
        self.assertEqual(payload['orders'][0]['schema'], 'FBO')

    def test_dashboard_filter_offer_id_returns_only_matched_items(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/orders/dashboard-data/', {'offer_id': 'apple'})
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload['summary']['total_orders'], 1)
        self.assertEqual(payload['summary']['total_items'], 1)
        self.assertEqual(payload['summary']['scope'], 'matched_items')

        order = payload['orders'][0]
        self.assertEqual(order['posting_number'], 'P-1')
        self.assertEqual(len(order['items']), 1)
        self.assertEqual(order['items'][0]['offer_id'], 'offer-apple')

    def test_dashboard_excludes_foreign_orders(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/orders/dashboard-data/')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        posting_numbers = [order['posting_number'] for order in payload['orders']]
        self.assertNotIn('P-3', posting_numbers)
