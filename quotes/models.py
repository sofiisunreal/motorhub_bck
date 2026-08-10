from django.db import models
from cars.models import Car
# Create your models here.

class Quote(models.Model):
    STATUS_CHOICES=[
       ( 'NEW','New'),
       ('CONTACTED',"Contacted"),
       ('CLOSED','Closed')
    ]
    car=models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='quotes'
    )
    customer_name=models.CharField(max_length=100)
    customer_phone=models.CharField(max_length=20)
    customer_email=models.EmailField()
    message=models.TextField(blank=True)
    status=models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW'
    )
    created_at=models.DateTimeField(auto_now_add=True)

    def  __str__(self):
        return f"{self.customer_name}- {self.car}"
