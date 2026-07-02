from django.db import models

from core.models import BaseModel

# Create your models here.
# supplier model
class Supplier(BaseModel):
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.company_name



# car model
class Car(BaseModel):
    supplier = models.ForeignKey(Supplier,on_delete=models.PROTECT,related_name='cars')

    brand = models.CharField(max_length=100)
    year = models.PositiveIntegerField()

    vin_number = models.CharField(max_length=100,unique=True)

    price = models.DecimalField(max_digits=12,decimal_places=2)
    STATUS_CHOICES = (
    ('available', 'Available'),
    ('reserved', 'Reserved'),
    ('sold', 'Sold'),
    )

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='available')

    image = models.ImageField(upload_to='cars/',null=True,blank=True)

    def __str__(self):
        return f"{self.brand} ({self.year}) ({self.vin_number})"
