from django.db import models

from cars.models import Car
from core.models import BaseModel, User

# Create your models here.
class Sale(BaseModel):
    car = models.OneToOneField(Car,on_delete=models.PROTECT,related_name='sale')

    sold_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='sales')

    sale_price = models.DecimalField(max_digits=12,decimal_places=2)

    notes = models.TextField(blank=True,null=True)

    def __str__(self):
        return f"{self.car} - KES {self.sale_price}"
