from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
  price = request.data.get("price")
  status = request.data.get("status", "available")

  if not supplier_id or not brand or not year or not vin_number or not price:
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
      price=price,
      status=status
    )
    return Response({
      "message": "Car added successfully",
      "car_id": car.id
    }, status=201)
  except Exception as e:
    return Response({"error": str(e)}, status=400)

# view cars
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ViewCars(request):
  status_filter = request.query_params.get("status")
  if status_filter:
    cars = Car.objects.filter(status=status_filter)
  else:
    cars = Car.objects.all()

  cars_data = []
  for car in cars:
    cars_data.append({
      "id": car.id,
      "supplier": car.supplier.company_name,
      "brand": car.brand,
      "year": car.year,
      "vin_number": car.vin_number,
      "price": str(car.buying_price),
      "status": car.status,
      "image": request.build_absolute_uri(car.image.url) if car.image else None
    })

  return Response(cars_data, status=200)

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

