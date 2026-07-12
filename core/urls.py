from django.urls import include, path
from .views import Logout, Profile, Register, Login, StaffViewSet
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('staff', StaffViewSet, basename='staff')

urlpatterns = [
    path('register/', Register),
    path('login/', Login),
    path('logout/', Logout),
    path('profile/', Profile),
    path('', include(router.urls)),
]
