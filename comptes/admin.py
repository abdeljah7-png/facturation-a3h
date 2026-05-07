from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Compte

@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):

    list_display = ("id", "libelle", "releve_compte", "paiements_non_echus")

    def releve_compte(self, obj):
        url = reverse("releve_compte", args=[obj.id])
        return format_html('<a href="{}">Relevé</a>', url)

    def paiements_non_echus(self, obj):
        url = reverse("releve_non_echu", args=[obj.id])
        return format_html('<a href="{}">Non échus</a>', url)

    releve_compte.short_description = "Relevé"
    paiements_non_echus.short_description = "Paiements non échus"