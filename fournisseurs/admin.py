from django.contrib import admin
from .models import Fournisseur
from django.urls import reverse
from django.utils.html import format_html


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):

    def voir_releve(self, obj):
        url = reverse('releve_fournisseur', args=[obj.id])
        return format_html('<a href="{}">📄 Relevé</a>', url)

    voir_releve.short_description = "Relevé"

    list_display = (
        "nom",
        "matricule_fiscal",
        "telephone",
        "email",
        "date_creation",
        'voir_releve',
    )
    search_fields = (
        "nom",
        "matricule_fiscal",
        "telephone",
        "email",
    )
    list_filter = ("date_creation",)
    ordering = ("nom",)
