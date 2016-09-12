import operator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from profile.models import Profile


class ProfileDetail(LoginRequiredMixin, DetailView):
	model = Profile

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(ProfileDetail, self).get_context_data(**kwargs)
		if self.object.is_ouder:	
			context['children'] = Profile.objects.filter(is_leerling=True, parents=self.object)
		
			# zelfde adres voor partner
			try:
				context['partner'] = Profile.objects.filter( \
				adres=self.object.adres, \
				postcode=self.object.postcode,
				is_ouder=True
				).exclude(pk=self.object.pk)[0]
			except Exception, e:
				pass

		elif self.object.is_leerling:
			# zelfde adres voor siblings
			try:
				context['siblings'] = Profile.objects.filter( \
				adres=self.object.adres, \
				postcode=self.object.postcode,
				is_leerling=True
				).exclude(pk=self.object.pk)
			except Exception, e:
				print e
				pass
			
		return context



class Search(LoginRequiredMixin, ListView):

	model = Profile

	def get_context_data(self, *args, **kwargs):
		context = super(Search, self).get_context_data(*args, **kwargs)
		context['searchterm'] = self.request.GET.get('q')
		return context

	def get_queryset(self):
		result = Profile.objects.none()
		query = self.request.GET.get('q')
		if query:
			query_list = query.split()
			result = Profile.objects.filter(
				reduce(operator.and_,
					   (Q(first_name__icontains=q) for q in query_list)) |
				reduce(operator.and_,
					   (Q(last_name__icontains=q) for q in query_list)) |
				reduce(operator.and_,
					   (Q(username__icontains=q) for q in query_list))
			)

		return result.filter(is_superuser=False)

