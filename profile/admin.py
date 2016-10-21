#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django.template.loader import get_template
from django.db import transaction, IntegrityError
from django.core import mail 

from django.utils import encoding

from import_export import resources, fields, widgets
from import_export.admin import ImportMixin

from profile.models import Profile
from profile.utils import send_password_mail
from classrooms.models import ClassRoom

import logging
logger = logging.getLogger("schoolapp")

			
class ProfileResource(resources.ModelResource):
	# rename regular attributes
	username = fields.Field(attribute='username', column_name="Rijksregisternr.")
	first_name = fields.Field(attribute='first_name', column_name='Voornaam')
	last_name = fields.Field(attribute='last_name', column_name='Naam')
	nickname = fields.Field(attribute='nickname', column_name='Nickname')
	geboortedatum = fields.Field(attribute='geboortedatum', column_name='Geboortedatum', widget=widgets.DateWidget('%d.%m.%Y'))
	
	aanspreektitel = fields.Field(attribute='aanspreektitel', column_name='Aanspreektitel (Aanschrijf)')
	aanspreeknaam = fields.Field(attribute="aanpspreeknaam", column_name='Aanspreeknaam (Aanschrijf)')
	parent1_voornaam = fields.Field(attribute="parent1_voornaam", column_name="Voornaam vader")
	parent1_naam = fields.Field(attribute="parent1_naam", column_name="Familienaam vader")
	parent2_voornaam = fields.Field(attribute="parent2_voornaam", column_name="Voornaam moeder")
	parent2_naam = fields.Field(attribute="parent2_naam", column_name="Familienaam moeder")
	adres = fields.Field(attribute="adres",column_name='Domicilie-adres')
	address = fields.Field(attribute="address",column_name='Aanschrijfadres')
	postcode = fields.Field(attribute='postcode', column_name='Hoofdpostnr (Aanschrijf)')
	gemeente = fields.Field(attribute='gemeente', column_name='Deelgemeente (Aanschrijf)')
	parent1_email = fields.Field(attribute="parent1_email", column_name="E-mail vader")
	parent2_email = fields.Field(attribute="parent2_email", column_name="E-mail moeder")
	#parent1_telefoon = fields.Field(attribute="parent1_telefoon", column_name="Telefoon vader")
	#parent2_telefoon = fields.Field(attribute="parent1_telefoon", column_name="Telefoon moeder")
	parent1_gsm = fields.Field(attribute="parent1_gsm", column_name="GSM Vader")
	parent2_gsm = fields.Field(attribute="parent2_gsm", column_name="GSM Moeder")
	telefoon = fields.Field(attribute="telefoon", column_name="Domicilie-telefoon")
	opmerking = fields.Field(attribute="opmerking", column_name="Opmerking leerling")
	parent1_overleden = fields.Field(attribute="parent1_overleden", column_name="Vader overleden")
	parent2_overleden = fields.Field(attribute="parent2_overleden", column_name="Moeder overleden")
	#parent_gescheiden = fields.Field(attribute='parent_name', column_name='Aanspreeknaam (Aanschrijf)')
	
	klas = fields.Field(attribute="klas", column_name="Klascode", widget=widgets.ForeignKeyWidget(ClassRoom, 'klascode'))
	

	class Meta:
		model = Profile
		import_id_fields = ('nickname',) #rijksregister!!
		fields = ('username', 'nickname','last_name','first_name', 'geboortedatum', \
			'postcode', 'gescheiden', 'klas', 'telefoon', )
		skip_unchanged = True
		report_skipped = True


	def dehydrate_username(self, profile):
		if profile.username:
			return profile.username
		else:
			return profile.nickname
		# DIT DOET NIETS?
		#return profile.first_name+profile.last_name

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
			try:
				with transaction.atomic():
					instance.save()
			except IntegrityError, e:
				#IntegrityError: (1062, "Duplicate entry 'zzz' for key 'username'")
				print "save instance: integrity error"
				print(e)
			except Exception, e:
				print "nog een andere fout"
				print e
		self.after_save_instance(instance, dry_run)

	def before_save_instance(self, instance, dry_run):
		# INVALIDE CACHE ! en cache hoger zetten
		
		instance.is_leerling = True
		if instance.aanspreektitel == "Aan":
			instance.gescheiden = True
		

	def after_save_instance(self, instance, dry_run):
		#print 'after_save'
		#print instance.aanpspreeknaam
		# om te weten met welke parent we te maken hebben
		
		
		if dry_run == False:
			overleden=False
			hide_address =False

			try:
				child = Profile.objects.get(username=instance.username)
			except:
				print "except 0"
				#print e
			
			if instance.gescheiden:
				email = ''
				voornaam = ''
				naam = ''
				gsm = ''
				

				
				if instance.aanpspreeknaam == instance.parent1_naam+' '+instance.parent1_voornaam:
					#print 'Parent 1'
					email = instance.parent1_email
					voornaam = instance.parent1_voornaam
					naam = instance.parent1_naam
					gsm = instance.parent1_gsm
					
					if instance.parent1_overleden == "overleden":
						overleden=True
					
					if 'adres:NietBeschikbaar(vader)' in instance.opmerking:
						hide_address = True
				elif instance.aanpspreeknaam == instance.parent2_naam+' '+instance.parent2_voornaam:
					#print 'Parent 2'
					email = instance.parent2_email
					voornaam = instance.parent2_voornaam
					naam = instance.parent2_naam
					gsm = instance.parent2_gsm
					
					if instance.parent2_overleden == "overleden":
						overleden=True
					
					if 'adres:NietBeschikbaar(moeder)' in instance.opmerking:
						hide_address = True
				
				username = email
				if username == '':
						username = instance.aanpspreeknaam
						username = username.replace(" ", "")

				# BETER: eerst kijken of ouder bestaat, dan ofwel update or create ?!

				try:
					with transaction.atomic():
						parent = Profile(username=username,
								first_name=voornaam,
								last_name=naam,
								is_ouder=True,
								adres=instance.address,
								gemeente=instance.gemeente,
								postcode=instance.postcode,
								email = email,
								gsm = gsm,
								telefoon= instance.telefoon,
								overleden=overleden,
								hide_address=hide_address
								)
						parent.save()
				except IntegrityError, e:
					parent = Profile.objects.get(username=username) #?
					parent.hide_address = hide_address
					parent.is_active = True
					parent.save()
				except Exception, e:
					print "except A"
					print e
				
				try:
					child.parents.add(parent)
				except Exception, e:
					print "except B"
					print e
			else:
				try:
					
					if 'adres:NietBeschikbaar' in instance.opmerking:
						hide_address = True

					#is er een parent1 = vader?
					if not instance.parent1_naam == '':
						#heeft email?
						username = instance.parent1_email
						if username == '':
							username = instance.parent1_voornaam+instance.parent1_naam
							username = username.replace(" ", "")

						overleden=False
						if instance.parent1_overleden == "overleden":
							overleden=True
						
						try:
							parent1 = Profile(
								username=username,
								first_name=instance.parent1_voornaam,
								last_name=instance.parent1_naam,
								is_ouder=True,
								adres=instance.address,
								gemeente=instance.gemeente,
								postcode=instance.postcode,
								email = instance.parent1_email,
								gsm = instance.parent1_gsm,
								telefoon=instance.telefoon,
								overleden=overleden,
								hide_address=hide_address
								)
							with transaction.atomic():
								parent1.save()
						except IntegrityError, e:
							parent1 = Profile.objects.get(username=username)
							parent1.hide_address = hide_address
							parent1.is_active = True
							parent1.save()
						except Exception, e:
							print e
						
						try:
							with transaction.atomic():
								child.parents.add(parent1)
						except Exception, e:
							print 'Except AA'
							print e
						
					
					#is er een ouder2
					if not instance.parent2_naam == '':
						username = instance.parent2_email
						if username == '':
							username = instance.parent2_voornaam+instance.parent2_naam
							username = username.replace(" ", "")
						
						overleden=False
						if instance.parent2_overleden == "overleden":
							overleden=True
						try:
							#print username
							parent2 = Profile(
								username=username,
								first_name=instance.parent2_voornaam,
								last_name=instance.parent2_naam,
								is_ouder=True,
								adres=instance.address,
								gemeente=instance.gemeente,
								postcode=instance.postcode,
								email = instance.parent2_email,
								gsm = instance.parent2_gsm,
								telefoon = instance.telefoon,
								overleden=overleden,
								hide_address=hide_address
								)
							with transaction.atomic():
								parent2.save()
						except IntegrityError, e:
							parent2 = Profile.objects.get(username=username)
							parent2.hide_address = hide_address
							parent2.is_active = True
							parent2.save()
						except Exception, e:
							print 'Except BB'
							print e
						
						try:
							with transaction.atomic():
								child.parents.add(parent2)
						except Exception, e:
							print 'except BBB'
							print e
				except Exception, e:
					print username
					print "except C"
					print e
		

# Define a new User admin
class UserAdmin(ImportMixin, BaseUserAdmin):
	resource_class = ProfileResource
	#inlines = (ProfileInline, )
	list_filter = ('is_leerling', 'is_ouder', 'is_klasouder', 'is_leerkracht', 'is_medewerker')
	list_display = ['first_name', 'last_name', 'is_ouder', 'is_leerling', 'klas']

	readonly_fields = ('image_tag',)
	
	filter_horizontal = ('parents',)
	actions = ['send_password_selected', ]

	def get_fieldsets(self, request, obj=None):
		if not obj:
			return self.add_fieldsets

		if request.user.is_superuser:
			perm_fields = ('is_active', 'is_staff', 'is_superuser',
						   'groups', 'user_permissions')
		else:
			# modify these to suit the fields you want your
			# staff user to be able to edit
			perm_fields = ('is_active', 'is_staff', 'groups')

		return [(None, {'fields': ('username','first_name', 'last_name', 'password')}),
				('Personal info', {'fields': ('geboortedatum', 'overleden','adres','postcode', 'gemeente', 'telefoon', 'gsm', 'email')}),
				('Privacy', {'fields': ('hide_address', 'hide_email', 'hide_phone')}),
				('Gezin', {'fields': ('is_leerling', 'is_ouder', 'gescheiden','parents',)}),
				('Klas (leerling)', {'fields': ('klas',)}),
				('Klasouder', {'fields': ('is_klasouder', 'klas_ouder',)}),
				('Leerkracht/Medewerkers', {'fields': ('is_leerkracht', 'is_medewerker', 'klasleerkracht', 'functie', 'doelgroep', 'picture', 'image_tag')}),
				('Werkgroep', {'fields': ('werkgroep',)}),
				('Bestuur', {'fields': ('bestuur',)}),
				('Permissions', {'fields': perm_fields}),
				('Important dates', {'fields': ('last_login', 'date_joined')})]


	#def formfield_for_manytomany(self, db_field, request, **kwargs):
		# enkel tonen bij leerlingen?

		#enkel ouders in lijst_
		#if db_field.name == "parents":
		#	kwargs["queryset"] = Profile.objects.filter(is_ouder=True)
		#return super(UserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

	def changelist_view(self, request, extra_context=None):
		if 'action' in request.POST and request.POST['action'] == 'send_password_all':
			if not request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
				post = request.POST.copy()
				for u in Profile.objects.all():
					post.update({admin.ACTION_CHECKBOX_NAME: str(u.id)})
				request._set_post(post)
		return super(UserAdmin, self).changelist_view(request, extra_context)


	def send_password_selected(self, request, queryset):
		if request.POST.get('post'):
			send_password_mail(queryset, request)
			self.message_user(request, "Mail sent successfully ")
		else:
			context = {
				'queryset': queryset,
				'action':'send_password_selected',
				'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
			}
			return TemplateResponse(request, 'admin/sendmail.html',
				context)
	
	send_password_selected.short_description = "Verstuur wachtwoord naar geselecteerde gebruikers"

	def send_password_all(self, request, queryset):
		queryset = Profile.objects.filter(is_active=True, is_superuser=False, is_leerling=False).exclude(email='')
		if request.POST.get('post'):
			send_password_mail(queryset,request)
			self.message_user(request, "Mail sent successfully ")
		else:
			context = {
				'queryset': queryset,
				'action': 'send_password_all',
				'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
			}
			return TemplateResponse(request, 'admin/sendmail.html',
				context)
	
	send_password_all.short_description = "Verstuur wachtwoord naar ALLE gebruikers"





# Re-register UserAdmin
#admin.site.register(Group)
admin.site.register(Profile, UserAdmin)