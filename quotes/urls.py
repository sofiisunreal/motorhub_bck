from django.urls import path
from .views import CreateQuoteView, QuoteListView, QuoteUpdateView

urlpatterns = [
    path('request/', CreateQuoteView.as_view(), name='create_quote'),
    path('', QuoteListView.as_view(), name='quote_list'),
    path('<int:pk>/', QuoteUpdateView.as_view(), name='update_quote'),
]