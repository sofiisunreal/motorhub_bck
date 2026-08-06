from django.urls import path
from .views import  AddCar, UpdateCar, ViewCars, UpdateCarStatus,ViewSingleCar

urlpatterns = [
    path('addcar/', AddCar),
    path('view_cars/<int:id>/', ViewCars),
    path('updatecar/<int:id>/',UpdateCar),
    path('<int:id>/status/', UpdateCarStatus),
    path('view_car/<int:id>/', ViewSingleCar)
]
