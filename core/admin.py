from django.contrib import admin
from .models import Societe


@admin.register(Societe)
class SocieteAdmin(admin.ModelAdmin):

    list_display = (
        "nom",
        "matricule_fiscal",
        "pays",
        "ville",
        "telephone",
    )

    search_fields = (
        "nom",
        "matricule_fiscal",
    )