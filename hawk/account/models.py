from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Organization(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Asset(models.Model):
    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=50, unique=True)
    lon = models.FloatField()
    lat = models.FloatField()


class HawkUser(AbstractBaseUser):
    username = models.CharField(_('username'), max_length=30, unique=True)
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    full_name = models.CharField(_('full name'), max_length=100)
    phone = models.CharField(_('phone number'), max_length=40, unique=True)
    organization = models.ForeignKey(Organization, null=True, blank=True)
    picture = models.ImageField()
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()
