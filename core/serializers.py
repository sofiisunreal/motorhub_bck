from rest_framework import serializers
from .models import User

class StaffSerializer(serializers.ModelSerializer):

    cars_sold = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "role",
            "cars_sold"
        ]

    def get_cars_sold(self, obj):
        return obj.sales.count()
