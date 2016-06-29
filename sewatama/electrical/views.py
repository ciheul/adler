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


@login_required
def genset_outgoing_1_unit_1(request):
    return render(request, 'genset-outgoing-1-unit-1.html')


@login_required
def genset_outgoing_1_unit_2(request):
    return render(request, 'genset-outgoing-1-unit-2.html')


@login_required
def genset_outgoing_1_unit_3(request):
    return render(request, 'genset-outgoing-1-unit-3.html')


@login_required
def genset_outgoing_1_unit_4(request):
    return render(request, 'genset-outgoing-1-unit-4.html')


@login_required
def genset_outgoing_2_unit_1(request):
    return render(request, 'genset-outgoing-2-unit-1.html')


@login_required
def genset_outgoing_2_unit_2(request):
    return render(request, 'genset-outgoing-2-unit-2.html')


@login_required
def genset_outgoing_2_unit_3(request):
    return render(request, 'genset-outgoing-2-unit-3.html')


@login_required
def genset_outgoing_2_unit_4(request):
    return render(request, 'genset-outgoing-2-unit-4.html')


@login_required
def trend_unit_1(request):
    return render(request, 'trend-unit-1.html')


@login_required
def trend_unit_2(request):
    return render(request, 'trend-unit-2.html')


@login_required
def trend_unit_3(request):
    return render(request, 'trend-unit-3.html')


@login_required
def trend_unit_4(request):
    return render(request, 'trend-unit-4.html')


@login_required
def report_sfc_outgoing(request):
    return render(request, 'report-sfc-outgoing.html')


@login_required
def report_dar(request):
    return render(request, 'report-dar.html')


@login_required
def alarm_summary(request):
    return render(request, 'alarm-summary.html')


@login_required
def alarm_history(request):
    return render(request, 'alarm-history.html')


@login_required
def alarm_event(request):
    return render(request, 'alarm-event.html')
