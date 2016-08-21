#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	adres = models.CharField("Straat+huisnr", max_length=255, blank=True)
	postcode = models.CharField("Postcode", max_length=15, blank=True)
	gemeente = models.CharField("Gemeente", max_length=255, blank=True)
	land = models.CharField("Land", max_length=255, default='België', blank=True)
	email = models.EmailField("E-mail", blank=True)
	telefoon = models.CharField("Telefoon", max_length=50, blank=True)
	geboortedatum = models.DateField("Geboortedatum", blank=True, null=True)
	nickname = models.CharField("nickname", max_length=255, blank=True)
	aanspreeknaam= models.CharField("aanspreeknaam", max_length=255, blank=True)

	is_ouder = models.BooleanField(default=False)
	is_leerling = models.BooleanField(default=False)
	is_klasouder = models.BooleanField(default=False)
	is_leerkracht = models.BooleanField(default=False)
	is_medewerker = models.BooleanField(default=False)
	parents = models.ManyToManyField("self", blank=True)
	
	def __str__(self):
		try:
			return "%s %s" % (self.user.first_name, self.user.last_name)
		except Exception, e:
			return ""
			
	def __unicode__(self):
		return "%s %s" % (self.user.first_name, self.user.last_name)

"""@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()
"""