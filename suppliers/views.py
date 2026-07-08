from django.shortcuts import render

# Create your views here.
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Supplier

# add supplier
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def AddSupplier(request):

    if request.user.role != "admin":
        return Response(
            {"error": "Only admins can add suppliers"},
            status=403
        )

    company_name = request.data.get("company_name")
    contact_person = request.data.get("contact_person")
    phone_number = request.data.get("phone_number")
    email = request.data.get("email")
    address = request.data.get("address")

    if not company_name or not contact_person or not phone_number or not email:
        return Response(
            {"error": "All required fields are required"},
            status=400
        )

    if Supplier.objects.filter(company_name=company_name).exists():
        return Response(
            {"error": "Supplier already exists"},
            status=400
        )

    try:
        supplier = Supplier.objects.create(
            company_name=company_name,
            contact_person=contact_person,
            phone_number=phone_number,
            email=email,
            address=address
        )

        return Response({
            "message": "Supplier added successfully",
            "supplier_id": supplier.id
        }, status=201)

    except IntegrityError as e:
        return Response({"error": str(e)}, status=400)


# get suppliers
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ViewSuppliers(request):
    if request.user.role != "admin":
        return Response(
            {"error": "Only admins can view suppliers"},
            status=403
        )


    suppliers = Supplier.objects.all()

    data = []

    for supplier in suppliers:
        data.append({
            "id": supplier.id,
            "company_name": supplier.company_name,
            "contact_person": supplier.contact_person,
            "phone_number": supplier.phone_number,
            "email": supplier.email,
            "address": supplier.address
        })

    return Response(data)

# update suppliers
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def UpdateSupplier(request, id):

    if request.user.role != "admin":
        return Response(
            {"error": "Only admins can update suppliers"},
            status=403
        )

    try:
        supplier = Supplier.objects.get(id=id)
    except Supplier.DoesNotExist:
        return Response(
            {"error": "Supplier not found"},
            status=404
        )

    company_name = request.data.get("company_name")
    contact_person = request.data.get("contact_person")
    phone_number = request.data.get("phone_number")
    email = request.data.get("email")
    address = request.data.get("address")

    if company_name:
        supplier.company_name = company_name
    if contact_person:
        supplier.contact_person = contact_person
    if phone_number:
        supplier.phone_number = phone_number
    if email:
        supplier.email = email
    if address:
        supplier.address = address

    try:
        supplier.save()
        return Response({
            "message": "Supplier updated successfully",
            "supplier_id": supplier.id
        }, status=200)

    except IntegrityError as e:
        return Response({"error": str(e)}, status=400)
