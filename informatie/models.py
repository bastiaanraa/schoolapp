from __future__ import unicode_literals
import os
from django.db import models

from .validators import validate_file_extension


class Informatie(models.Model):
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
		verbose_name_plural = 'informatie'

def custom_upload_to(instance, filename):
	# this function has to return the location to upload the file
		
		return os.path.join('/media/%s/' % instance.naam)

class Documenten(models.Model):

	upload = models.FileField(
		upload_to='informatie/%Y/', 
		validators=[validate_file_extension],
		help_text="enkel pdf",
		null=True, blank=True)
	datum = models.DateField(auto_now_add=True)
	informatie = models.ForeignKey(Informatie, blank=True, null=True, related_name='informatie')

	def filename(self):
		return os.path.basename(self.upload.name).replace('_', ' ')

	class Meta:
		ordering = ['-datum',]
