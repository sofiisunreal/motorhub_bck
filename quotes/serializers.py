from rest_framework import serializers
from .models import Quote

class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model= Quote
        fields=[
            'id',
            'car',
            'customer_name',
            'customer_phone',
            'message',
            'status',
            'created_at'
        ]
        read_only_fields=[
            'id',
            'status',
            'created_at'
        ]
class QuoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Quote
        fields=['status']