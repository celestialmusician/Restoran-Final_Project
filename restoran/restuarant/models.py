from django.db import models

import uuid

# Create your models here.

class BaseClass(models.Model):

    uuid=models.UUIDField(unique=True,default=uuid.uuid4)

    active_status=models.BooleanField(default=True)

    created_at= models.DateField(auto_now_add=True)

    updated_at=models.DateField(auto_now=True)

    class Meta:

        abstract=True


class CategoryChoices(models.TextChoices):

    VEG = 'Veg', 'Veg'

    NON_VEG = 'Non-Veg', 'Non-Veg'

    ALL = 'All', 'All'


class MenuItem(BaseClass):

    name = models.CharField(max_length=100)

    category = models.CharField(max_length=10,choices=CategoryChoices.choices)

    price = models.FloatField()

    description = models.TextField(blank=True)

    image = models.ImageField(upload_to='restuarant/banner-imges')

    is_available = models.BooleanField(default=True)

    class Meta:

        verbose_name = 'Menu Item'

        verbose_name_plural = 'Menu Items'

    def __str__(self):

        return self.name

