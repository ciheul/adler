from django.conf.urls import url, patterns, include

import views


urlpatterns = [
    url(r'^alarm/$', views.alarm, name="alarm"),
    url(r'^cctv/$', views.cctv, name="cctv"),
    url(r'^live/$', views.live, name="live"),
    url(r'^report/$', views.report, name="report"),
    url(r'^trend/$', views.trend, name="trend"),
    url(r'^$', views.dashboard, name="dashboard"),
]
