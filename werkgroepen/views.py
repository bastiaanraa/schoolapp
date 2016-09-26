from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from werkgroepen.models import Werkgroep

class WerkgroepDetail(LoginRequiredMixin, DetailView):
	model = Werkgroep

# Create your views here.
