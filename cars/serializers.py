from rest_framework import serializers
from suppliers.models import Supplier
from .models import Car

class CarSerializer(serializers.ModelSerializer):
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), source="supplier"
    )
    supplier_name = serializers.CharField(
        source="supplier.company_name", read_only=True
    )

    class Meta:
        model = Car
        fields = [
            "id",
            "supplier_id",
            "supplier_name",
            "brand",
            "year",
            "vin_number",
            "buying_price",
            "status",
            "image",
        ]
