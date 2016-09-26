from django.shortcuts import render
from django.views.generic import ListView, DetailView

from bestuur.models import Bestuur

class BestuurDetail(DetailView):
	model = Bestuur
