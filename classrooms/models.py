from __future__ import unicode_literals

from django.db import models

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
