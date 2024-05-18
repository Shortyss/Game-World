from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model, CharField, DateField, IntegerField, ForeignKey, DO_NOTHING, ImageField


# Create your models here.


class Profile(Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = CharField(max_length=25, null=True, blank=True, verbose_name='Telefon')
    birthdate = DateField(null=True, blank=True, verbose_name='Datum narození')
    street = CharField(max_length=255, null=True, blank=True, verbose_name='Ulice')
    house_number = IntegerField(null=True, blank=True, verbose_name='Číslo domu')
    city = CharField(max_length=132, null=True, blank=True, verbose_name='Město')
    country = CharField(max_length=132, null=True, blank=True, verbose_name='Země')
    postal_code = CharField(max_length=20, null=True, blank=True, verbose_name='PSČ')


class UserImage(Model):
    user = ForeignKey(Profile, on_delete=DO_NOTHING)
    image = ImageField(upload_to='users_image/')
