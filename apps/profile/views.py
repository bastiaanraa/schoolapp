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
		#print self.object.klas_set.all() DIT MOET TOCH WERKEN???
		
		context['klassen'] = ClassRoom.objects.all() #hier een context variabele van maken context_processor?
		return context


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

class MyClassRoom(LoginRequiredMixin, DetailView):
	model = ClassRoom
	template_name = "profile/classroom_detail.html"

	myKlas = None

	def dispatch(self, request, *args, **kwargs):
		try:
			self.myKlas = self.request.user.parents.all()[0].klas
		except:
			pass
		return super(MyClassRoom, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(MyClassRoom, self).get_context_data(*args, **kwargs)
		context['klassen'] = ClassRoom.objects.all()
		context['students'] = Profile.objects.filter(is_leerling=True, klas=self.myKlas).order_by('first_name')
		context["klasouders"] = Profile.objects.filter(is_klasouder=True, klas_ouder=self.myKlas)
		return context

	def get_object(self):
		"""
		Return the list of items for this view.
		The return value must be an iterable and may be an instance of
		`QuerySet` in which case `QuerySet` specific behavior will be enabled.
		"""

		try:
			object = ClassRoom.objects.get(klasnaam=self.myKlas)
		except:
			object = None
		return object

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

class ClassRooms(LoginRequiredMixin, ListView):
	model = ClassRoom

	"""
	def get_context_data(self, *args, **kwargs):
		context = super(ClassRooms, self).get_context_data(*args, **kwargs)
		# add extra context
		retrun context
	"""