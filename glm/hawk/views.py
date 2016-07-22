from django.http import HttpResponse                                               
                                                                                   
def index(request):                                                                
    return HttpResponse('<br /><a href=\"accounts/\"><h1>INetSCADA</h1></a>')

