from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from classrooms.models import ClassRoom
from profile.models import Profile


class ClassRoomDetail(LoginRequiredMixin, DetailView):
	model = ClassRoom

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(ClassRoomDetail, self).get_context_data(**kwargs)
		
		context['students'] = Profile.objects.filter(is_leerling=True, klas=self.object).order_by('first_name')
		#print self.object.klas_set.all() DIT MOET TOCH WERKEN???
		
		context['klassen'] = ClassRoom.objects.all() #hier een context variabele van maken context_processor?
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

class ClassRooms(LoginRequiredMixin, ListView):
	model = ClassRoom

	"""
	def get_context_data(self, *args, **kwargs):
		context = super(ClassRooms, self).get_context_data(*args, **kwargs)
		# add extra context
		retrun context
	"""