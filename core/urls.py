from django.urls import path
from .views import Register, Login

urlpatterns = [
    path('register/', Register),
    path('login/', Login),
]
