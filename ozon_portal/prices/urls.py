from django.urls import path
from .views import PriceSnapshotView, ExpensePolicyView, DesiredPriceUpdateView, PriceRecalcView

urlpatterns = [
    path('snapshot/', PriceSnapshotView.as_view()),
    path('policy/', ExpensePolicyView.as_view()),
    path('desired/', DesiredPriceUpdateView.as_view()),
    path('recalc/', PriceRecalcView.as_view()),
]
