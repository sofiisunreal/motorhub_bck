from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticated

from .models import Quote
from .serializers import  QuoteSerializer, QuoteUpdateSerializer, QuoteCreateSerializer
# Create your views here.

class CreateQuoteView(generics.CreateAPIView):
    queryset = Quote.objects.all()
    serializer_class = QuoteCreateSerializer
    permission_classes = [AllowAny]


class QuoteListView(generics.ListAPIView):
    queryset = Quote.objects.select_related('car').all().order_by('-created_at')
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated]


class QuoteUpdateView(generics.UpdateAPIView):
    queryset = Quote.objects.all()
    serializer_class = QuoteUpdateSerializer
    permission_classes = [IsAuthenticated]
