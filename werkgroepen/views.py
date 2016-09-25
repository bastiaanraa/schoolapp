from django.shortcuts import render
from django.views.generic import ListView, DetailView

from werkgroepen.models import Werkgroep

class WerkgroepDetail(DetailView):
	model = Werkgroep

# Create your views here.
