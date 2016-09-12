from django.contrib import admin

from classrooms.models import ClassRoom
from profile.models import Profile

class StudentInline(admin.TabularInline):
	model = Profile

	fieldsets = (
		(None, {'fields': ('first_name', 'last_name', 'parents')}),
		)
	readonly_fields = ('first_name', 'last_name', 'parents')


class ClassroomAdmin(admin.ModelAdmin):
	inlines = [StudentInline]
	prepopulated_fields = {"slug": ("klasnaam",)}
	#readonly_fields = ("slug",)


admin.site.register(ClassRoom, ClassroomAdmin)