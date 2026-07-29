from django.urls import include, path
from .views import Logout, Profile, Register, Login, StaffViewSet
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
    path('', include(router.urls)),
]
