from django.urls import path
from .views import Logout, Profile, Register, Login

urlpatterns = [
    path('register/', Register),
    path('login/', Login),
    path('logout/', Logout),
    path('profile/', Profile),
]
