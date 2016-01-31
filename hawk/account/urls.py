from django.conf.urls import url, patterns, include
from django.contrib import admin
admin.autodiscover()

from rest_framework import routers

import api, views

# Routers provide an easy way of automatically determining the URL conf
router = routers.DefaultRouter()
router.register(r'users', api.UserViewSet)
router.register(r'groups', api.GroupViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    # url(r'^login/', views.LoginView.as_view(), name='login'),
    # url(r'^logout/', views.LogoutView.as_view(), name='logout'),
    # url(r'^profile/', views.UserProfileView.as_view(), name='profile'),
    # url(r'^passwordresetdone/', 'django.contrib.auth.views.password_reset_done',
    #     name='password_reset_done'),

    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/login/', api.LoginAPIView.as_view(), name='api-login'),
    url(r'^api/logout/', api.LogoutAPIView.as_view(), name='api-logout'),
    url(r'^api/profile/', api.ProfileAPIView.as_view(), name='api-profile'),
    url(r'^api/forgotpassword/', api.ForgotPasswordAPIView.as_view(),
        name='api-forgotpassword'),

    url(r'^', views.LoginView.as_view(), name='login')
]
