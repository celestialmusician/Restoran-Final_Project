from django.db import models
import uuid

from bookings.models import Booking  


class PaymentStatus(models.TextChoices):
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"
    PENDING = "PENDING", "Pending"


class Transaction(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4,editable=False,unique=True)

    booking = models.ForeignKey(Booking,on_delete=models.CASCADE,related_name="transactions")

    rzp_order_id = models.CharField(max_length=200)

    status = models.CharField(max_length=20,choices=PaymentStatus.choices,default=PaymentStatus.PENDING)

    amount = models.FloatField()

    rzp_payment_id = models.CharField(max_length=200,null=True,blank=True)

    rzp_payment_signature = models.TextField(null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.user.email} - ₹{self.amount}"

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]
