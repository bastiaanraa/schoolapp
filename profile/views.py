import operator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout as auth_logout
from django.contrib import messages

from profile.models import Profile
from profile.forms import SendPasswordForm


class ProfileDetail(LoginRequiredMixin, DetailView):
	model = Profile

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(ProfileDetail, self).get_context_data(**kwargs)
		if self.object.is_ouder:	
			context['children'] = Profile.objects.filter(is_active=True,is_leerling=True, parents=self.object).prefetch_related("parents")
		
			# zelfde adres voor partner
			try:
				context['partner'] = Profile.objects.filter( \
				adres=self.object.adres, \
				postcode=self.object.postcode,
				is_ouder=True, overleden=False
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


class MedewerkersListView(LoginRequiredMixin, ListView):
	model = Profile
	template_name = "profile/medewerkers_list.html"

	def get_queryset(self):
		return Profile.objects.filter(is_medewerker = True)

	def get_context_data(self, *args, **kwargs):
		context = super(MedewerkersListView, self).get_context_data(**kwargs)

		all_email = ''
		for p in Profile.objects.filter(is_medewerker = True):
			if p.email:
				all_email += p.email+", "
		context['all_email'] = all_email

		leerkrachten_email = ''
		for p in Profile.objects.filter(is_leerkracht = True):
			if p.email:
				leerkrachten_email += p.email+", "
		context['leerkrachten_email'] = leerkrachten_email

		BS_email = ''
		for p in Profile.objects.filter(is_leerkracht = True, doelgroep__contains='BS'):
			if p.email:
				BS_email += p.email+", "
		context['BS_email'] = BS_email

		MS_email = ''
		for p in Profile.objects.filter(is_leerkracht = True, doelgroep__contains='MS'):
			if p.email:
				MS_email += p.email+", "
		context['MS_email'] = MS_email

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

		return result.filter(is_active=True,is_superuser=False, overleden=False)

class LogoutView(RedirectView):
	"""
	Provides users the ability to logout
	"""
	url = '/'

	def get(self, request, *args, **kwargs):
		auth_logout(request)
		return super(LogoutView, self).get(request, *args, **kwargs)


from django.contrib.messages.views import SuccessMessageMixin
class SendPasswordView(SuccessMessageMixin, FormView):
    template_name = 'sendpasswordform.html'
    form_class = SendPasswordForm
    success_url = '/'
    success_message = "E-mail met login gegevens is verstuurd."

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email(form.cleaned_data.get('email'), self.request)
        return super(SendPasswordView, self).form_valid(form)
