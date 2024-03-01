from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def incoming_sms(request):
    # Process incoming SMS message here
    return HttpResponse(status=200)