from django.urls import path
from .views import ActionsListView, ActionsCandidatesView, ActionsProductsView, ActionsActivateView, ActionsDeactivateView

urlpatterns = [
    path('actions/', ActionsListView.as_view()),
    path('actions/candidates/', ActionsCandidatesView.as_view()),
    path('actions/products/', ActionsProductsView.as_view()),
    path('actions/activate/', ActionsActivateView.as_view()),
    path('actions/deactivate/', ActionsDeactivateView.as_view()),
]
