from django.db import models

import uuid

from django.conf import settings


class BookingStatus(models.TextChoices):

    BOOKED = "BOOKED", "Booked"

    CANCELLED = "CANCELLED", "Cancelled"

    PAID = "PAID", "Paid"


class Booking(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)

    total_amount = models.FloatField()

    status = models.CharField(max_length=20, default="BOOKED")

    is_paid = models.BooleanField(default=False)  

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):

        return f"Booking {self.uuid} - {self.user}"
