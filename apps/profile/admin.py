#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.db import transaction, IntegrityError

from django.utils import encoding

from import_export import resources, fields, widgets
from import_export.admin import ImportMixin

from apps.profile.models import Profile, ClassRoom

import logging
logger = logging.getLogger("schoolapp")

			
class ProfileResource(resources.ModelResource):
	student_exists = False
	# rename regular attributes
	username = fields.Field(attribute='username')
	first_name = fields.Field(attribute='first_name', column_name='Voornaam')
	last_name = fields.Field(attribute='last_name', column_name='Naam')
	nickname = fields.Field(attribute='nickname', column_name='Nickname')
	geboortedatum = fields.Field(attribute='geboortedatum', column_name='Geboortedatum', widget=widgets.DateWidget('%d.%m.%Y'))
	
	aanspreektitel = fields.Field(attribute='aanspreektitel', column_name='Aanspreektitel (Aanschrijf)')
	parent1 = fields.Field(attribute="parent1", column_name="Vader")
	parent2 = fields.Field(attribute="parent2", column_name="Moeder")
	address = fields.Field(attribute="address",column_name='Aanschrijfadres')
	postcode = fields.Field(attribute='postcode', column_name='Hoofdpostnr (Aanschrijf)')
	gemeente = fields.Field(attribute='gemeente', column_name='Deelgemeente (Aanschrijf)')
	parent1_email = fields.Field(attribute="parent1_email", column_name="E-mail vader")
	parent2_email = fields.Field(attribute="parent2_email", column_name="E-mail moeder")
	 
	parent_gescheiden = fields.Field(attribute='parent_name', column_name='Aanspreeknaam (Aanschrijf)')
	
	klas = fields.Field(attribute="klas", column_name="Klascode", widget=widgets.ForeignKeyWidget(ClassRoom, 'klascode'))
	

	class Meta:
		model = Profile
		import_id_fields = ('nickname',)
		fields = ('nickname','last_name','first_name', 'username', 'geboortedatum', \
			'postcode', 'gescheiden', 'klas')
		skip_unchanged = True
		report_skipped = True


	def dehydrate_first_name(self, user):
		#print user
		return user.first_name
		#return user.first_name.encode('utf-8')

	def dehydrate_username(self, profile):
		# DIT DOET NIETS?
		return profile.first_name+profile.last_name

	def dehydrate_gescheiden(self, profile):
		if profile.aanspreektitel == "Aan":
			return True
		return False

	def save_instance(self, instance, dry_run=False):
		"""
		Takes care of saving the object to the database.
		Keep in mind that this is done by calling ``instance.save()``, so
		objects are not created in bulk!
		"""
		self.before_save_instance(instance, dry_run)
		if not dry_run:
			self.student_exists = False
			try:
				with transaction.atomic():
					instance.save()
			except IntegrityError, e:
				#IntegrityError: (1062, "Duplicate entry 'zzz' for key 'username'")
				print "save instance: integrity error"
				print(e)
				self.student_exists = True
			except Exception, e:
				print "nog een andere fout"
				print e
		self.after_save_instance(instance, dry_run)

	def before_save_instance(self, instance, dry_run):
		print 'before_save'
		#instance.first_name = instance.first_name.encode('utf-8')
		instance.username = instance.first_name+instance.last_name
		instance.is_leerling = True
		if instance.aanspreektitel == "Aan":
			instance.gescheiden = True
		

	def after_save_instance(self, instance, dry_run):
		print 'after_save'
		
		if dry_run == False:
			password = make_password('123')
			child = Profile.objects.get(username=instance.username)
			
			if instance.gescheiden:
				try:
					with transaction.atomic():
						parent = Profile(username=instance.parent_name, 
								password=password,
								first_name=instance.parent_name, 
								is_ouder=True,
								adres=instance.address,
								gemeente=instance.gemeente,
								postcode=instance.postcode,
								)
						parent.save()
				except IntegrityError, e:
					parent = Profile.objects.get(username=instance.parent_name)
				except Exception, e:
					print "except A"
					raise e
				
				try:
					child.parents.add(parent)
				except Exception, e:
					print "except B"
					raise e
			else:
				try:
					
					if not instance.parent1 == '':
						try:
							parent1 = Profile(
								username=instance.parent1,
								password=password,
								first_name=instance.parent1, 
								is_ouder=True,
								adres=instance.address,
								gemeente=instance.gemeente,
								postcode=instance.postcode,
								)
							with transaction.atomic():
								parent1.save()
						except Exception, e:
							parent1 = Profile.objects.get(username=instance.parent1)
							#raise e
						with transaction.atomic():
							child.parents.add(parent1)
					if not instance.parent2 == '':
						try:
							parent2 = Profile(
								username=instance.parent2,
								password=password,
								first_name=instance.parent2, 
								is_ouder=True,
								adres=instance.address,
								gemeente=instance.gemeente,
								postcode=instance.postcode,
								)
							with transaction.atomic():
								parent2.save()
						except Exception, e:
							parent2 = Profile.objects.get(username=instance.parent2)
							#raise e
						with transaction.atomic():
							child.parents.add(parent2)
				except Exception, e:
					print "except C"
					print e
		

# Define a new User admin
class UserAdmin(ImportMixin, BaseUserAdmin):
	resource_class = ProfileResource
	#inlines = (ProfileInline, )

	list_display = ['first_name', 'last_name', 'is_ouder', 'is_leerling', 'klas']
	fieldsets = (
		(None, {'fields': ('username','first_name', 'last_name','email', 'password')}),
		('Rollen', {'fields': ('is_leerling', 'is_ouder', 'is_klasouder', 'is_leerkracht', 'is_medewerker')}),
		('Personal info', {'fields': ('geboortedatum','adres','postcode', 'gemeente', 'telefoon', 'gsm', 'email')}),
		('Gezin', {'fields': ('gescheiden','parents',)}),
		('Klas', {'fields': ('klas',)}),
		('Klasouder', {'fields': ('klas_ouder',)}),
		('Permissions', {'fields': ('is_superuser',)}),
	)
	filter_horizontal = ('parents',)

	def formfield_for_manytomany(self, db_field, request, **kwargs):
		# enkel tonen bij leerlingen?

		#enkel ouders in lijst_
		if db_field.name == "parents":
			kwargs["queryset"] = Profile.objects.filter(is_ouder=True)
		return super(UserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class StudentInline(admin.TabularInline):
	model = Profile

	fieldsets = (
		(None, {'fields': ('first_name', 'last_name', 'parents')}),
		)
	readonly_fields = ('first_name', 'last_name', 'parents')


class ClassroomAdmin(admin.ModelAdmin):
	inlines = [StudentInline]
	prepopulated_fields = {"slug": ("klasnaam",)}
	#readonly_fields = ("slug",)


# Re-register UserAdmin
admin.site.unregister(Group)
admin.site.register(Profile, UserAdmin)

admin.site.register(ClassRoom, ClassroomAdmin)