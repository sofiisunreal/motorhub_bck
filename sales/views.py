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
from sales.models import Sale,Payment
from suppliers.models import Supplier
import csv
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import Sum


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def SellCar(request):

    # Only staff can sell cars
    if request.user.role != "staff":
        return Response(
            {"error": "Only staff can sell cars"},
            status=403
        )

    car_id = request.data.get("car_id")
    customer_name = request.data.get("customer_name")
    customer_phone = request.data.get("customer_phone")
    selling_price = request.data.get("selling_price")

    # First payment
    initial_payment = request.data.get("initial_payment")
    payment_method = request.data.get("payment_method")
    payment_reference = request.data.get("payment_reference")
    payment_notes = request.data.get("payment_notes")

    notes = request.data.get("notes")

    # -------------------------
    # REQUIRED SALE FIELDS
    # -------------------------

    if not car_id or not customer_name or not customer_phone or not selling_price:
        return Response(
            {
                "error": "Car, customer name, phone and selling price are required"
            },
            status=400
        )

    # -------------------------
    # REQUIRED INITIAL PAYMENT
    # -------------------------

    if not initial_payment or not payment_method:
        return Response(
            {
                "error": "Initial payment and payment method are required"
            },
            status=400
        )

    # -------------------------
    # PAYMENT METHOD
    # -------------------------

    if payment_method not in ["cash", "bank"]:
        return Response(
            {
                "error": "Payment method must be cash or bank"
            },
            status=400
        )

    # -------------------------
    # CONVERT AMOUNTS
    # -------------------------

    try:
        selling_price = Decimal(str(selling_price))
        initial_payment = Decimal(str(initial_payment))

    except (InvalidOperation, ValueError):
        return Response(
            {
                "error": "Invalid selling price or payment amount"
            },
            status=400
        )

    # -------------------------
    # VALIDATE SELLING PRICE
    # -------------------------

    if selling_price <= 0:
        return Response(
            {
                "error": "Selling price must be greater than zero"
            },
            status=400
        )

    # -------------------------
    # VALIDATE INITIAL PAYMENT
    # -------------------------

    if initial_payment <= 0:
        return Response(
            {
                "error": "Payment amount must be greater than zero"
            },
            status=400
        )

    if initial_payment > selling_price:
        return Response(
            {
                "error": "Initial payment cannot exceed selling price"
            },
            status=400
        )

    # -------------------------
    # GET AND LOCK CAR
    # -------------------------

    try:
        car = Car.objects.select_for_update().get(
            vin_number=car_id
        )

    except Car.DoesNotExist:
        return Response(
            {
                "error": "Car does not exist"
            },
            status=404
        )

    # -------------------------
    # CHECK CAR STATUS
    # -------------------------

    if car.status != "available":
        return Response(
            {
                "error": "Car is not available for sale"
            },
            status=400
        )

    # -------------------------
    # MARK CAR AS SOLD
    # -------------------------

    car.status = "sold"

    car.save(
        update_fields=["status"]
    )

    # -------------------------
    # CREATE SALE
    # -------------------------

    sale = Sale.objects.create(
        car=car,
        sold_by=request.user,
        customer_name=customer_name,
        customer_phone=customer_phone,
        selling_price=selling_price,
        notes=notes
    )

    # -------------------------
    # CREATE FIRST PAYMENT
    # -------------------------

    payment = Payment.objects.create(
        sale=sale,
        amount=initial_payment,
        payment_method=payment_method,
        reference=payment_reference,
        notes=payment_notes,
        received_by=request.user
    )

    # -------------------------
    # CALCULATE PAYMENT DETAILS
    # -------------------------

    amount_paid = sale.amount_paid
    balance = sale.balance
    payment_status = sale.payment_status

    # -------------------------
    # RESPONSE
    # -------------------------

    return Response(
        {
            "message": "Car sold successfully",

            "sale": {
                "sale_id": sale.id,
                "vin_number": car.vin_number,

                "customer_name": sale.customer_name,
                "customer_phone": sale.customer_phone,

                "selling_price": sale.selling_price,

                "amount_paid": amount_paid,
                "balance": balance,
                "payment_status": payment_status,

                "payment": {
                    "id": payment.id,
                    "amount": payment.amount,
                    "method": payment.payment_method,
                    "reference": payment.reference,
                    "date": payment.created_at,
                },

                "sold_by": request.user.username,
            }
        },
        status=201
    )



@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def AddPayment(request, sale_id):

    if request.user.role != "staff":
        return Response(
            {"error": "Only staff can receive payments"},
            status=403
        )

    amount = request.data.get("amount")
    payment_method = request.data.get("payment_method")
    payment_reference = request.data.get("payment_reference")
    notes = request.data.get("notes")

    if not amount or not payment_method:
        return Response(
            {"error": "Amount and payment method are required"},
            status=400
        )

    if payment_method not in ["cash", "bank"]:
        return Response(
            {"error": "Payment method must be cash or bank"},
            status=400
        )

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        return Response(
            {"error": "Invalid payment amount"},
            status=400
        )

    if amount <= 0:
        return Response(
            {"error": "Payment must be greater than zero"},
            status=400
        )

    try:
        # Lock the sale while calculating balance
        sale = Sale.objects.select_for_update().get(
            id=sale_id
        )
    except Sale.DoesNotExist:
        return Response(
            {"error": "Sale does not exist"},
            status=404
        )

    # Calculate how much has already been paid
    amount_paid = sale.payments.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    balance = sale.selling_price - amount_paid

    if balance <= 0:
        return Response(
            {"error": "This sale has already been fully paid"},
            status=400
        )

    if amount > balance:
        return Response(
            {
                "error": "Payment exceeds remaining balance",
                "remaining_balance": balance
            },
            status=400
        )

    # Create payment
    payment = Payment.objects.create(
        sale=sale,
        amount=amount,
        payment_method=payment_method,
        reference=payment_reference,
        notes=notes,
        received_by=request.user
    )

    # New totals
    new_amount_paid = amount_paid + amount
    new_balance = sale.selling_price - new_amount_paid

    if new_balance == 0:
        payment_status = "paid"
    else:
        payment_status = "partial"

    return Response(
        {
            "message": "Payment recorded successfully",

            "payment": {
                "id": payment.id,
                "amount": payment.amount,
                "method": payment.payment_method,
                "reference": payment.reference,
                "date": payment.created_at,
            },

            "sale": {
                "sale_id": sale.id,
                "selling_price": sale.selling_price,
                "amount_paid": new_amount_paid,
                "balance": new_balance,
                "payment_status": payment_status,
            },

            "received_by": request.user.username,
        },
        status=201
    )

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

    month = request.query_params.get("month")
    year = request.query_params.get("year")

    if month and year:
        sales = sales.filter(
            created_at__month=month,
            created_at__year=year
        )

    customer = request.query_params.get("customer")

    if customer:
        sales = sales.filter(
            customer_name__icontains=customer
        )
    data = []
    for sale in sales:
        amount_paid = sale.payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        balance = sale.selling_price - amount_paid

        if balance == 0:
            payment_status = "paid"
        else:
            payment_status = "partial"

        profit = sale.selling_price - sale.car.buying_price
        payments = []
        for payment in sale.payments.all():
            payments.append({
                "id": payment.id,
                "amount": payment.amount,
                "method": payment.payment_method,
                "reference": payment.reference,
                "date": payment.created_at,
                "received_by": (
                    payment.received_by.username
                    if payment.received_by
                    else None
                ),
            })
        data.append({
            "sale_id": sale.id,
            "vin_number": sale.car.vin_number,
            "brand": sale.car.brand,
            "year": sale.car.year,
            "image": (
                request.build_absolute_uri(sale.car.image.url)
                if sale.car.image
                else None
            ),

            "customer_name": sale.customer_name,
            "customer_phone": sale.customer_phone,
            "selling_price": sale.selling_price,
            "buying_price": sale.car.buying_price,
            "profit": profit,
            "amount_paid": amount_paid,
            "balance": balance,
            "payment_status": payment_status,
            "payments": payments,
            "sold_by": (
                sale.sold_by.username
                if sale.sold_by
                else None
            ),
            "date": sale.created_at,
        })

    return Response(data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def UpdateSale(request, id):

    # Only admins can edit sales
    if request.user.role != "admin":
        return Response(
            {"error": "Only admins can edit sales"},
            status=403
        )

    # Get sale
    try:
        sale = Sale.objects.select_for_update().select_related("car").get(
            id=id
        )
    except Sale.DoesNotExist:
        return Response(
            {"error": "Sale does not exist"},
            status=404
        )
    customer_name = request.data.get("customer_name")
    customer_phone = request.data.get("customer_phone")
    selling_price = request.data.get("selling_price")
    vin_number = request.data.get("vin_number")
    notes = request.data.get("notes")

    if customer_name is not None:
        sale.customer_name = customer_name

    if customer_phone is not None:
        sale.customer_phone = customer_phone

    if notes is not None:
        sale.notes = notes

    if selling_price is not None:
        try:
            selling_price = Decimal(str(selling_price))
        except (InvalidOperation, ValueError):
            return Response(
                {"error": "Invalid selling price"},
                status=400
            )
        if selling_price <= 0:
            return Response(
                {"error": "Selling price must be greater than zero"},
                status=400
            )

        amount_paid = sale.amount_paid

        # Cannot reduce selling price below amount already received
        if selling_price < amount_paid:
            return Response(
                {
                    "error": (
                        "Selling price cannot be less than "
                        "the amount already paid"
                    ),
                    "amount_paid": amount_paid
                },
                status=400
            )

        sale.selling_price = selling_price

    if vin_number is not None and vin_number != sale.car.vin_number:

        # Check whether another car already has this VIN
        if Car.objects.filter(
            vin_number=vin_number
        ).exclude(
            id=sale.car.id
        ).exists():

            return Response(
                {
                    "error": "Another car already has this VIN number"
                },
                status=400
            )

        sale.car.vin_number = vin_number
        sale.car.save(update_fields=["vin_number"])

    # Save sale
    try:
        sale.save()
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=400
        )


    amount_paid = sale.amount_paid
    balance = sale.balance
    payment_status = sale.payment_status

    profit = sale.selling_price - sale.car.buying_price

    return Response(
        {
            "message": "Sale updated successfully",

            "sale": {
                "sale_id": sale.id,
                "vin_number": sale.car.vin_number,
                "brand": sale.car.brand,
                "year": sale.car.year,

                "image": (
                    request.build_absolute_uri(
                        sale.car.image.url
                    )
                    if sale.car.image
                    else None
                ),

                "customer_name": sale.customer_name,
                "customer_phone": sale.customer_phone,

                "selling_price": sale.selling_price,
                "buying_price": sale.car.buying_price,
                "profit": profit,

                "amount_paid": amount_paid,
                "balance": balance,
                "payment_status": payment_status,

                "sold_by": (
                    sale.sold_by.username
                    if sale.sold_by
                    else None
                ),

                "date": sale.created_at,
                "notes": sale.notes,
            }
        },
        status=200
    )
@api_view(["GET"])
@permission_classes([IsAdminUser])
def AdminDashboard(request):

    today = timezone.now().date()
    month_start = today.replace(day=1)

    # =========================
    # BASIC COUNTS
    # =========================

    total_staff = User.objects.filter(role="staff").count()
    total_suppliers = Supplier.objects.count()
    total_cars = Car.objects.count()

    available_cars = Car.objects.filter(
        status="available"
    ).count()

    reserved_cars = Car.objects.filter(
        status="reserved"
    ).count()

    sold_cars = Car.objects.filter(
        status="sold"
    ).count()

    # =========================
    # SALES PERIODS
    # =========================

    today_sales = Sale.objects.filter(
        created_at__date=today
    )

    monthly_sales = Sale.objects.filter(
        created_at__date__gte=month_start
    )

    all_sales = Sale.objects.all()

    # =========================
    # SALES VALUE
    # =========================

    today_sales_value = today_sales.aggregate(
        total=Sum("selling_price")
    )["total"] or Decimal("0.00")

    monthly_sales_value = monthly_sales.aggregate(
        total=Sum("selling_price")
    )["total"] or Decimal("0.00")

    total_sales_value = all_sales.aggregate(
        total=Sum("selling_price")
    )["total"] or Decimal("0.00")
# =========================
# MONEY COLLECTED
# =========================

    today_collected = Payment.objects.filter(
        payment_date__date=today
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")


    monthly_collected = Payment.objects.filter(
        payment_date__date__gte=month_start
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")


    total_collected = Payment.objects.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")
# =========================
    # OUTSTANDING BALANCE
    # =========================

    total_outstanding = (
        total_sales_value - total_collected
    )

    # =========================
    # PROFIT
    # =========================

    today_profit = today_sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or Decimal("0.00")

    monthly_profit = monthly_sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or Decimal("0.00")

    total_profit = all_sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or Decimal("0.00")

    # =========================
    # PAYMENT STATUS
    # =========================

    paid_sales = 0
    partial_sales = 0

    for sale in all_sales:
        if sale.payment_status == "paid":
            paid_sales += 1
        else:
            partial_sales += 1

    # =========================
    # STAFF PERFORMANCE
    # =========================

    staff_performance = []

    staff_members = User.objects.filter(
        role="staff"
    )

    for staff in staff_members:

        sales = Sale.objects.filter(
            sold_by=staff
        )

        revenue = sales.aggregate(
            total=Sum("selling_price")
        )["total"] or Decimal("0.00")

        profit = sales.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("selling_price") - F("car__buying_price"),
                    output_field=DecimalField()
                )
            )
        )["total"] or Decimal("0.00")

        staff_performance.append({
            "username": staff.username,
            "cars_sold": sales.count(),
            "sales_value": revenue,
            "profit": profit
        })

    # =========================
    # RECENT SALES
    # =========================

    recent_sales = []

    for sale in all_sales.select_related(
        "car",
        "sold_by"
    ).order_by("-created_at")[:5]:

        recent_sales.append({
            "sale_id": sale.id,
            "vin_number": sale.car.vin_number,
            "brand": sale.car.brand,
            "customer_name": sale.customer_name,
            "selling_price": sale.selling_price,
            "amount_paid": sale.amount_paid,
            "balance": sale.balance,
            "payment_status": sale.payment_status,
            "sold_by": (
                sale.sold_by.username
                if sale.sold_by
                else None
            ),
            "date": sale.created_at
        })

    return Response({

        # =========================
        # INVENTORY
        # =========================

        "total_staff": total_staff,
        "total_suppliers": total_suppliers,
        "total_cars": total_cars,

        "available_cars": available_cars,
        "reserved_cars": reserved_cars,
        "sold_cars": sold_cars,

        # =========================
        # SALES
        # =========================

        "cars_sold_today": today_sales.count(),
        "cars_sold_this_month": monthly_sales.count(),

        "today_sales_value": today_sales_value,
        "monthly_sales_value": monthly_sales_value,
        "total_sales_value": total_sales_value,

        # =========================
        # PAYMENTS
        # =========================

        "today_collected": today_collected,
        "monthly_collected": monthly_collected,
        "total_collected": total_collected,

        "total_outstanding": total_outstanding,

        # =========================
        # PAYMENT STATUS
        # =========================

        "paid_sales": paid_sales,
        "partial_sales": partial_sales,

        # =========================
        # PROFIT
        # =========================

        "today_profit": today_profit,
        "monthly_profit": monthly_profit,
        "total_profit": total_profit,

        # =========================
        # STAFF
        # =========================

        "staff_performance": staff_performance,

        # =========================
        # RECENT SALES
        # =========================

        "recent_sales": recent_sales
    })
# staff dashboard
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def StaffDashboard(request):

    if request.user.role != "staff":
        return Response(
            {"error": "Unauthorized"},
            status=403
        )

    today = timezone.now().date()
    month_start = today.replace(day=1)

    # =========================
    # STAFF SALES
    # =========================

    sales = Sale.objects.filter(
        sold_by=request.user
    )

    today_sales = sales.filter(
        created_at__date=today
    )

    monthly_sales = sales.filter(
        created_at__date__gte=month_start
    )

    # =========================
    # SALES VALUE
    # =========================

    today_sales_value = today_sales.aggregate(
        total=Sum("selling_price")
    )["total"] or Decimal("0.00")

    monthly_sales_value = monthly_sales.aggregate(
        total=Sum("selling_price")
    )["total"] or Decimal("0.00")

    total_sales_value = sales.aggregate(
        total=Sum("selling_price")
    )["total"] or Decimal("0.00")

    # =========================
    # MONEY COLLECTED
    # =========================

    today_collected = Payment.objects.filter(
        received_by=request.user,
        payment_date__date=today
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    monthly_collected = Payment.objects.filter(
        received_by=request.user,
        payment_date__date__gte=month_start
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    total_collected = Payment.objects.filter(
        received_by=request.user
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    # =========================
    # OUTSTANDING
    # =========================

    total_outstanding = (
        total_sales_value - total_collected
    )

    # =========================
    # PROFIT
    # =========================

    today_profit = today_sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or Decimal("0.00")

    monthly_profit = monthly_sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or Decimal("0.00")

    total_profit = sales.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("selling_price") - F("car__buying_price"),
                output_field=DecimalField()
            )
        )
    )["total"] or Decimal("0.00")

    # =========================
    # RECENT SALES
    # =========================

    recent_sales = []

    for sale in sales.select_related(
        "car"
    ).order_by("-created_at")[:5]:

        recent_sales.append({
            "sale_id": sale.id,
            "vin_number": sale.car.vin_number,
            "brand": sale.car.brand,
            "customer_name": sale.customer_name,
            "selling_price": sale.selling_price,
            "amount_paid": sale.amount_paid,
            "balance": sale.balance,
            "payment_status": sale.payment_status,
            "profit": (
                sale.selling_price -
                sale.car.buying_price
            ),
            "date": sale.created_at
        })

    return Response({

        "staff": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "phone_number": request.user.phone_number
        },

        # =========================
        # SALES
        # =========================

        "cars_sold_today": today_sales.count(),
        "cars_sold_this_month": monthly_sales.count(),
        "total_cars_sold": sales.count(),

        "today_sales_value": today_sales_value,
        "monthly_sales_value": monthly_sales_value,
        "total_sales_value": total_sales_value,

        # =========================
        # PAYMENTS
        # =========================

        "today_collected": today_collected,
        "monthly_collected": monthly_collected,
        "total_collected": total_collected,

        "total_outstanding": total_outstanding,

        # =========================
        # PROFIT
        # =========================

        "today_profit": today_profit,
        "monthly_profit": monthly_profit,
        "total_profit": total_profit,

        # =========================
        # RECENT SALES
        # =========================

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
