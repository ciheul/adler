from django.conf.urls import url, patterns, include

import views
import api

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

    url(r'^report-sfc-outgoing/$', views.report_sfc_outgoing, name="report-sfc-outgoing"),

    ##### API #####
    url(r'^api/overview-outgoing-1/$', api.electrical_overview_outgoing_1,
        name="electrical-overview-outgoing-1-api"),
    url(r'^api/sld-outgoing-1/$', api.electrical_sld_outgoing_1,
        name="electrical-sld-outgoing-1-api"),
    url(r'^api/genset-overview-outgoing-1/$', api.genset_overview_outgoing_1,
        name="genset-overview-outgoing-1-api"),

    url(r'^api/genset-outgoing-1-unit-1/$', api.genset_outgoing_1_unit_1,
        name="genset-outgoing-1-unit-1-api"),
    url(r'^api/genset-outgoing-1-unit-2/$', api.genset_outgoing_1_unit_2,
        name="genset-outgoing-1-unit-2-api"),
    url(r'^api/genset-outgoing-1-unit-3/$', api.genset_outgoing_1_unit_3,
        name="genset-outgoing-1-unit-3-api"),
    url(r'^api/genset-outgoing-1-unit-4/$', api.genset_outgoing_1_unit_4,
        name="genset-outgoing-1-unit-4-api"),

    url(r'^api/trend-unit-1/$', api.trend_unit_1, name="trend-unit-1-api"),
    url(r'^api/trend-unit-2/$', api.trend_unit_2, name="trend-unit-2-api"),
    url(r'^api/trend-unit-3/$', api.trend_unit_3, name="trend-unit-3-api"),
    url(r'^api/trend-unit-4/$', api.trend_unit_4, name="trend-unit-4-api"),

    # historical trend
    url(r'^api/historical-trend/$', api.get_historical_trend,
        name="historical-trend-api"),

    # real time trend
    url(r'^api/trend-unit-1/cylinder-exhause-temperature/$', api.trend_unit_chart),
    # url(r'^api/(?P<trend-unit>\d+)/(?P<chart>\d+)/$', api.trend_unit_chart),

    url(r'^api/report-sfc-outgoing/$', api.report_sfc_outgoing, name="report-sfc-outgoing-api"),

    url(r'^api/filebrowser/$', api.file_browser_get_directory, name="filebrowser-api"),
    url(r'^api/filebrowser/download/$', api.file_browser_download, name="filebrowser-api"),

    url(r'^api/latest/$', api.latest, name="latest"),

    url(r'^download/trend/$', api.download_trend_csv, name="csv-trend"),
]
