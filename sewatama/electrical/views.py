from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse

import simplejson as json


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def electrical_overview_outgoing_1(request):
    return render(request, 'electrical-overview-outgoing-1.html')


@login_required
def electrical_overview_outgoing_2(request):
    return render(request, 'electrical-overview-outgoing-2.html')


@login_required
def electrical_sld_outgoing_1(request):
    return render(request, 'electrical-sld-outgoing-1.html')


@login_required
def electrical_sld_outgoing_2(request):
    return render(request, 'electrical-sld-outgoing-2.html')


@login_required
def genset_overview_outgoing_1(request):
    return render(request, 'genset-overview-outgoing-1.html')


@login_required
def genset_overview_outgoing_2(request):
    return render(request, 'genset-overview-outgoing-2.html')
