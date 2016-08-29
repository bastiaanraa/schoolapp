import operator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.profile.models import Profile, ClassRoom

class ClassRoomDetail(LoginRequiredMixin, DetailView):
	model = ClassRoom

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(ClassRoomDetail, self).get_context_data(**kwargs)
		context['students'] = Profile.objects.filter(is_leerling=True, klas=self.object).order_by('first_name')
		context["klasouders"] = Profile.objects.filter(is_klasouder=True, klas_ouder=self.object)
		context['klassen'] = ClassRoom.objects.all() #hier een context variabele van maken context_processor?
		return context


class ProfileDetail(LoginRequiredMixin, DetailView):
	model = Profile

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(ProfileDetail, self).get_context_data(**kwargs)
		if self.object.is_ouder:	
			context['children'] = Profile.objects.filter(is_leerling=True, parents=self.object)
		
			# zelfde adres! voor partner!
			#context['partner'] = Profile.objects.filter( \
			#	adres=self.object.adres, \
			#	postcode=self.objects.postcode,
			#	)
		return context

class MyClassRooms(LoginRequiredMixin, ListView):
	model = ClassRoom
	template_name = "profile/classroom_detail.html"

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(MyClassRooms, self).get_context_data(**kwargs)
		context['klassen'] = ClassRoom.objects.all()
		return context

def get_queryset(self):
	"""
	Return the list of items for this view.
	The return value must be an iterable and may be an instance of
	`QuerySet` in which case `QuerySet` specific behavior will be enabled.
	"""
	queryset = ClassRoom.objects.filter(self.request.user.klas)
	return queryset

class Search(LoginRequiredMixin, ListView):

	model = Profile

	def get_queryset(self):
		result = super(Search, self).get_queryset()
		query = self.request.GET.get('q')
		if query:
			query_list = query.split()
			result = result.filter(
				reduce(operator.and_,
					   (Q(first_name__icontains=q) for q in query_list)) |
				reduce(operator.and_,
					   (Q(last_name__icontains=q) for q in query_list)) |
				reduce(operator.and_,
					   (Q(username__icontains=q) for q in query_list))
			)

		return result