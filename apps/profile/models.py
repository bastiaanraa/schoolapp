#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import capfirst

class ClassRoom(models.Model):
	klascode = models.CharField(max_length=10, unique=True)
	klasnaam = models.CharField(max_length=20)
	slug = models.SlugField()

	def __str__(self):
		try:
			return "%s" % (self.klasnaam)
		except Exception, e:
			return ""
			
	def __unicode__(self):
		return "%s" % (self.klasnaam)

class Profile(AbstractUser):
	email = models.EmailField(db_index = True, blank=True)

	adres = models.CharField("Straat+huisnr", max_length=255, blank=True)
	postcode = models.CharField("Postcode", max_length=15, blank=True)
	gemeente = models.CharField("Gemeente", max_length=255, blank=True)
	land = models.CharField("Land", max_length=255, default='België', blank=True)
	telefoon = models.CharField("Telefoon", max_length=50, blank=True)
	gsm = models.CharField("Telefoon", max_length=50, blank=True)
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
	
	klas = models.ForeignKey(ClassRoom, on_delete=models.PROTECT, null=True, blank=True)
	klas_ouder = models.ManyToManyField('ClassRoom', blank=True, related_name='klasouders')
	
	def __str__(self):
		try:
			return "%s %s" % (self.first_name, self.last_name)
		except Exception, e:
			return ""
			
	def __unicode__(self):
		return "%s %s" % (self.first_name, self.last_name)

	def get_gemeente(self):
		return capfirst(self.gemeente.split(' ')[0].lower())