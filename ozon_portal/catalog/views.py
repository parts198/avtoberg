from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product
from .serializers import ProductSerializer, ProductGroupSerializer, OfferCandidateSerializer
from .services import find_candidates, confirm_group, propose_candidate

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(store__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

class OfferCandidateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        offer_id = request.query_params.get('offer_id')
        if not offer_id:
            return Response({'detail': 'offer_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        products = find_candidates(request.user, offer_id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ConfirmGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        offer_ids = request.data.get('offer_ids', [])
        if not offer_ids:
            return Response({'detail': 'Нужно передать offer_ids'}, status=status.HTTP_400_BAD_REQUEST)
        group = confirm_group(request.user, offer_ids)
        return Response(ProductGroupSerializer(group).data)

class ProposeCandidateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = OfferCandidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        candidate = propose_candidate(request.user, serializer.validated_data['source_offer_id'], serializer.validated_data['target_offer_id'])
        return Response(OfferCandidateSerializer(candidate).data, status=status.HTTP_201_CREATED)
