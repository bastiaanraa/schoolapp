from __future__ import unicode_literals

from django.db import models

from .validators import validate_file_extension


class Bestuur(models.Model):
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
		verbose_name_plural = 'bestuur'

class Verslag(models.Model):
	upload = models.FileField(
		upload_to='bestuur/%Y/', 
		validators=[validate_file_extension],
		help_text="enkel pdf")
	bestuur = models.ForeignKey(Bestuur, blank=True, null=True, related_name='bestuursverslag')
