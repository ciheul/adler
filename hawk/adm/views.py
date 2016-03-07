from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

@staff_member_required
def tagSettler(request):
    return render(request, 'tags.html')
