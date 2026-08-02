from django.db import router
from django.urls import include, path
from .views import  AddSupplier, ToggleSupplierStatus, UpdateSupplier, ViewSuppliers
from rest_framework.routers import DefaultRouter
urlpatterns = [
    path('addsupplier/', AddSupplier),
    path('viewsuppliers/', ViewSuppliers),
    path('updatesupplier/<int:id>/', UpdateSupplier),
    path("suppliers/<int:id>/toggle-status/",ToggleSupplierStatus),
]

