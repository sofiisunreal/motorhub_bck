from rest_framework import serializers
from .models import Quote
from cars.models import Car


class QuoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = [
            'car',
            'customer_name',
            'customer_phone',
            'customer_email',
            'message',
        ]


class QuoteCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            'id',
            'brand',
            'year',
            'vin_number',
            'status',
            'image',
        ]


class QuoteSerializer(serializers.ModelSerializer):
    car = QuoteCarSerializer(read_only=True)

    class Meta:
        model = Quote
        fields = [
            'id',
            'car',
            'customer_name',
            'customer_phone',
            'customer_email',
            'message',
            'status',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'status',
            'created_at',
        ]


class QuoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ['status']
