from django.conf.urls import url, patterns, include
import views
import api

urlpatterns = [
    url(r'^tags/', views.tagSettler, name="tags"),
    url(r'^api/tags/$', api.tags_api, name="tags-api"),
]
