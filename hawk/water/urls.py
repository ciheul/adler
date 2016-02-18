from django.conf.urls import url, patterns, include

import views
import api


urlpatterns = [
    url(r'^alarm/$', views.alarm, name="alarm"),
    url(r'^cctv/$', views.cctv, name="cctv"),
    url(r'^live-pretreatment/$', views.live_pretreatment,
        name="live-pretreatment"),
    url(r'^live-osmosis/$', views.live_osmosis,
        name="live-osmosis"),
    url(r'^live-product/$', views.live_product,
        name="live-product"),
    url(r'^live-reject/$', views.live_reject,
        name="live-reject"),
    url(r'^live-energy/$', views.live_energy,
        name="live-energy"),
    url(r'^report/$', views.report, name="report"),
    url(r'^trend/$', views.trend, name="trend"),
    url(r'^$', views.dashboard, name="dashboard"),

    #url live api
    url(r'^api/live-pretreatment/$',api.live_pretreatment_api,
        name="live-pretreatment-api"),
    url(r'^api/live-osmosis/$',api.live_osmosis_api,name="live-osmosis-api"),
    url(r'^api/live-product/$',api.live_product_api,name="live-product-api"),
    url(r'^api/live-reject/$',api.live_reject_api,name="live-reject-api"),
    url(r'^api/live-energy/$',api.live_energy_api,name="live-energy-api"),

]
