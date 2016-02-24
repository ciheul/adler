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

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import password_reset_confirm
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import View

import forms


class LoginView(View):
    def get(self, request):
        """If template does not load, add path into template loader in
           settings.py."""
        # ReactJS
        # return render(request, "static/account/reactapp/index.html")

        # BackboneJS
        return render(request, "static/account/backboneapp/index.html")
        
        '''
        if not request.user.is_authenticated(): 
            return render(request, "static/account/backboneapp/index.html")
        else 
            return render(request, "static/account/backboneapp/index.html")
        '''

class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse_lazy('login'))


# revert back to function-based
# TODO change to class-view-based and find out how the method can be called
# from urls.py
def reset_confirm(request, uidb64=None, token=None):
    print request.POST
    return password_reset_confirm(
        request,
        template_name='email/password_reset_confirm.html',
        uidb64=uidb64,
        token=token,
        set_password_form=forms.PasswordResetForm,
        post_reset_redirect=reverse('login'))
