
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.response import Response
from rest_framework import generics
from cars.serializers import CarSerializer
from suppliers.models import Supplier

from .models import Car

# add car
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def AddCar(request):
  if request.user.role != "admin":
    return Response(
      {"error": "Only admins can add cars"},
      status=403
    )
  supplier_id = request.data.get("supplier_id")
  brand = request.data.get("brand")
  year = request.data.get("year")
  vin_number = request.data.get("vin_number")
  buying_price = request.data.get("buying_price")
  status = request.data.get("status", "available")
  image = request.FILES.get("image")

  if not supplier_id or not brand or not year or not vin_number or not buying_price:
    return Response(
      {"error": "All required fields are required"},
      status=400
    )
  if Car.objects.filter(vin_number=vin_number).exists():
    return Response(
      {"error": "Car with this VIN number already exists"},
      status=400
    )

  try:
    supplier = Supplier.objects.get(id=supplier_id)
  except Supplier.DoesNotExist:
    return Response(
      {"error": "Supplier does not exist"},
      status=400
    )

  try:
    car = Car.objects.create(
      supplier=supplier,
      brand=brand,
      year=year,
      vin_number=vin_number,
      buying_price=buying_price,
      status=status,
      image=image
    )
    return Response({
      "message": "Car added successfully",
      "car_id": car.id
    }, status=201)
  except Exception as e:
    return Response({"error": str(e)}, status=400)

# view cars based on statusof the car
@api_view(["GET"])
@permission_classes([AllowAny])
def ViewCars(request):
    status_filter = request.query_params.get("status")
    if status_filter:
        cars = Car.objects.filter(status=status_filter)
    else:
        cars = Car.objects.all()

    serializer = CarSerializer(cars, many=True, context={"request": request})
    return Response(serializer.data, status=200)

@api_view(["GET"])
@permission_classes([AllowAny])
def ViewSingleCar(request, id):

    try:
        car = Car.objects.get(id=id)

    except Car.DoesNotExist:
        return Response(
            {"error":"Car does not exist"},
            status=404
        )

    serializer = CarSerializer(
        car,
        context={"request": request}
    )

    return Response(serializer.data)

# update car status
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def UpdateCarStatus(request, id):
  try:
    car = Car.objects.get(id=id)
  except Car.DoesNotExist:
    return Response(
      {"error": "Car does not exist"},
      status=404
    )

  try:
    new_status = request.data.get("status")
    if new_status not in ["available", "reserved", "sold"]:
      return Response(
        {"error": "Invalid status value"},
        status=400
      )

    car.status = new_status
    car.save()

    return Response({
      "message": "Car status updated successfully",
      "car_id": car.id,
      "new_status": car.status
    }, status=200)
  except Exception as e:
    return Response({"error": str(e)}, status=400)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def UpdateCar(request, id):
    try:
        car = Car.objects.get(id=id)
    except Car.DoesNotExist:
        return Response(
            {"error": "Car does not exist"},
            status=404
        )

    serializer = CarSerializer(
        car,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
            status=200
        )

    return Response(
        serializer.errors,
        status=400
    )

