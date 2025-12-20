from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from stores.models import Store
from ozon.client import OzonClient

class ProxyBase(APIView):
    permission_classes = [permissions.IsAuthenticated]
    path = ''

    def post(self, request):
        store_id = request.data.get('store_id')
        store = Store.objects.filter(user=request.user, id=store_id).first()
        if not store:
            return Response({'detail': 'Магазин не найден'}, status=404)
        client = OzonClient(store.client_id, store.api_key, store_id=store.id)
        data = client.post(self.path, request.data)
        return Response(data)

    def get(self, request):
        store_id = request.query_params.get('store_id')
        store = Store.objects.filter(user=request.user, id=store_id).first()
        if not store:
            return Response({'detail': 'Магазин не найден'}, status=404)
        client = OzonClient(store.client_id, store.api_key, store_id=store.id)
        data = client.post(self.path, {})
        return Response(data)

class ActionsListView(ProxyBase):
    path = '/v1/actions'

class ActionsCandidatesView(ProxyBase):
    path = '/v1/actions/candidates'

class ActionsProductsView(ProxyBase):
    path = '/v1/actions/products'

class ActionsActivateView(ProxyBase):
    path = '/v1/actions/products/activate'

class ActionsDeactivateView(ProxyBase):
    path = '/v1/actions/products/deactivate'
