from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse


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
def detail(request):
    return render(request, 'detail.html')


@login_required
def report(request):
    return render(request, 'report.html')


@login_required
def trend(request):
    return render(request, 'trend.html')
