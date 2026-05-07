from django.shortcuts import render
from decimal import Decimal

from .models import Produit
from achats.models import LigneBonReception, LigneAvoirFournisseur
from ventes.models import LigneBonLivraison, LigneAvoirClient


def liste_stock(request):

    produits = Produit.objects.all()
    data = []

    for p in produits:

        date_ref = p.date_creation

        # =========================
        # ACHATS
        # =========================
        achats = LigneBonReception.objects.filter(
            produit=p,
            bon_reception__date__gte=date_ref
        )

        # =========================
        # VENTES
        # =========================
        ventes = LigneBonLivraison.objects.filter(
            produit=p,
            bon_livraison__date__gte=date_ref
        )

        # =========================
        # AVOIRS CLIENT (retour client → + stock)
        # =========================
        avoirs_clients = LigneAvoirClient.objects.filter(
            produit=p,
            avoir_client__date__gte=date_ref
        )

        # =========================
        # AVOIRS FOURNISSEUR (retour fournisseur → - stock)
        # =========================
        avoirs_fournisseurs = LigneAvoirFournisseur.objects.filter(
            produit=p,
            avoir_fournisseur__date__gte=date_ref
        )

        # =========================
        # TOTAUX
        # =========================
        total_achats = sum(Decimal(l.quantite or 0) for l in achats)
        total_ventes = sum(Decimal(l.quantite or 0) for l in ventes)
        total_avoir_client = sum(Decimal(l.quantite or 0) for l in avoirs_clients)
        total_avoir_fournisseur = sum(Decimal(l.quantite or 0) for l in avoirs_fournisseurs)

        # =========================
        # STOCK REEL
        # =========================
        stock_reel = (
            Decimal(p.stock_initial or 0)
            + total_achats
            - total_ventes
            + total_avoir_client
            - total_avoir_fournisseur
        )

        data.append({
            "produit": p,
            "stock_initial": p.stock_initial,
            "achats": total_achats,
            "ventes": total_ventes,
            "avoir_client": total_avoir_client,
            "avoir_fournisseur": total_avoir_fournisseur,
            "stock_reel": stock_reel,
            "date_ref": date_ref
        })

    return render(request, "produits/liste_stock.html", {"data": data})

from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Sum

from .models import Produit
from achats.models import LigneBonReception, LigneAvoirFournisseur
from ventes.models import LigneBonLivraison, LigneAvoirClient


from django.http import JsonResponse
from django.db.models import Sum
from .models import Produit
from achats.models import LigneBonReception, LigneAvoirFournisseur
from ventes.models import LigneBonLivraison, LigneAvoirClient


def stock_produit(request, produit_id):

    produit = Produit.objects.get(id=produit_id)

    date_ref = produit.date_creation

    # =========================
    # ACHATS
    # =========================
    total_achats = LigneBonReception.objects.filter(
        produit_id=produit_id,
        bon_reception__date__gte=date_ref
    ).aggregate(total=Sum("quantite"))["total"] or 0

    # =========================
    # VENTES
    # =========================
    total_ventes = LigneBonLivraison.objects.filter(
        produit_id=produit_id,
        bon_livraison__date__gte=date_ref
    ).aggregate(total=Sum("quantite"))["total"] or 0

    # =========================
    # AVOIR CLIENT (+ stock)
    # =========================
    total_avoir_client = 0
    try:
        total_avoir_client = LigneAvoirClient.objects.filter(
            produit_id=produit_id,
            avoir_client__date__gte=date_ref   # ⚠️ adapte si nécessaire
        ).aggregate(total=Sum("quantite"))["total"] or 0
    except:
        pass

    # =========================
    # AVOIR FOURNISSEUR (- stock)
    # =========================
    total_avoir_fournisseur = 0
    try:
        total_avoir_fournisseur = LigneAvoirFournisseur.objects.filter(
            produit_id=produit_id,
            avoir_fournisseur__date__gte=date_ref   # ⚠️ adapte si nécessaire
        ).aggregate(total=Sum("quantite"))["total"] or 0
    except:
        pass

    # =========================
    # STOCK FINAL
    # =========================
    stock = (
        produit.stock_initial
        + total_achats
        - total_ventes
        + total_avoir_client
        - total_avoir_fournisseur
    )

    seuil = produit.seuil
    alerte = stock < seuil

    return JsonResponse({
        "stock": round(stock, 3),
        "seuil": seuil,
        "alerte": alerte
    })
