from django.contrib import admin
from django.forms import ModelForm

from tinymce.widgets import TinyMCE

from informatie.models import Informatie, Documenten


class InformatieForm(ModelForm):
	class Meta:
		model = Informatie
		fields = '__all__'
		widgets = {
			'tekst': TinyMCE(attrs={'cols':100, 'rows':15}),
		}


class DocumentenInline(admin.TabularInline):
	model = Documenten

class InformatieAdmin(admin.ModelAdmin):
	inlines = [DocumentenInline,]
	form = InformatieForm
	fields = ('naam', 'slug', 'tekst',)
	prepopulated_fields = {'slug': ('naam',)}


# Register your models here.
admin.site.register(Informatie, InformatieAdmin)