from django.urls import path
from .views import  AddCar, UpdateCar, ViewCars, UpdateCarStatus

urlpatterns = [
    path('addcar/', AddCar),
    path('view_cars/<int:id>/', ViewCars),
    path('updatecar/<int:id>/',UpdateCar),
    path('<int:id>/status/', UpdateCarStatus),
]
