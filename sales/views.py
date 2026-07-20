from django.utils import timezone
from django.shortcuts import render
from rest_framework import request, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from cars.models import Car
from core.models import User
from sales.models import Sale
from suppliers.models import Supplier
import csv
from django.http import HttpResponse


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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ViewSales(request):

    if request.user.role == "admin":
        sales = Sale.objects.all()

    elif request.user.role == "staff":
        sales = Sale.objects.filter(
            sold_by=request.user
        )

    else:
        return Response(
            {"error": "Unauthorized"},
            status=403
        )


    # filtering by month and year
    month = request.query_params.get("month")
    year = request.query_params.get("year")


    if month and year:
        sales = sales.filter(
            created_at__month=month,
            created_at__year=year
        )


    # filter by customer
    customer = request.query_params.get("customer")

    if customer:
        sales = sales.filter(
            customer_name__icontains=customer
        )


    data = []

    for sale in sales:

        profit = (
            sale.selling_price -
            sale.car.buying_price
        )

        data.append({

            "sale_id": sale.id,

            "vin_number": sale.car.vin_number,

            "brand": sale.car.brand,

            "customer_name": sale.customer_name,

            "customer_phone": sale.customer_phone,

            "selling_price": sale.selling_price,

            "buying_price": sale.car.buying_price,

            "profit": profit,

            "sold_by": (
                sale.sold_by.username
                if sale.sold_by
                else None
            ),

            "date": sale.created_at

        })


    return Response(data)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def AdminDashboard(request):

    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Basic counts
    total_staff = User.objects.filter(role="staff").count()
    total_suppliers = Supplier.objects.count()
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(status="available").count()
    reserved_cars = Car.objects.filter(status="reserved").count()
    sold_cars = Car.objects.filter(status="sold").count()

    # Sales periods
    today_sales = Sale.objects.filter(created_at__date=today)
    monthly_sales = Sale.objects.filter(created_at__date__gte=month_start)

    # Revenue
    today_revenue = today_sales.aggregate(
        total=Sum("selling_price")
    )["total"] or 0

    monthly_revenue = monthly_sales.aggregate(
        total=Sum("selling_price")
    )["total"] or 0

    total_revenue = Sale.objects.aggregate(
        total=Sum("selling_price")
    )["total"] or 0

    # Profit
    today_profit = today_sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or 0

    monthly_profit = monthly_sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or 0

    total_profit = Sale.objects.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or 0

    # Staff performance
    staff_performance = []
    staff_members = User.objects.filter(role="staff")

    for staff in staff_members:
        sales = Sale.objects.filter(sold_by=staff)

        revenue = sales.aggregate(
            total=Sum("selling_price")
        )["total"] or 0

        profit = sales.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("selling_price") - F("car__buying_price"),
                    output_field=DecimalField()
                )
            )
        )["total"] or 0

        staff_performance.append({
            "username": staff.username,
            "cars_sold": sales.count(),
            "revenue": revenue,
            "profit": profit
        })

    # Recent sales
    recent_sales = []

    for sale in Sale.objects.order_by("-created_at")[:5]:
        recent_sales.append({
            "sale_id": sale.id,
            "vin_number": sale.car.vin_number,
            "brand": sale.car.brand,
            "customer_name": sale.customer_name,
            "selling_price": sale.selling_price,
            "sold_by": sale.sold_by.username if sale.sold_by else None,
            "date": sale.created_at
        })

    return Response({
        "total_staff": total_staff,
        "total_suppliers": total_suppliers,
        "total_cars": total_cars,

        "available_cars": available_cars,
        "reserved_cars": reserved_cars,
        "sold_cars": sold_cars,

        "cars_sold_today": today_sales.count(),
        "cars_sold_this_month": monthly_sales.count(),

        "today_revenue": today_revenue,
        "monthly_revenue": monthly_revenue,
        "total_revenue": total_revenue,

        "today_profit": today_profit,
        "monthly_profit": monthly_profit,
        "total_profit": total_profit,

        "staff_performance": staff_performance,
        "recent_sales": recent_sales
    })
# staff dashboard
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def StaffDashboard(request):

    if request.user.role != "staff":
        return Response({"error": "Unauthorized"}, status=403)

    today = timezone.now().date()
    month_start = today.replace(day=1)

    sales = Sale.objects.filter(sold_by=request.user)
    today_sales = sales.filter(created_at__date=today)
    monthly_sales = sales.filter(created_at__date__gte=month_start)

    # Revenue
    today_revenue = today_sales.aggregate(
        total=Sum("selling_price")
    )["total"] or 0

    monthly_revenue = monthly_sales.aggregate(
        total=Sum("selling_price")
    )["total"] or 0

    total_revenue = sales.aggregate(
        total=Sum("selling_price")
    )["total"] or 0

    # Profit
    today_profit = today_sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or 0

    monthly_profit = monthly_sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or 0

    total_profit = sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or 0

    # Recent sales
    recent_sales = []

    for sale in sales.order_by("-created_at")[:5]:
        recent_sales.append({
            "sale_id": sale.id,
            "vin_number": sale.car.vin_number,
            "brand": sale.car.brand,
            "customer_name": sale.customer_name,
            "selling_price": sale.selling_price,
            "profit": sale.selling_price - sale.car.buying_price,
            "date": sale.created_at
        })

    return Response({
        "staff": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "phone_number": request.user.phone_number
        },

        "cars_sold_today": today_sales.count(),
        "cars_sold_this_month": monthly_sales.count(),
        "total_cars_sold": sales.count(),

        "today_revenue": today_revenue,
        "monthly_revenue": monthly_revenue,
        "total_revenue": total_revenue,

        "today_profit": today_profit,
        "monthly_profit": monthly_profit,
        "total_profit": total_profit,

        "recent_sales": recent_sales
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ExportSalesCSV(request):

    # only admin can export reports
    if request.user.role != "admin":
        return Response(
            {"error": "Only admins can export reports"},
            status=403
        )

    # create the csv response
    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="sales_report.csv"'
    )

    writer = csv.writer(response)

    # CSV headings
    writer.writerow([
        "Sale ID",
        "VIN Number",
        "Car Brand",
        "Customer Name",
        "Customer Phone",
        "Buying Price",
        "Selling Price",
        "Profit",
        "Sold By",
        "Date"
    ])


    sales = Sale.objects.all().order_by("-created_at")


    for sale in sales:

        profit = sale.selling_price - sale.car.buying_price

        writer.writerow([
            sale.id,
            sale.car.vin_number,
            sale.car.brand,
            sale.customer_name,
            sale.customer_phone,
            sale.car.buying_price,
            sale.selling_price,
            profit,
            sale.sold_by.username if sale.sold_by else "N/A",
            sale.created_at.strftime("%Y-%m-%d")
        ])


    return response
