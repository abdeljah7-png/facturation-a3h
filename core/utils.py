from .models import Societe

def get_societe():
    return Societe.objects.first()