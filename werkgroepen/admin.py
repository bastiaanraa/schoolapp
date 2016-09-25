from django.contrib import admin
from django.forms import ModelForm

from tinymce.widgets import TinyMCE

from profile.models import Profile
from werkgroepen.models import Werkgroep


class WerkgroepForm(ModelForm):
	class Meta:
		model = Werkgroep
		fields = '__all__'
		widgets = {
			'tekst': TinyMCE(attrs={'cols':100, 'rows':15}),
		}


class ProfileInline(admin.TabularInline):
	model = Profile.werkgroep.through

class WerkgroepAdmin(admin.ModelAdmin):
	inlines = [ProfileInline]
	form = WerkgroepForm
	fields = ('naam', 'slug', 'tekst')
	prepopulated_fields = {'slug': ('naam',)}


# Register your models here.
admin.site.register(Werkgroep, WerkgroepAdmin)