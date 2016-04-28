from django.shortcuts import render


from django.shortcuts import render_to_response
from django.template import RequestContext
from django import template
from django.template.loader import get_template 
from django.http import HttpResponseRedirect
from django.http import HttpResponse

# Create your views here.
# Create your views here.

def index(request):
    context= {'ha':'bow before the robot army'}
    return render(request, 'robots.html', context)

def new(request):
    return HttpResponse('wher new')