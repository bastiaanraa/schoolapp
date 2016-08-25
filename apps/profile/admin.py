#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
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

	aanspreektitel = fields.Field(attribute='aanspreektitel', column_name='Aanspreektitel (Aanschrijf)')
	geboortedatum = fields.Field(attribute='geboortedatum', column_name='Geboortedatum', widget=widgets.DateWidget('%d.%m.%Y'))
	postcode = fields.Field(attribute='postcode', column_name='Hoofdpostnr (Aanschrijf)')
	
	parent_name = fields.Field(attribute='parent_name', column_name='Aanspreeknaam (Aanschrijf)')
	parent_address = fields.Field(attribute="parent_address",column_name='Aanschrijfadres') #adres gescheiden ouder
	parent1 = fields.Field(attribute="parent1", column_name="Vader")
	parent2 = fields.Field(attribute="parent2", column_name="Moeder")

	#klas = fields.Field(attribute="klas", column_name="Klascode")
	klas = fields.Field(attribute="klas", column_name="Klascode", widget=widgets.ForeignKeyWidget(ClassRoom, 'klascode'))
	

	class Meta:
		model = Profile
		import_id_fields = ('nickname',)
		fields = ('nickname','id','last_name','first_name', 'username', 'geboortedatum', \
			'postcode', 'gescheiden', 'klas')
		skip_unchanged = True


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
			child = Profile.objects.get(username=instance.username)
			print "SAVE"
			if 1==2:
			#if instance.gescheiden:
			#dit is niet nodig want enkel voor domiclie kind, tonen we niet
				try:
					with transaction.atomic():
						parent, created = \
							Profile.objects.get_or_create( \
								username=instance.parent_name, 
								first_name=instance.parent_name, 
								is_ouder=True,
								#klas=instance.klas,
								)
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
					with transaction.atomic():
						if not instance.parent1 == '':
							parent1, created = Profile.objects.get_or_create( \
								username=instance.parent1, 
								first_name=instance.parent1, 
								is_ouder=True,
								#klas=instance.klas,
								)
							child.parents.add(parent1)
						if not instance.parent2 == '':
							parent2, created = Profile.objects.get_or_create( \
								username=instance.parent2, 
								first_name=instance.parent2, 
								is_ouder=True,
								#klas=instance.klas,
								)
							child.parents.add(parent2)
				except Exception, e:
					print "except C"
					print e
		

# Define a new User admin
class UserAdmin(ImportMixin, BaseUserAdmin):
	resource_class = ProfileResource
	#inlines = (ProfileInline, )

	list_display = ['first_name', 'last_name', 'is_ouder', 'is_leerling', 'gescheiden']
	fieldsets = (
		(None, {'fields': ('first_name', 'last_name','email', 'password')}),
		('Personal info', {'fields': ('geboortedatum','postcode')}),
		('Gezin', {'fields': ('gescheiden','parents',)}),
		('Klas', {'fields': ('klas','is_leerling', 'is_ouder')}),
		('Permissions', {'fields': ('is_superuser',)}),
	)
	filter_horizontal = ()

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