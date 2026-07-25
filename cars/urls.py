from django.urls import path
from .views import  AddCar, UpdateCar, ViewCars, UpdateCarStatus

urlpatterns = [
    path('addcar/', AddCar),
    path('view_cars/', ViewCars),
    path('updatecar/',UpdateCar),
    path('<int:id>/status/', UpdateCarStatus),
]
