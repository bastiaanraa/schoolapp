from django.contrib import admin

from .models import SchoolCalendar

class SchoolCalendarAdmin(admin.ModelAdmin):
    list_display = ['titel', 'startdatum', 'einddatum', 'get_doelgroep_display', 'publiek']

    def get_form(self, request, obj=None, **kwargs):
        form = super(SchoolCalendarAdmin, self).get_form(request, obj, **kwargs)
        # increase title textinput field
        form.base_fields['titel'].widget.attrs['style'] = 'width: 47em;'
        return form

admin.site.register(SchoolCalendar, SchoolCalendarAdmin)
