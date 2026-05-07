from django.contrib import admin
from .models import Client
from django.urls import reverse
from django.utils.html import format_html

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):

    def voir_releve(self, obj):

        
        url = reverse('releve_client', args=[obj.id])
        return format_html('<a class="button" href="{}">📄 Relevé</a>', url)

    voir_releve.short_description = "Relevé"

    list_display = (
        "nom",
        "matricule_fiscal",
        "telephone",
        "date_creation",
        'voir_releve',
    )
    search_fields = (
        "nom",
        "matricule_fiscal",
        "telephone",
        "email",
    )

