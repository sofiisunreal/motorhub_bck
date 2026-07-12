from django.db import models
from suppliers.models import Supplier
from core.models import BaseModel

# Create your models here.


# car model
class Car(BaseModel):
    supplier = models.ForeignKey(Supplier,on_delete=models.PROTECT,related_name='cars')

    brand = models.CharField(max_length=100)
    year = models.PositiveIntegerField()

    vin_number = models.CharField(max_length=100,unique=True)

    buying_price = models.DecimalField(max_digits=12,decimal_places=2)
    STATUS_CHOICES = (
    ('available', 'Available'),
    ('reserved', 'Reserved'),
    ('sold', 'Sold'),
    )

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='available')

    image = models.ImageField(upload_to='cars/',null=True,blank=True)

    def __str__(self):
        return f"{self.brand} ({self.year}) ({self.vin_number})"
