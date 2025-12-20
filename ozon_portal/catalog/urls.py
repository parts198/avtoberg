from django.urls import path
from .views import ProductListCreateView, OfferCandidateView, ConfirmGroupView, ProposeCandidateView

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('product-groups/offer-candidates/', OfferCandidateView.as_view(), name='offer-candidates'),
    path('product-groups/confirm', ConfirmGroupView.as_view(), name='confirm-group'),
    path('offer-candidates/', ProposeCandidateView.as_view(), name='propose-candidate'),
]
