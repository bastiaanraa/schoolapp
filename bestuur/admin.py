from django.contrib import admin
from django.forms import ModelForm

from tinymce.widgets import TinyMCE

from profile.models import Profile
from bestuur.models import Bestuur, Verslag


class BestuurForm(ModelForm):
	class Meta:
		model = Bestuur
		fields = '__all__'
		widgets = {
			'tekst': TinyMCE(attrs={'cols':100, 'rows':15}),
		}


class ProfileInline(admin.TabularInline):
	model = Profile.bestuur.through

class VerslagInline(admin.TabularInline):
	model = Verslag

class BestuurAdmin(admin.ModelAdmin):
	inlines = [VerslagInline, ProfileInline]
	exclude = ('bestuur',)
	form = BestuurForm
	fields = ('naam', 'slug', 'tekst',)
	prepopulated_fields = {'slug': ('naam',)}


# Register your models here.
admin.site.register(Bestuur, BestuurAdmin)