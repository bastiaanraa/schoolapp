from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.flatpages.models import FlatPage

from classrooms.models import ClassRoom
from profile.models import Profile


class ClassRoomDetail(LoginRequiredMixin, DetailView):
	model = ClassRoom

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(ClassRoomDetail, self).get_context_data(**kwargs)
		
		context['students'] = Profile.objects.filter(is_leerling=True, klas=self.object).prefetch_related("parents").order_by('first_name')
		#print self.object.klas_set.all() DIT MOET TOCH WERKEN???

		all_email = ''
		for student in context['students']:
			for parent in student.parents.all():
				if parent.email:
					all_email += parent.email+", "
		for leerkracht in self.object.leerkracht.all():
			all_email += leerkracht.email + ", "
		print all_email
		context['all_email'] = all_email
		
		return context

class MyClassRoom(ClassRoomDetail):
	model = ClassRoom
	
	myKlas = None

	def dispatch(self, request, *args, **kwargs):
		try:
			self.myKlas = self.request.user.parents.all()[0].klas
		except:
			pass
		return super(MyClassRoom, self).dispatch(request, *args, **kwargs)

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

	
	def get_context_data(self, *args, **kwargs):
		context = super(ClassRooms, self).get_context_data(*args, **kwargs)
		
		# add extra context
		try:
			context['tekst'] = FlatPage.objects.get(url='/') # get home page
		except Exception, e:
			raise e
		
		
		return context
	