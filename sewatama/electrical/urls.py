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
        name="electrical-sld-outgoing-1"),
    url(r'^sld-outgoing-2/$', views.electrical_sld_outgoing_2,
        name="electrical-sld-outgoing-2"),

    url(r'^genset-overview-outgoing-1/$', views.genset_overview_outgoing_1,
        name="genset-overview-outgoing-1"),
    url(r'^genset-overview-outgoing-2/$', views.genset_overview_outgoing_2,
        name="genset-overview-outgoing-2"),
]
