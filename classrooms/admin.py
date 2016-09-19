from django.contrib import admin

from classrooms.models import ClassRoom
from classrooms.forms import ClassRoomForm
from profile.models import Profile

class StudentInline(admin.TabularInline):
	model = Profile

	fieldsets = (
		(None, {'fields': ('first_name', 'last_name', 'parents')}),
		)
	readonly_fields = ('first_name', 'last_name', 'parents')

class LeerkrachtInline(admin.TabularInline):
	model = Profile.klasleerkracht.through

class KlasOuderInline(admin.TabularInline):
	model = Profile.klas_ouder.through

class ClassroomAdmin(admin.ModelAdmin):
	#form = ClassRoomForm
	inlines = [LeerkrachtInline, KlasOuderInline, StudentInline]
	#prepopulated_fields = {"slug": ("klasnaam",)}
	fieldsets = (
		(None, {'fields' : ('klascode', 'klasnaam', )}),
		)
	#readonly_fields = ("slug",)


admin.site.register(ClassRoom, ClassroomAdmin)