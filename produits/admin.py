from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html
from .models import Produit
from django.db.models import Sum
from achats.models import LigneBonReception, LigneAvoirFournisseur
from ventes.models import LigneBonLivraison, LigneAvoirClient
from decimal import Decimal



@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):

    list_display = (
        "reference",
        "designation",
        "prix_ht",
        "taux_tva",
        "stock_initial",
        "stock_reel"
    )

    search_fields = (
        "designation",
        "reference",
    )


    def stock_reel(self, obj):

        date_ref = obj.date_creation

        # ACHATS
        total_achats = LigneBonReception.objects.filter(
            produit=obj,
            bon_reception__date__gte=date_ref
        ).aggregate(total=Sum('quantite'))['total'] or 0

        # VENTES
        total_ventes = LigneBonLivraison.objects.filter(
            produit=obj,
            bon_livraison__date__gte=date_ref
        ).aggregate(total=Sum('quantite'))['total'] or 0

        # =========================
        # AVOIR CLIENT (SAFE)
        # =========================
        total_avoir_client = 0
        try:
            total_avoir_client = LigneAvoirClient.objects.filter(
                produit=obj,
                avoir_client__date__gte=date_ref   # ⚠️ adapte ici si besoin
            ).aggregate(total=Sum('quantite'))['total'] or 0
        except:
            pass

        # =========================
        # AVOIR FOURNISSEUR (SAFE)
        # =========================
        total_avoir_fournisseur = 0
        try:
            total_avoir_fournisseur = LigneAvoirFournisseur.objects.filter(
                produit=obj,
                avoir_fournisseur__date__gte=date_ref   # ⚠️ adapte ici
            ).aggregate(total=Sum('quantite'))['total'] or 0
        except:
            pass

        return round((
            obj.stock_initial
            + total_achats
            - total_ventes
            + total_avoir_client
            - total_avoir_fournisseur
        ) ,3)

    stock_reel.short_description = "Stock réel"


    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}
        extra_context['stock_url'] = reverse('liste_stock')

        return super().changelist_view(request, extra_context=extra_context)