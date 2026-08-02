from django.urls import include, path

from suppliers.views import ToggleSupplierStatus
from .views import Logout, Profile, Register, Login, StaffViewSet, togglestaff_status
from rest_framework.routers import DefaultRouter
from .views import ChangePassword

router=DefaultRouter()
router.register('staff', StaffViewSet, basename='staff')

urlpatterns = [
    path('register/', Register),
    path('login/', Login),
    path('logout/', Logout),
    path('profile/', Profile),
    path("change-password/", ChangePassword),
    path("staff/<int:id>/toggle-status/",togglestaff_status),
    path("suppliers/<int:id>/toggle-status/",ToggleSupplierStatus),
    path('', include(router.urls)),
]
