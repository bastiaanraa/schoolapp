
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User, Group

from apps.profile.models import Profile, ClassRoom

class ClassRoomDetail(DetailView):
	model = ClassRoom

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(ClassRoomDetail, self).get_context_data(**kwargs)
		context['students'] = Profile.objects.filter(is_leerling=True, klas=self.object).order_by('first_name')
		context['klassen'] = ClassRoom.objects.all()
		return context



class ProfileDetail(DetailView):
	model = Profile

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super(ProfileDetail, self).get_context_data(**kwargs)
		context['children'] = Profile.objects.filter(is_leerling=True, parents=self.object)
		return context
	