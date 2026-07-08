from django.urls import path
from .views import  AddSupplier, UpdateSupplier, ViewSuppliers

urlpatterns = [
    path('addsupplier/', AddSupplier),
    path('viewsuppliers/', ViewSuppliers),
    path('updatesupplier/<int:id>/', UpdateSupplier),
]

