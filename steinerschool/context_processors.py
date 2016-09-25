from werkgroepen.models import Werkgroep
from classrooms.models import ClassRoom


def schoolapp_context(request):
    """
    A context processor that provides event information.
    :param request: the current HttpRequest object.
    :return: the dictionary to be merged into the context, including the event information.
    """
        
    werkgroepen = None

    werkgroepen = Werkgroep.objects.all()
    klassen = ClassRoom.objects.all()
 
    return {
        'werkgroepen': werkgroepen,
        'klassen': klassen,
    }