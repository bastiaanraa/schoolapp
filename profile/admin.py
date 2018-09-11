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
from django.db.models import Q
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
	#geboortedatum = fields.Field(attribute='geboortedatum', column_name='Geboortedatum', widget=widgets.DateWidget('%d.%m.%Y'))
	
	aanspreektitel = fields.Field(attribute='aanspreektitel', column_name='Aanspreektitel (Aanschrijf)')
	aanspreeknaam = fields.Field(attribute="aanspreeknaam", column_name='Aanspreeknaam (Aanschrijf)')
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
		import_id_fields = ('username',) #rijksregister!!
		fields = ('username', 'nickname','last_name','first_name', 
			#'geboortedatum', 
			'postcode', 'gescheiden', 'klas', 'telefoon', )
		skip_unchanged = True
		report_skipped = True

	#def before_import(self, dataset, using_transactions, dry_run, **kwargs):
	#def before_import(self, dataset, dry_run, **kwargs):
		# zet eerst alle lln en ouders inactief
	#	if not dry_run:
			#queryset = Profile.objects.filter(is_active=True, is_superuser=False, is_leerling=True)
			#queryset.update(is_active=False)
			#queryset = Profile.objects.filter(is_active=True, is_superuser=False, is_ouder=True)
			#queryset.update(is_active=False)
			# MAG NIET WANT 2 X APART IMPORT
	#		pass


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


	def save_instance(self, instance, using_transaction, dry_run=False):
		""" 
		Takes care of saving the object to the database.
		Keep in mind that this is done by calling ``instance.save()``, so
		objects are not created in bulk!
		"""
		self.before_save_instance(instance, dry_run)
		if not dry_run:
			try:
				with transaction.atomic():
					#instance.is_active = True
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
		instance.is_active = True
		if instance.aanspreektitel == "Aan":
			instance.gescheiden = True
		
			if instance.aanspreeknaam.replace(" ", "").lower() == instance.parent1_naam.replace(" ", "").lower()+instance.parent1_voornaam.replace(" ", "").lower():
				pass
			elif instance.aanspreeknaam.replace(" ", "").lower() == instance.parent2_naam.replace(" ", "").lower()+instance.parent2_voornaam.replace(" ", "").lower():
				pass
			else:
				raise Exception("Fout in Aanspreeknaam (Aanschrijf): %s" % (instance.aanspreeknaam))
		

	def after_save_instance(self, instance, dry_run):
		#print 'after_save'
		#print instance.aanspreeknaam
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
				

				
				if instance.aanspreeknaam.replace(" ", "").lower() == instance.parent1_naam.replace(" ", "").lower()+instance.parent1_voornaam.replace(" ", "").lower():
					#print 'Parent 1'
					email = instance.parent1_email
					voornaam = instance.parent1_voornaam
					naam = instance.parent1_naam
					gsm = instance.parent1_gsm
					
					if instance.parent1_overleden == "overleden":
						overleden=True
					
					if 'adres:NietBeschikbaar(vader)' in instance.opmerking:
						hide_address = True
				elif instance.aanspreeknaam.replace(" ", "").lower() == instance.parent2_naam.replace(" ", "").lower()+instance.parent2_voornaam.replace(" ", "").lower():
					#print 'Parent 2'
					email = instance.parent2_email
					voornaam = instance.parent2_voornaam
					naam = instance.parent2_naam
					gsm = instance.parent2_gsm
					
					if instance.parent2_overleden == "overleden":
						overleden=True
					
					if 'adres:NietBeschikbaar(moeder)' in instance.opmerking:
						hide_address = True
				else:
					print "IETS FOUT"
					#print instance.aanspreeknaam+'Z'
					#print instance.parent1_naam+'Z'
					#print instance.parent1_voornaam+'Z'
					#print instance.parent2_naam+'Z'
					#print instance.parent2_voornaam+'Z'
					
				
				username = email
				if username == '':
						username = instance.aanspreeknaam
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
					#todo: adresgegevens aanpassen
					parent.first_name = voornaam
					parent.last_name = naam
					parent.adres=instance.address
					parent.gemeente=instance.gemeente
					parent.postcode=instance.postcode
					parent.email = email
					parent.gsm = gsm
					parent.telefoon= instance.telefoon
					#parent.overleden=overleden
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
							#todo: adresgegevens aanpassen
							parent1.adres=instance.address
							parent1.gemeente=instance.gemeente
							parent1.postcode=instance.postcode
							parent1.email = instance.parent1_email
							parent1.gsm = instance.parent1_gsm
							parent1.telefoon= instance.telefoon
							#parent1.overleden=overleden
							parent1.save()
							parent1
						except Exception, e:
							print e
						
						try:
							with transaction.atomic():
								child.parents.add(parent1)
						except Exception, e:
							print 'Except AA'
							print parent1
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
							#todo: adresgegevens aanpassen
							parent2.adres=instance.address
							parent2.gemeente=instance.gemeente
							parent2.postcode=instance.postcode
							parent2.email = instance.parent2_email
							parent2.gsm = instance.parent2_gsm
							parent2.telefoon= instance.telefoon
							#parent2.overleden=overleden
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
		
class SchoolFilter(admin.SimpleListFilter):
	# Human-readable title which will be displayed in the
	# right admin sidebar just above the filter options.
	title = 'school'

	# Parameter for the filter that will be used in the URL query.
	parameter_name = 'school'

	def lookups(self, request, model_admin):
		"""
		Returns a list of tuples. The first element in each
		tuple is the coded value for the option that will
		appear in the URL query. The second element is the
		human-readable name for the option that will appear
		in the right sidebar.
		"""
		return (
			('basis', 'Basisschool'),
			('middelbare', 'Middebare School'),
		)

	def queryset(self, request, queryset):
		"""
		Returns the filtered queryset based on the value
		provided in the query string and retrievable via
		`self.value()`.
		"""
		if self.value() == 'basis':
			return queryset.filter(
				Q(klas__klascode__startswith="L")
				| Q(klas__klascode__startswith="P")
				| Q(klas__klascode__startswith="K")
				| Q(klasleerkracht__klascode__startswith="L")
				| Q(klasleerkracht__klascode__startswith="P")
				| Q(klasleerkracht__klascode__startswith="K")
				| Q(klas_ouder__klascode__startswith="L")
				| Q(klas_ouder__klascode__startswith="P")
				| Q(klas_ouder__klascode__startswith="K")
				)
		if self.value() == 'middelbare':
			return queryset.filter(
				Q(is_leerling=True, klas__klascode__startswith="1")
				| Q(is_leerling=True, klas__klascode__startswith="2")
				| Q(is_leerling=True, klas__klascode__startswith="3")
				| Q(is_leerling=True, klas__klascode__startswith="4")
				| Q(is_leerling=True, klas__klascode__startswith="5")
				| Q(is_leerling=True, klas__klascode__startswith="6")

				| Q(klasleerkracht__klascode__startswith="1")
				| Q(klasleerkracht__klascode__startswith="2")
				| Q(klasleerkracht__klascode__startswith="3")
				| Q(klasleerkracht__klascode__startswith="4")
				| Q(klasleerkracht__klascode__startswith="5")
				| Q(klasleerkracht__klascode__startswith="6")

				| Q(klas_ouder__klascode__startswith="1")
				| Q(klas_ouder__klascode__startswith="2")
				| Q(klas_ouder__klascode__startswith="3")
				| Q(klas_ouder__klascode__startswith="4")
				| Q(klas_ouder__klascode__startswith="5")
				| Q(klas_ouder__klascode__startswith="6")
				)
		return queryset

# Define a new User admin
class UserAdmin(ImportMixin, BaseUserAdmin):
	resource_class = ProfileResource
	#inlines = (ProfileInline, )
	list_filter = ('is_leerling', SchoolFilter, 'is_ouder', 'is_klasouder', 'is_leerkracht', 'is_medewerker', 'is_active', 'doelgroep', 'last_login', 'date_joined')
	list_display = ['first_name', 'last_name', 'is_ouder', 'is_leerling', 'klas', 'klasouder_klas', 'klasleerkracht_klas']

	readonly_fields = ('image_tag',)
	
	filter_horizontal = ('parents',)
	actions = ['send_password_selected', 'put_inactive', 'put_one_higher_klasouder','put_one_higher_klasleerkracht']

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

	def klasouder_klas(self, obj):
		return "\n".join([p.klascode for p in obj.klas_ouder.all()])

	def klasleerkracht_klas(self, obj):
		return "\n".join([p.klascode for p in obj.klasleerkracht.all()])

	#def formfield_for_manytomany(self, db_field, request, **kwargs):
		# enkel tonen bij leerlingen?

		#enkel ouders in lijst_
		#if db_field.name == "parents":
		#	kwargs["queryset"] = Profile.objects.filter(is_ouder=True)
		#return super(UserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


	def save_model(self, request, obj, form, change):
		# indien nog nooit aangemeld -> set_password(username) bij wijzigen username
		# omdat we bij aanmaken set_password(username), daarom opnieuw set_passwprd voor versturen login mail
		# beetje omslachtig, beter set_password(voormaan+naam)
		if 'username' in form.changed_data:
			if obj.last_login is None:
				obj.set_password(obj.make_pw_hash(obj.username))

		super(UserAdmin, self).save_model(request, obj, form, change)

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

	def put_inactive(self, request, queryset):
		#zet alle lln en ouders inactief
		#queryset = Profile.objects.filter(is_active=True, is_superuser=False, is_leerling=True, is_ouder=True)
		queryset.update(is_active=False)
	put_inactive.short_description = 'Zet alle lln en ouders inactief'

	def put_one_higher_klasouder(self, request, queryset):
		# zet geselecteerde klasouders een klas hoger
		queryset = queryset.filter(is_klasouder=True)
		for p in queryset:
			for klas_ouder in p.klas_ouder.all():
				klas = None
				if klas_ouder.klascode.startswith("P"):
					# do nothing for peuters
					continue
				elif klas_ouder.klascode.startswith("K"):
					klas = ClassRoom.objects.get(klascode="L1")
				elif klas_ouder.klascode.startswith("L1"):
					klas = ClassRoom.objects.get(klascode="L2")
				elif klas_ouder.klascode.startswith("L2"):
					klas = ClassRoom.objects.get(klascode="L3")
				elif klas_ouder.klascode.startswith("L3"):
					klas = ClassRoom.objects.get(klascode="L4")
				elif klas_ouder.klascode.startswith("L4"):
					klas = ClassRoom.objects.get(klascode="L5")
				elif klas_ouder.klascode.startswith("L5"):
					klas = ClassRoom.objects.get(klascode="L6")

				# van 6 naar 7 kunnen weniet automatisch

				elif klas_ouder.klascode.startswith("1S1A"):
					klas = ClassRoom.objects.get(klascode="2S1A")
				elif klas_ouder.klascode.startswith("1S1B"):
					klas = ClassRoom.objects.get(klascode="2S1B")
				elif klas_ouder.klascode.startswith("1S1C"):
					klas = ClassRoom.objects.get(klascode="2S1C")

				# van 8 naar 9 kunnen we niet automatisch
				elif klas_ouder.klascode.startswith("1S1A"):
					klas = ClassRoom.objects.get(klascode="2S1A")
				elif klas_ouder.klascode.startswith("1S1B"):
					klas = ClassRoom.objects.get(klascode="2S1B")
				elif klas_ouder.klascode.startswith("1S1C"):
					klas = ClassRoom.objects.get(klascode="2S1C")

				elif klas_ouder.klascode.startswith("3S1A"):
					klas = ClassRoom.objects.get(klascode="4S1A")
				elif klas_ouder.klascode.startswith("3S1B"):
					klas = ClassRoom.objects.get(klascode="4S1B")
				elif klas_ouder.klascode.startswith("3TS1"):
					klas = ClassRoom.objects.get(klascode="4T1")

				elif klas_ouder.klascode.startswith("4S1A"):
					klas = ClassRoom.objects.get(klascode="5S1A")
				elif klas_ouder.klascode.startswith("4S1B"):
					klas = ClassRoom.objects.get(klascode="5S1B")
				elif klas_ouder.klascode.startswith("4TS1"):
					klas = ClassRoom.objects.get(klascode="5T1")

				elif klas_ouder.klascode.startswith("5S1A"):
					klas = ClassRoom.objects.get(klascode="6S1A")
				elif klas_ouder.klascode.startswith("5S1B"):
					klas = ClassRoom.objects.get(klascode="6S1B")
				elif klas_ouder.klascode.startswith("5TS1"):
					klas = ClassRoom.objects.get(klascode="6T1")

				#12de klas geen klasouder meer

				if klas:
					p.klas_ouder.add(klas)
				p.klas_ouder.remove(klas_ouder)
	put_one_higher_klasouder.short_description = "Zet geselecteerde klasouders een klas hoger"

	def put_one_higher_klasleerkracht(self, request, queryset):
		# zet geselecteerde klasouders een klas hoger
		queryset = queryset.filter(is_leerkracht=True)
		for p in queryset:
			for klas_klasleerkracht in p.klasleerkracht.all():
				klas = None
				if klas_klasleerkracht.klascode.startswith("P"):
					# do nothing for peuters
					continue
				elif klas_klasleerkracht.klascode.startswith("K"):
					# do nothing for kleuters
					continue
				elif klas_klasleerkracht.klascode.startswith("L1"):
					klas = ClassRoom.objects.get(klascode="L2")
				elif klas_klasleerkracht.klascode.startswith("L2"):
					klas = ClassRoom.objects.get(klascode="L3")
				elif klas_klasleerkracht.klascode.startswith("L3"):
					klas = ClassRoom.objects.get(klascode="L4")
				elif klas_klasleerkracht.klascode.startswith("L4"):
					klas = ClassRoom.objects.get(klascode="L5")
				elif klas_klasleerkracht.klascode.startswith("L5"):
					klas = ClassRoom.objects.get(klascode="L6")

				# van 6 naar 7 kunnen we niet automatisch

				elif klas_klasleerkracht.klascode.startswith("1S1A"):
					klas = ClassRoom.objects.get(klascode="2S1A")
				elif klas_klasleerkracht.klascode.startswith("1S1B"):
					klas = ClassRoom.objects.get(klascode="2S1B")
				elif klas_klasleerkracht.klascode.startswith("1S1C"):
					klas = ClassRoom.objects.get(klascode="2S1C")

				# van 8 naar 9 kunnen we niet automatisch

				elif klas_klasleerkracht.klascode.startswith("1S1A"):
					klas = ClassRoom.objects.get(klascode="2S1A")
				elif klas_klasleerkracht.klascode.startswith("1S1B"):
					klas = ClassRoom.objects.get(klascode="2S1B")
				elif klas_klasleerkracht.klascode.startswith("1S1C"):
					klas = ClassRoom.objects.get(klascode="2S1C")

				elif klas_klasleerkracht.klascode.startswith("3S1A"):
					klas = ClassRoom.objects.get(klascode="4S1A")
				elif klas_klasleerkracht.klascode.startswith("3S1B"):
					klas = ClassRoom.objects.get(klascode="4S1B")
				elif klas_klasleerkracht.klascode.startswith("3TS1"):
					klas = ClassRoom.objects.get(klascode="4T1")

				elif klas_klasleerkracht.klascode.startswith("4S1A"):
					klas = ClassRoom.objects.get(klascode="5S1A")
				elif klas_klasleerkracht.klascode.startswith("4S1B"):
					klas = ClassRoom.objects.get(klascode="5S1B")
				elif klas_klasleerkracht.klascode.startswith("4TS1"):
					klas = ClassRoom.objects.get(klascode="5T1")

				elif klas_klasleerkracht.klascode.startswith("5S1A"):
					klas = ClassRoom.objects.get(klascode="6S1A")
				elif klas_klasleerkracht.klascode.startswith("5S1B"):
					klas = ClassRoom.objects.get(klascode="6S1B")
				elif klas_klasleerkracht.klascode.startswith("5TS1"):
					klas = ClassRoom.objects.get(klascode="6T1")

				#12de klas geen klasleerkracht meer automatisch
				elif klas_klasleerkracht.klascode.startswith("6S"):
					klas = None
				elif klas_klasleerkracht.klascode.startswith("6T"):
					klas = None

				if klas:
					p.klasleerkracht.add(klas)
				p.klasleerkracht.remove(klas_klasleerkracht)
	put_one_higher_klasleerkracht.short_description = "Zet geselecteerde klasleerkracht een klas hoger"




# Re-register UserAdmin
#admin.site.register(Group)
admin.site.register(Profile, UserAdmin)


from django.contrib.admin.models import LogEntry

class LogEntryAdmin(admin.ModelAdmin):
    search_fields = (
        'object_id',
        'object_repr',
        'action_time',
        'action_flag',
        'change_message',
    )
    readonly_fields = ('content_type',
        'user',
        'action_time',
        'object_id',
        'object_repr',
        'action_flag',
        'change_message'
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

admin.site.register(LogEntry, LogEntryAdmin)