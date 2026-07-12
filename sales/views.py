from django.shortcuts import render
from rest_framework import request, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from cars.models import Car
from sales.models import Sale
# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def SellCar(request):
    if request.user.role != "staff":
        return Response(
            {"error": "Only staff can sell cars"},
            status=403
        )
    car_id = request.data.get("car_id")
    customer_name = request.data.get("customer_name")
    customer_phone = request.data.get("customer_phone")
    selling_price = request.data.get("selling_price")
    notes = request.data.get("notes")

    if not car_id or not customer_name or not customer_phone or not selling_price:
        return Response(
            {"error": "All required fields are required"},
            status=400
        )

    try:
        car = Car.objects.get(vin_number=car_id)
    except Car.DoesNotExist:
        return Response(
            {"error": "Car does not exist"},
            status=400
        )

    if car.status != "available":
        return Response(
            {"error": "Car is not available for sale"},
            status=400
        )

    try:
        car.status = "sold"
        car.save()

        sale=Sale.objects.create(
            car=car,
            sold_by=request.user,
            customer_name=customer_name,
            customer_phone=customer_phone,
            selling_price=selling_price,
            notes=notes
        )

        return Response({
            "message": "Car sold successfully",
            "sale_id": sale.id,
            "car_id": car.vin_number,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "selling_price": selling_price,
            "notes": notes,
            "sold_by": sale.sold_by.username,
        }, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

# view sales
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ViewSales(request):

    if request.user.role == "admin":
        sales = Sale.objects.all()

    elif request.user.role == "staff":
        sales = Sale.objects.filter(sold_by=request.user)

    else:
        return Response(
            {"error": "Unauthorized"},
            status=403
        )

    data = []

    for sale in sales:
        profit = sale.selling_price - sale.car.buying_price

        data.append({
            "sale_id": sale.id,
            "vin_number": sale.car.vin_number,
            "brand": sale.car.brand,
            "customer_name": sale.customer_name,
            "customer_phone": sale.customer_phone,
            "selling_price": sale.selling_price,
            "buying_price": sale.car.buying_price,
            "profit": profit,
            "sold_by": sale.sold_by.username if sale.sold_by else None,
            "status": sale.car.status,
            "date": sale.created_at
        })

    return Response(data)


