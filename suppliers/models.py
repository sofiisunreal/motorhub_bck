from django.db import models
from core.models import BaseModel

# Create your models here.

class Supplier(BaseModel):
    company_name = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    address = models.TextField()

    def __str__(self):
        return self.company_name
