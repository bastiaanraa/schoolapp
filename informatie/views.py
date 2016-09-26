from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from informatie.models import Informatie

class InformatieDetail(LoginRequiredMixin, DetailView):
	model = Informatie

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(InformatieDetail, self).get_context_data(**kwargs)
		context['infodocumenten'] = Informatie.objects.all()
		return context
