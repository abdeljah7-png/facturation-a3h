from .utils import get_societe

def societe_context(request):
    return {
        'societe': get_societe()
    }