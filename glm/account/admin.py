from django.contrib import admin

from .models import HawkUser, Organization


admin.site.register(HawkUser)
admin.site.register(Organization)
