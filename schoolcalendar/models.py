from __future__ import unicode_literals

from django.db import models
from multiselectfield import MultiSelectField


class SchoolCalendar(models.Model):

	DOELGROEP_CHOICES = (
		('KS', 'Kleuters'),
		('BS', 'Basisschool'),
		('OB', 'Onderbouw'),
		('MS', 'Middelbare school'),
		('MB', 'Middenbouw'),
		('BB', 'Bovenbouw'),
		('AA', 'allen'),
		)

	titel = models.CharField(max_length=250)
	tekst = models.TextField(blank=True)
	startdatum = models.DateField()
	einddatum = models.DateField(null=True, blank=True)
	plaats = models.CharField(max_length=200, blank=True)
	doelgroep = MultiSelectField(choices=DOELGROEP_CHOICES)
	publiek = models.BooleanField(default=False)

	def __str__(self):
		return self.titel

	def get_absolute_url(self):
		from django.urls import reverse
		return reverse('kalender_detail', args=[self.id])

	class Meta:
		verbose_name_plural = 'SchoolCalendar'
		ordering = ['startdatum',]
