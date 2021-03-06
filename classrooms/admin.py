from django.contrib import admin

from classrooms.models import ClassRoom
from profile.models import Profile

from adminsortable.admin import SortableAdmin

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

class ClassroomAdmin(SortableAdmin):
	#form = ClassRoomForm
	inlines = [LeerkrachtInline, KlasOuderInline, StudentInline]
	list_display = ["klasnaam", "klascode"]
	#prepopulated_fields = {"slug": ("klasnaam",)}
	fieldsets = (
		(None, {'fields' : ('klascode', 'klasnaam', 'slug')}),
		)
	#readonly_fields = ("slug",)


admin.site.register(ClassRoom, ClassroomAdmin)