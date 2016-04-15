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

    url(r'^genset-outgoing-1-unit-1/$', views.genset_outgoing_1_unit_1,
        name="genset-outgoing-1-unit-1"),
    url(r'^genset-outgoing-1-unit-2/$', views.genset_outgoing_1_unit_2,
        name="genset-outgoing-1-unit-2"),
    url(r'^genset-outgoing-1-unit-3/$', views.genset_outgoing_1_unit_3,
        name="genset-outgoing-1-unit-3"),
    url(r'^genset-outgoing-1-unit-4/$', views.genset_outgoing_1_unit_4,
        name="genset-outgoing-1-unit-4"),

    url(r'^genset-outgoing-2-unit-1/$', views.genset_outgoing_2_unit_1,
        name="genset-outgoing-2-unit-1"),
    url(r'^genset-outgoing-2-unit-2/$', views.genset_outgoing_2_unit_2,
        name="genset-outgoing-2-unit-2"),
    url(r'^genset-outgoing-2-unit-3/$', views.genset_outgoing_2_unit_3,
        name="genset-outgoing-2-unit-3"),
    url(r'^genset-outgoing-2-unit-4/$', views.genset_outgoing_2_unit_4,
        name="genset-outgoing-2-unit-4"),

    url(r'^trend-unit-1/$', views.trend_unit_1, name="trend-unit-1"),
    url(r'^trend-unit-2/$', views.trend_unit_2, name="trend-unit-2"),
    url(r'^trend-unit-3/$', views.trend_unit_3, name="trend-unit-3"),
    url(r'^trend-unit-4/$', views.trend_unit_4, name="trend-unit-4"),
]
