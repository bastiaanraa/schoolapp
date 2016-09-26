from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from bestuur.models import Bestuur

class BestuurDetail(LoginRequiredMixin, DetailView):
	model = Bestuur
