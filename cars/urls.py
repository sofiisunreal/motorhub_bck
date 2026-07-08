from django.urls import path
from .views import  AddCar, ViewCars, UpdateCarStatus

urlpatterns = [
    path('addcar/', AddCar),
    path('view_cars/', ViewCars),
    path('<int:id>/status/', UpdateCarStatus),
]
