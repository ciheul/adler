"""
Requirements backend:
- login, logout, and sign up through API
- it consists of account and user whereas one account has at least one user
- a reusable app
- it can change how user logins either by username or email
- it can handle invalid combination of username/email or password
- after signing up, app sends email confirmation
- use django-oauth-toolkit
"""

"""
URL:
- http://django-oauth-toolkit.readthedocs.org/en/latest/rest-framework/getting_started.html#step-1-minimal-setup
- https://yeti.co/blog/oauth2-with-django-rest-framework/
- http://httplambda.com/a-rest-api-with-django-and-oauthw-authentication/
"""

import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

from rest_framework import permissions, status, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from celerymanager import celery_client
from serializers import LoginSerializer, UserSerializer, GroupSerializer


class LoginAPIView(APIView):
    serializer_class = LoginSerializer
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        # return user object when authenticated
        user = authenticate(username=request.data['username'],
                            password=request.data['password'])

        # if user is not authenticated, send http 401 unauthorized
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # login to the system
        login(request, user)

        # TODO check return value get and create. are they different?
        token = Token.objects.get_or_create(user=user)

        # generate response message
        data = {
            'success': 0,
            'token': token[0].key,
            'next': '/water/'
        }

        return Response(data=data, status=status.HTTP_201_CREATED)


class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        data = { 'success': 0, 'next': '/accounts/#/login' }

        # return http 201 created
        return Response(data=data, status=status.HTTP_201_CREATED)


class ProfileAPIView(APIView):
    def get(self, request):
        user = User.objects.get(username=request.user.username, is_active=True)
        data = {
            'user': {
                'username': user.username,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'email': user.email
            }
        }
        return Response(data=data, status=status.HTTP_200_OK)


class ForgotPasswordAPIView(APIView):
    def post(self, request):
        # validate empty email
        if not request.POST['email']:
            data = { 'success': -1, 'message': "Please input your email." }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        # TODO validate email format

        # validate email against database
        u = None
        try:
            u = User.objects.get(email__iexact=request.POST['email'],
                                 is_active=True)
        except User.DoesNotExist:
            data = { 'success': -1, 'message': "Your email is not registered." }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        # prepare important information to password_reset
        meta = {
            'email': request.POST['email'],
            'csrftoken': request.META['CSRF_COOKIE'],
            'server_name': request.META['REMOTE_ADDR'],
            'server_port': request.META['SERVER_PORT'],
        }

        # send task to celery
        celery_client.invoke_send_forgot_password_email(meta) 

        data = { 'success': 0 }
        return Response(data=data, status=status.HTTP_201_CREATED)


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    required_scopes = ['groups']
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
