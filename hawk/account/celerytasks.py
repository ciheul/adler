# script to use django configuration when using django as external library
# otherwise, use:
# from django.conf import settings; settings.configure()
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dago.settings')
import django; django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.views import password_reset
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from celery import Celery


app = Celery('tasks', broker='amqp://guest@localhost//')

@app.task
def send_forgot_password_email(meta):
    csrftoken = meta['csrftoken']

    request = HttpRequest()

    request.COOKIES = { 'csrftoken': csrftoken }
    request.META['CSRF_COOKIE'] = csrftoken
    request.META['HTTP_X_CSRFTOKEN'] = csrftoken
    request.META['HTTP_COOKIE'] = 'csrftoken=' + csrftoken

    request.META['SERVER_NAME'] = meta['server_name']
    request.META['SERVER_PORT'] = meta['server_port']

    request.method = 'POST'
    request.POST = { 'email': meta['email'] }
    
    status = password_reset(
        request,
        email_template_name='email/password_reset_email.html',
        subject_template_name='email/password_reset_email_subject.txt',
            post_reset_redirect=reverse('login')
    )

    if type(status) != HttpResponseRedirect:
        return False

    return True
