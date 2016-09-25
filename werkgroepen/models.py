from __future__ import unicode_literals

from django.db import models


class Werkgroep(models.Model):
	naam = models.CharField(max_length=20)
	slug = models.SlugField()
	tekst = models.TextField()

	def __str__(self):
		try:
			return "%s" % (self.naam)
		except Exception, e:
			return ""
			
	def __unicode__(self):
		return "%s" % (self.naam)

	class Meta:
		verbose_name_plural = 'werkgroepen'
