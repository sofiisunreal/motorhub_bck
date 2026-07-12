from django.urls import path
from .views import SellCar, ViewSales
urlpatterns = [
    path('addsale/', SellCar),
    path('viewsales/', ViewSales),
]
