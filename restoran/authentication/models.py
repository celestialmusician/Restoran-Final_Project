from django.db import models

from django.contrib.auth.models import AbstractUser

from restuarant.models import BaseClass

# Create your models here.

class RoleChoices(models.TextChoices):

    USER='User','User'

    ADMIN='Admin','Admin'


class Profile(AbstractUser):

    role=models.CharField(max_length=10,choices=RoleChoices.choices)

    phone=models.CharField(max_length=13,null=True,blank=True)
    
    email_verified = models.BooleanField(default=False) 

    phone_verified = models.BooleanField(default=False)

    class Meta:

        verbose_name='Profile'

        verbose_name_plural='Profiles'

    def __str__(self):

        return f'{self.username}'
    
class OTP(BaseClass):

    profile = models.OneToOneField('Profile', on_delete=models.CASCADE)

    otp = models.CharField(max_length=4, null=True, blank=True)

    email_otp = models.CharField(max_length=4, null=True, blank=True)

    email_otp_verified = models.BooleanField(default=False)

    phone_otp = models.CharField(max_length=6, null=True, blank=True)

    class Meta:
        verbose_name = 'OTP'

        verbose_name_plural = 'OTPs'

    def __str__(self):

        return f'{self.profile} otp'
    
class TableSeat(models.Model):

    seat_number = models.CharField(max_length=10, unique=True)

    is_booked = models.BooleanField(default=False)

    def __str__(self):
        
        return self.seat_number


    
    
                           



