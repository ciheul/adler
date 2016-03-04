from django.conf.urls import url, patterns, include
import views

urlpatterns = [
    url(r'^tags/', views.tagSettler, name="tags"),
]
