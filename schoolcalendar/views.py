from datetime import datetime

from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import SchoolCalendar


class SchoolCalendarListView(LoginRequiredMixin, ListView):
	model = SchoolCalendar

	def get_queryset(self):
		return SchoolCalendar.objects.filter(
			Q(startdatum__gte= datetime.now()) | Q(einddatum__gte= datetime.now()))
