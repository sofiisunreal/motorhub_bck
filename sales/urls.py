from django.urls import path
from .views import SellCar, ViewSales, StaffDashboard, AdminDashboard, ExportSalesCSV
urlpatterns = [
    path('addsale/', SellCar),
    path('viewsales/', ViewSales),
    path('staffdashboard/', StaffDashboard),
    path('admindashboard/', AdminDashboard),
    path('exportsalescsv/', ExportSalesCSV),
]
