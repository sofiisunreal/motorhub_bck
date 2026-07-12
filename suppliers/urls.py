from django.db import router
from django.urls import include, path
from .views import  AddSupplier, UpdateSupplier, ViewSuppliers
from rest_framework.routers import DefaultRouter
urlpatterns = [
    path('addsupplier/', AddSupplier),
    path('viewsuppliers/', ViewSuppliers),
    path('updatesupplier/<int:id>/', UpdateSupplier),
]

