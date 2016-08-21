#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError

from django.utils import encoding

from import_export import resources, fields, widgets
from import_export.admin import ImportMixin

from apps.myusermodel.models import Profile

import logging
logger = logging.getLogger("schoolapp")


class OneToOneField(fields.Field):
	parent_prop = ''
	child_prop = ''

	def __init__(self, parent_prop, child_prop, *args, **kwargs):
		self.parent_prop = parent_prop
		self.child_prop = child_prop
		super().__init__(*args, **kwargs)

	def save(self, obj, data):
		if not self.readonly:
			child_obj = getattr(obj, self.parent_prop, None)
			if not child_obj:
				raise ValueError('Unable to find %s on %s' % (self.parent_prop, obj))
			setattr(child_obj, self.child_prop, self.clean(data))
			child_obj.save()

			
class ProfileResource(resources.ModelResource):
	# rename regular attributes
	username = fields.Field(attribute='username')
	first_name = fields.Field(attribute='first_name', column_name='Voornaam')
	last_name = fields.Field(attribute='last_name', column_name='Naam')

	#geboortedatum = fields.Field(attribute='geboortedatum', column_name='Geboortedatum', widget=widgets.DateWidget())
	geboortedatum = fields.Field(attribute='geboortedatum', column_name='Geboortedatum')
	postcode = fields.Field(attribute='postcode', column_name='Hoofdpostnr (Aanschrijf)')
	
	parent1 = fields.Field(attribute="parent1", column_name="Vader")
	parent2 = fields.Field(attribute="parent2", column_name="Moeder")
	

	"""
	VOORBEELD VAN OneToOneField
	address = OneToOneField(
			attribute='address__freeform',
			parent_prop='address',
			child_prop='freeform',
			column_name='address',
		)
	"""

	class Meta:
		model = User
		fields = ('id','last_name','first_name', 'username')
		#skip_unchanged = True

	def init_instance(self, row=None):
		"""
		Initializes a new Django model.
		"""
		print 'init_instance'
		#print self._meta.fields
		#print self._meta.model
		return self._meta.model()

	def dehydrate_first_name(self, user):
		print "dehydrate_first_name"
		print user
		return user.first_name.encode('utf-8')

	def dehydrate_username(self, profile):
		# DIT DOET NIETS
		return profile.first_name+profile.last_name

	def save_instance(self, instance, dry_run=False):
		"""
		Takes care of saving the object to the database.
		Keep in mind that this is done by calling ``instance.save()``, so
		objects are not created in bulk!
		"""
		self.before_save_instance(instance, dry_run)
		if not dry_run:
			try:
				with transaction.atomic():
					instance.save()
			except IntegrityError, e:
				#IntegrityError: (1062, "Duplicate entry 'zzz' for key 'username'")
				logger.debug(e)
		self.after_save_instance(instance, dry_run)

	def before_save_instance(self, instance, dry_run):
		print 'before_save'
		instance.username = instance.first_name+instance.last_name
		

	def after_save_instance(self, instance, dry_run):
		print 'after_save'
		user = instance
		if not instance.parent1 == '':
			print 'parent1'
			try:
				parent1_user = User(username=instance.parent1, first_name=instance.parent1)
			except Exception, e:
				print e
		if not instance.parent2 == '':
			print 'parent2'
			try:
				parent2_user = User(username=instance.parent2, first_name=instance.parent2)
			except Exception, e:
				print e
			
		profile = Profile(
			user=user,
			postcode=instance.postcode,
			geboortedatum=datetime.strptime(instance.geboortedatum, "%d.%m.%Y").date(), #format str to date
			is_leerling=True,
			)
		if dry_run == False:
			try:
				#user = more.user
				print "user save"
				user.save() # Duplicate entry opvangen
				profile.save() # Duplicate entry opvangen
				
				parent1_user.save()
				profile_parent1 = Profile(user=parent1_user, is_ouder=True)
				profile_parent1.save() # Duplicate opvagen

				parent2_user.save()
				profile_parent2 = Profile(user=parent2_user, is_ouder=True)
				profile_parent2.save() # Duplicate opvagen
				
				profile.parents.add(profile_parent1, profile_parent2)
			except Exception, e:
				print "except"
				print e
		


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
	model = Profile
	can_delete = False
	verbose_name_plural = 'Profiel'

	def formfield_for_manytomany(self, db_field, request, **kwargs):
		# enkel tonen bij leerlingen?

		#enkel ouders in lijst_
		if db_field.name == "parents":
			kwargs["queryset"] = Profile.objects.filter(is_ouder=True)
		return super(ProfileInline, self).formfield_for_manytomany(db_field, request, **kwargs)

# Define a new User admin
class UserAdmin(ImportMixin, BaseUserAdmin):
	resource_class = ProfileResource
	inlines = (ProfileInline, )

	list_display = ['first_name', 'last_name', 'is_ouder', 'is_leerling']

	def is_ouder(self, obj):
		return obj.profile.is_ouder
	def is_leerling(self, obj):
		return obj.profile.is_leerling


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)