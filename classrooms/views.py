import datetime

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.flatpages.models import FlatPage
from django.db.models import Q

from classrooms.models import ClassRoom
from profile.models import Profile
from schoolcalendar.models import SchoolCalendar


class ClassRoomDetail(LoginRequiredMixin, DetailView):
	model = ClassRoom

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(ClassRoomDetail, self).get_context_data(**kwargs)
		
		context['students'] = Profile.objects.filter(is_leerling=True, klas=self.object).prefetch_related("parents").order_by('first_name')

		all_email = ''
		for student in context['students']:
			for parent in student.parents.all():
				if parent.email:
					all_email += parent.email+", "
		
		if self.object:
			for leerkracht in self.object.leerkracht.all():
				all_email += leerkracht.email + ", "

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

		# calendar items
		try:
			context['calendar'] = SchoolCalendar.objects.filter(
				Q(startdatum__gte= datetime.datetime.today()) & Q(startdatum__lte= datetime.datetime.today() + datetime.timedelta(days=14)))
		except Exception, e:
			raise e
		
		klasouders_email = ""
		klasouders_email_k = ""
		klasouders_email_l = ""
		klasouders_email_m = ""
		klasouders_email_b = ""
		klasouders = Profile.objects.filter(is_klasouder = True)
		for klasouder in klasouders:
			if klasouder.email:
				klasouders_email += klasouder.email + ", "
				for klas in klasouder.klas_ouder.all():
					if klas.klascode.startswith('K') or klas.klascode.startswith('P'):
						#kleuters
						klasouders_email_k += klasouder.email + ", "
					if klas.klascode.startswith('L'):
						#lager
						klasouders_email_l += klasouder.email + ", "
					if klas.klascode.startswith('1S') or klas.klascode.startswith('2S'):
						#middenbouw
						klasouders_email_m += klasouder.email + ", "
					if klas.klascode.startswith('3') or klas.klascode.startswith('4') or klas.klascode.startswith('5') or klas.klascode.startswith('6'):
						#bovenbouw
						klasouders_email_b += klasouder.email + ", "
		context['klasouders_email'] = klasouders_email
		context['klasouders_email_k'] = klasouders_email_k
		context['klasouders_email_l'] = klasouders_email_l
		context['klasouders_email_m'] = klasouders_email_m
		context['klasouders_email_b'] = klasouders_email_b

		return context
	