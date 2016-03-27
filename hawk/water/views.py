from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse

import simplejson as json


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def alarm(request):
    return render(request, 'alarm.html')


@login_required
def cctv(request):
    return render(request, 'cctv.html')


@login_required
def live_pretreatment(request):
    return render(request, 'live-pretreatment.html')


@login_required
def live_osmosis(request):
    return render(request, 'live-osmosis.html')


@login_required
def live_product(request):
    return render(request, 'live-product.html')


@login_required
def live_reject(request):
    return render(request, 'live-reject.html')


@login_required
def live_energy(request):
    return render(request, 'live-energy.html')


@login_required
def report(request):
    return render(request, 'report.html')


@login_required
def trend(request):
    return render(request, 'trend.html')


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def notifications(request):
    return render(request, 'notification.html')



