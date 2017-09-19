#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import hashlib

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.text import capfirst
from django.utils.safestring import mark_safe

from multiselectfield import MultiSelectField

from classrooms.models import ClassRoom
from werkgroepen.models import Werkgroep
from bestuur.models import Bestuur

DOELGROEP_CHOICES = (
		('', '-'),
		('KS', 'Kleuters'),
		('BS', 'Basisschool'),
		('OB', 'Onderbouw'),
		('MS', 'Middelbare school'),
		('MB', 'Middenbouw'),
		('BB', 'Bovenbouw'),
		('AA', 'allen'),
		)

class ProfileQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class CustomUserManager(UserManager):
	use_for_related_fields = True

	def get_queryset(self):
		return ProfileQuerySet(self.model)

	def active(self, *args, **kwargs):
		return self.get_queryset.active(*arg, **kwargs)

class ProfileManager(models.Manager):
	#custom manager
	def has_email(self):
		return Profile.objects.filter(is_active=True).exclude(email='')
	def active(self):
		return Profile.objects.filter(is_active=True)

class Profile(AbstractUser):
	email = models.EmailField(db_index = True, blank=True)

	adres = models.CharField("Straat+huisnr", max_length=255, blank=True)
	postcode = models.CharField("Postcode", max_length=15, blank=True)
	gemeente = models.CharField("Gemeente", max_length=255, blank=True)
	land = models.CharField("Land", max_length=255, default='België', blank=True)
	telefoon = models.CharField("Telefoon", max_length=50, blank=True)
	gsm = models.CharField("GSM", max_length=50, blank=True)
	#domicilietelefoon = models.CharField("Domicilie Telefoon", max_length=50, blank=True)
	geboortedatum = models.DateField("Geboortedatum", blank=True, null=True)
	nickname = models.CharField("nickname", max_length=255, blank=True)
	aanspreektitel= models.CharField("aanspreetitel", max_length=255, blank=True)
	aanspreeknaam= models.CharField("aanspreeknaam", max_length=255, blank=True)

	is_ouder = models.BooleanField(default=False)
	is_leerling = models.BooleanField(default=False)
	is_klasouder = models.BooleanField(default=False) #dit zal niet werken, want welke klas? wat na nieuwe import?
	is_leerkracht = models.BooleanField(default=False)
	is_medewerker = models.BooleanField(default=False)
	parents = models.ManyToManyField("self", blank=True)
	gescheiden = models.BooleanField(default=False)
	overleden = models.BooleanField(default=False)
	opmerking = models.CharField("Opmerking leerling", max_length=255, blank=True)
	picture = models.ImageField(upload_to='profile/', blank=True, null=True)
	# voor leerkrachten
	doelgroep = MultiSelectField(choices=DOELGROEP_CHOICES, blank=True, default='')
	functie = models.CharField(max_length=255, blank=True)

	# privacy
	hide_address = models.BooleanField(default=False)
	hide_email = models.BooleanField(default=False)
	hide_phone = models.BooleanField(default=False)

	# relations
	klas = models.ForeignKey(ClassRoom, on_delete=models.PROTECT, null=True, blank=True)
	klas_ouder = models.ManyToManyField(ClassRoom, blank=True, related_name='klasouders')
	klasleerkracht = models.ManyToManyField(ClassRoom, blank=True, related_name='leerkracht')

	werkgroep = models.ManyToManyField(Werkgroep, blank=True, related_name='werkgroep')
	bestuur = models.ManyToManyField(Bestuur, blank=True, related_name='bestuur')

	objects = CustomUserManager()
	has_email = ProfileManager()
	active = ProfileManager()
	
	def __str__(self):
		try:
			if self.overleden:
				return "&dagger; %s %s" % (self.first_name, self.last_name)
			return "%s %s" % (self.first_name, self.last_name)
		except Exception, e:
			return ""
			
	def __unicode__(self):
		if self.overleden:
			return "&dagger; %s %s" % (self.first_name, self.last_name)
		return "%s %s" % (self.first_name, self.last_name)

	def get_address(self):
		if self.hide_address:
			return ""
		try:
			if self.get_partner().hide_address:
				return ""
		except Exception, e:
			pass
		return self.adres

	def get_postcode(self):
		if self.hide_address:
			return ""
		try:
			if self.get_partner().hide_address:
				return ""
		except Exception, e:
			pass
		return self.postcode
	
	def get_gemeente(self):
		if self.hide_address:
			return ""
		try:
			if self.get_partner().hide_address:
				return ""
		except Exception, e:
			pass
		return capfirst(self.gemeente.split(' ')[0].lower())

	def get_partner(self):
		try:
			return Profile.objects.filter( \
				adres=self.adres, \
				postcode=self.postcode,
				is_ouder=True, overleden=False
				).exclude(pk=self.pk)[0]
		except Exception, e:
			return None
	
	def image_tag(self):
		if self.picture:
			return mark_safe('<img src="/media/%s" width="auto" height="150px" title="%s"/>' % (self.picture, self))
		return ""
	image_tag.short_description = 'Image'
	
	def make_pw_hash(self, user_name):
		#Function to create hashed password
		salt = '2016'
		h = hashlib.md5(self.username+salt).digest().encode('base64')[:8]
		return h

	def save(self, *args, **kwargs):
		if self.pk is None:
			#set password only for new objects
			if not self.is_superuser:
				self.set_password(self.make_pw_hash(self.username))
		super(Profile, self).save(*args, **kwargs)

	class Meta:
		ordering= ['overleden', 'first_name',]


from csvImporter.model import CsvModel
from csvImporter import fields

class MyCsvModel(CsvModel):
	#mycsv = MyCsvModel.import_data(data=open("steinerschool/leerkrachten.csv"))

	last_name=fields.CharField()
	first_name=fields.CharField()
	email=fields.CharField()
	is_medewerker=fields.BooleanField()
	username = fields.CharField()
	
	class Meta:
		delimiter = str(",")
		dbModel = Profile
		silent_failure = True
		update = {'keys': ["username",]}