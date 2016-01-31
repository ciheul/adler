from django.conf.urls import url, patterns, include

import views


urlpatterns = [
    url(r'^', views.index),
]
