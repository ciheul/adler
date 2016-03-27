from django.conf.urls import url, patterns, include

import views
# import api

urlpatterns = [
    # url(r'^alarm/$', views.alarm, name="alarm"),
    url(r'^$', views.dashboard, name="dashboard"),
    url(r'^overview-outgoing-1/$', views.electrical_overview_outgoing_1,
        name="electrical-overview-outgoing-1"),
    url(r'^overview-outgoing-2/$', views.electrical_overview_outgoing_2,
        name="electrical-overview-outgoing-2"),
    url(r'^sld-outgoing-1/$', views.electrical_sld_outgoing_1,
        name="sld-overview-outgoing-1"),
    url(r'^sld-outgoing-2/$', views.electrical_sld_outgoing_2,
        name="sld-overview-outgoing-2"),
]
