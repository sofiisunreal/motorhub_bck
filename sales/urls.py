from django.urls import path
from .views import SellCar, UpdateSale, ViewSales, StaffDashboard, AdminDashboard, ExportSalesCSV, AddPayment
urlpatterns = [
    path('addsale/', SellCar),
    path('viewsales/', ViewSales),
    path('staffdashboard/', StaffDashboard),
    path('admindashboard/', AdminDashboard),
    path('exportsalescsv/', ExportSalesCSV),
    path('update-sale/<int:id>/', UpdateSale),
    path('addpayment/<int:sale_id>/', AddPayment)
]
