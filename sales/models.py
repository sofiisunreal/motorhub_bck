from decimal import Decimal

from django.db import models

from cars.models import Car
from core.models import BaseModel, User
from django.db.models import Sum

# Create your models here.
class Sale(BaseModel):
    car = models.OneToOneField(
        Car,
        on_delete=models.PROTECT,
        related_name="sale"
    )

    sold_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sales"
    )

    customer_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    customer_phone = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    @property
    def amount_paid(self):
        return self.payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

    @property
    def balance(self):
        return self.selling_price - self.amount_paid

    @property
    def payment_status(self):
        if self.amount_paid >= self.selling_price:
            return "paid"

        return "partial"

    def __str__(self):
        return f"{self.car} - KES {self.selling_price}"

class Payment(BaseModel):
    PAYMENT_METHODS = (
        ("cash", "Cash"),
        ("bank", "Bank"),
    )

    sale = models.ForeignKey(
        Sale,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    reference = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="received_payments"
    )

    def __str__(self):
        return f"{self.sale} - KES {self.amount}"
