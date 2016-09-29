from werkgroepen.models import Werkgroep
from classrooms.models import ClassRoom
from bestuur.models import Bestuur


def schoolapp_context(request):
    """
    A context processor that provides event information.
    :param request: the current HttpRequest object.
    :return: the dictionary to be merged into the context, including the event information.
    """
        
    werkgroepen = None

    werkgroepen = Werkgroep.objects.all()
    klassen = ClassRoom.objects.all()
    besturen = Bestuur.objects.all()
    mijn_klassen = []
    try:
        for child in request.user.parents.all():
            mijn_klassen.append(child.klas)
    except Exception, e:
        pass
    
 
    return {
        'werkgroepen': werkgroepen,
        'klassen': klassen,
        'besturen': besturen,
        'mijn_klassen': mijn_klassen,
    }
