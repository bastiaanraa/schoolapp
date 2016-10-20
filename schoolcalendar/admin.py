from django.contrib import admin

from .models import SchoolCalendar

class SchoolCalendarAdmin(admin.ModelAdmin):
	list_display = ['titel', 'startdatum', 'einddatum', 'get_doelgroep_display', 'publiek']

admin.site.register(SchoolCalendar, SchoolCalendarAdmin)
