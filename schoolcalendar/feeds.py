from django_ical.views import ICalFeed
from .models import SchoolCalendar

class EventFeed(ICalFeed):
    """
    A simple event calender
    """
    product_id = '-//Steinerschool Gent//Kalender//NL'
    timezone = 'UTC+01:00'
    file_name = "event.ics"

    def items(self):
        return SchoolCalendar.objects.all().order_by('-startdatum')

    def item_title(self, item):
        return item.titel

    def item_description(self, item):
        return item.tekst

    def item_start_datetime(self, item):
        return item.startdatum